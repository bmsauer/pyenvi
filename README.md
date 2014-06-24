pyenvi
======

Python system environment variable simulator.

By: Brian Sauer

## Overview and purpose:

PyEnvi is a library to give multi process applications an environment variable
like construct.  os.environ[] only works in a single process, and to use true
system level environment variables is sloppy and not cross platform.  PyEnvi is
a pure python library.

##Brief usage:

    from pyenvi.pyenvi import PyEnvi
    
    pyenvi = PyEnvi({"name":"Brian"})           #initialize environment variable "name" to "Brian"
    
    pyenvi.start()                              #must be called to use variables
    
    pyenvi.set("color":"blue")                  #sets new environment variable or updates old one
    
    pyenvi.get("color")                         #returns environment variable
    
    PyEnvi.get_instance()                       #get singleton instance from anywhere in code
    
    PyEnvi.stop()                               #shut down PyEnvi


## Module Description:
See files in docs folder.

##Possible Improvements:
- Support for variables over a network
- Variable persistance from start to stop

##TODO / Open Issues:
- Better tests (see test file)
