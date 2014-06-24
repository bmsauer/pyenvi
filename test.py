import json

import unittest
from unittest.mock import MagicMock
from pyenvi import PyEnvi
from pyenvi.exceptions import *

class PyEnviTest(unittest.TestCase):
    """
    PyEnviTest: a test class for PyEnvi.
    TODO: These tests are a little sketchy, due to the static nature of PyEnvi.
    Furthermore, they do not test any expected values from the subprocess, which
    should be added.
    """
    
    def setUp(self):
        PyEnvi.get_instance()
            
    def tearDown(self):
        try:
            pyenvi.stop()
        except Exception:
            pass
        
        if PyEnvi.get_instance().subp!=None:
            PyEnvi.get_instance().subp.kill()
            PyEnvi.get_instance().subp = None
        PyEnvi._instance = None
            
    def test_get_instance(self):
        """
        PyEnvi.get_instance() test plan:
            -Make sure a call to get_instance is not none
            -Make sure second call equals first call
            -If starts at none, should be not none
        """
        first_instance = PyEnvi.get_instance()
        self.assertNotEqual(first_instance,None)
        second_instance = PyEnvi.get_instance()
        self.assertEqual(first_instance,second_instance)
        
        
    def test_constructor(self):
        """
        PyEnvi.__init__() test plan:
            -Make sure variables are all set
            -make sure constructor sets _instance to itself
            -make sure subp is none
            -make sure exception raised if called twice
        """
        pyenvi = PyEnvi.get_instance()
        self.assertEqual(pyenvi.subp,None)
        pyenvi.start()
        self.assertNotEqual(pyenvi._instance,None)
        self.assertEqual(pyenvi,pyenvi._instance)
        self.assertRaises(MultipleInstanceError, PyEnvi.__init__,{})
    
    def test_str(self):
        """
        PyEnvi.__str__() test plan:
            -ensure a string is returned with the environment variables.
        """
        pyenvi = PyEnvi.get_instance()
        pyenvi.start()
        pyenvi.set("test","value")
        self.assertEqual(str(pyenvi),"PyEnvi: " + str(pyenvi.environment_variables))
        
    def test_is_running(self):
        """
        PyEnvi.is_running() test plan:
            -set subp to different things, make sure return value is right
        """
        pyenvi = PyEnvi.get_instance()
        self.assertEqual(pyenvi.is_running(),False)
        pyenvi.start()
        self.assertEqual(pyenvi.is_running(),True)
        
    def test_start(self):
        """
        PyEnvi.start() test plan:
            -make sure subp is a subprocess once stared
            -make sure on second call exception is raised
        """
        pyenvi = PyEnvi.get_instance()
        pyenvi.start()
        self.assertEqual(str(type(pyenvi.subp)),"<class 'subprocess.Popen'>")
        self.assertRaises(AlreadyRunningError,pyenvi.start)
    
    def test_stop(self):
        """
        PyEnvi.stop() test plan:
            -raise exception if not running
            -mock send_message, return ok, 
            -ensure subp set to none
            -ensure return value matches mock
        """
        def mock_send_message(message):
            return "Mock value"
            
        pyenvi = PyEnvi.get_instance()
        self.assertRaises(NotRunningError,pyenvi.stop)
        pyenvi.start()
        pyenvi.send_message = mock_send_message
        response = pyenvi.stop()
        self.assertEqual(pyenvi.subp,None)
        self.assertEqual(response,"Mock value")
    
    def test_set(self):
        """
        PyEnvi.set() test plan:
            -if not running, exception should be raised
            -mock send_message, make sure returned.
        """
        def mock_send_message(message):
            return "Mock value"
        pyenvi = PyEnvi.get_instance()
        self.assertRaises(NotRunningError,pyenvi.set,"one","two")
        pyenvi.send_message = mock_send_message
        pyenvi.start()
        response = pyenvi.set("one","two")
        self.assertEqual(response,"Mock value")
        
    def test_get(self):
        """
        PyeEvi.get() test plan:
            -if not running, exception should be raised
            -mock response to return "_NOT_SET" or "OK"
            -on NOT_SET, should raise not set error
            -one set, should return "OK"
        """
        def mock_send_message(message):
            return "Mock value"
        def mock_send_message_not_set(message):
            return "_NOT_SET"
        pyenvi = PyEnvi.get_instance()
        self.assertRaises(NotRunningError,pyenvi.get,"one")
        pyenvi.send_message = mock_send_message_not_set
        pyenvi.start()
        self.assertRaises(NotSetError,pyenvi.get,"one")
        pyenvi.send_message = mock_send_message
        self.assertEqual(pyenvi.get("one"),"Mock value")
        
     
    def test_exists(self):
        """
        PyEnvi.exists() test plan:
           -if not running, raise exception
           -mock send message to return yes and no, return value should reflect that
        """
        def mock_send_message_no(message):
           return "NO"
        def mock_send_message_yes(message):
           return "YES"
        pyenvi = PyEnvi.get_instance()
        self.assertRaises(NotRunningError,pyenvi.exists,"one")
        pyenvi.start()
        pyenvi.send_message = mock_send_message_no
        self.assertEqual(pyenvi.exists("one"),False)
        pyenvi.send_message = mock_send_message_yes
        self.assertEqual(pyenvi.exists("one"),True)
        

    def test_parse_response(self):
        """
        PyEnvi.parse_response() test plan:
            -equivalence table:
            
            type    left padding    right padding   result
            bytes   0               0               string
            object  0               0               attribute error
            bytes   1               0               string
            bytes   0               1               string
            bytes   1               1               string  
        """
        pyenvi = PyEnvi.get_instance()
        response = bytes("this is a response","UTF-8")
        self.assertEqual(pyenvi.parse_response(response),"this is a response")
        response = 4
        self.assertRaises(AttributeError,pyenvi.parse_response,response)
        response = bytes(" this is a response","UTF-8")
        self.assertEqual(pyenvi.parse_response(response),"this is a response")
        response = bytes("this is a response ","UTF-8")
        self.assertEqual(pyenvi.parse_response(response),"this is a response")
        response = bytes(" this is a response \n","UTF-8")
        self.assertEqual(pyenvi.parse_response(response),"this is a response")

    def test_create_message(self):
        """
        PyEnvi.create_message() test plan:
            -make sure return value is bytes
            -make sure that last character is \n
            -make sure json has proper structure
        """
        pyenvi = PyEnvi.get_instance()
        value = pyenvi.create_message("actionname","datathing")
        self.assertEqual(str(type(value)),"<class 'bytes'>")
        value = value.decode("utf-8")
        self.assertEqual(value[-1],"\n")
        value = json.loads(value)
        self.assertEqual(value["action"],"actionname")
        self.assertEqual(value["data"],"datathing")
        
    def test_send_message(self):
        """
        PyEnvi.send_message() test plan:
            -send bogus message to subp, get unknown action
        """
        def mock_parse_response():
            return "value"
        pyenvi = PyEnvi.get_instance()
        pyenvi.start()
        response = pyenvi.send_message(pyenvi.create_message("actionname","datathing"))
        self.assertEqual(response,"_UNKNOWN_ACTION")
        
        
        
if __name__ == "__main__":
    unittest.main()

    
