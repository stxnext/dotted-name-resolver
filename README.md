This code is stolen from pyramid.path 
(https://github.com/Pylons/pyramid/blob/master/pyramid/path.py).

You can use this code to resolve ``dotted Python name`` to a global python 
object. ``Dotted Python name`` is a reference to a Python object by name 
using a string, in the form path.to.modulename:attributename or
path.to.modulename.attributename.
