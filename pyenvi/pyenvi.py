import subprocess
import json
import shlex
import os
import atexit

from .exceptions import *

def cleanup():
    """
    The cleanup function, executed on program close.
    """
    if PyEnvi.get_instance().is_running() == True:
        PyEnvi.get_instance().subp.kill()
        PyEnvi.get_instance().subp = None

class PyEnvi(object):
    """
    PyEnvi: environment variable simulator to multi process python applications.
    """
    
    _instance = None
    def get_instance():
        """
        Get the singleton instance of PyEnvi.  Creates a new instance if it doesn't exist.
        """
        
        if PyEnvi._instance == None:
            PyEnvi._instance = PyEnvi()
        return PyEnvi._instance
    
    def __init__(self,environment_variables={}):
        """
        Constructor.  Params: dictionary of environment variables.
        Sets singleton instance.  Note that if called twice, will 
        raise exception.
        """
        if PyEnvi._instance == None:
           PyEnvi._instance = self
           self.environment_variables = environment_variables #for printing purposes
           self.subp = None
        else:
           raise MultipleInstanceError("Cannot have 2 instances")

    def __str__(self):
        """
        Returns a string of the currently set environment variables
        """
        return "PyEnvi: " + str(self.environment_variables)
    
    def is_running(self):
        """
        Returns True if PyEnvi is running, False if it isn't.
        """
        if self.subp == None:
            return False
        else:
            return True
    
    def start(self):
        """
        Starts PyEnvi so that environment variables can be set and get.  Raises an exception
        if already started.  Registers shutdown code on atexit.
        """
        
        if self.is_running():
            raise AlreadyRunningError("Pyenvi is already running")
        else:
            environment_vars_string = shlex.quote(json.dumps(self.environment_variables))
            self.subp = subprocess.Popen(["python",os.path.join(os.path.dirname(__file__),"pyenvi_run.py"),environment_vars_string],stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True) 
        
        atexit.register(cleanup)
    
    def stop(self):
        """
        Stops PyEnvi, closes subprocess.  Returns "OK" on success, error message on fail.
        """
        if not self.is_running():
            raise NotRunningError("PyEnvi is not running")
        else:
            message = self.create_message("STOP",{})
            response = self.send_message(message)
            
            if response != "OK":
                self.subp.kill()
            
            self.subp = None
            return response
                
                
    def set(self,key, value):
        """
        Sets a variable.  Params:  string key and value, representing a environment variable.
        PyEnvi must be running, or an exception is raised.
        """
        if not self.is_running():
            raise NotRunningError("PyEnvi is not running")
        else:
            self.environment_variables[str(key)] = str(value)
            message = self.create_message("SET",{"key":str(key),"value":str(value)})
            response = self.send_message(message)
        
            return response
                
    def get(self,key):
        """
        Gets the value of a variable.  Params: a string key for the variable wanted.
        PyEnvi must be running, or an exception is raised.
        If the variable is not set, an exception is raised.
        """
        if not self.is_running():
            raise NotRunningError("PyEnvi is not running")
        else:
            message = self.create_message("GET",{"key":key})
            response = self.send_message(message)
        
            if response != "_NOT_SET":  #TODO: find some way around this
                return response
            else:
                raise NotSetError("Key " + key + " not set.")
                
    def exists(self,key):
        """
        Returns true if a variable is set, false if it isn't. Params:  key to be queried.
        PyEnvi must be running, or an exception is raised.
        """
        if not self.is_running():
            raise NotRunningError("PyEnvi is not running")
        else:
            message = self.create_message("EXISTS",{"key":key})
            response = self.send_message(message)
            
            if response == "YES":
                return True
            else:
                return False
        
    def parse_response(self,response):
        """
        Converts a byte response into a string, returns said string.  Params: bytes from response.
        """
        return response.rstrip().lstrip().decode("utf-8")
    
    def create_message(self, action,data):
        """
        Create a message.  Params:  Action for subprocess to process, and data sent.
        """
        message = json.dumps({
                                "action": action,
                                "data":data
        })
        message += "\n"
        return bytes(message,"UTF-8")
    
    def send_message(self,message):
        """
        Send a message to the subprocess, and return the response it gives.  Params: message generated by create_message
        """
        self.subp.stdin.write(message)
        self.subp.stdin.flush()
        
        response = self.parse_response(self.subp.stdout.readline())
        return response

        
if __name__ == "__main__":
    pass #test code can go here
    

    
