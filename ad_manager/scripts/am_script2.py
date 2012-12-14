import pprint
# pprint.pprint(dir(obj))
# pprint.pprint(list)

# $ python manage.py runscript am_script2

class BaseMixin(object):
    
    #----------------------------------
    # Init:
    #----------------------------------
    
    def __init__(self):
        
        # Default value:
        self._x = None
    
    #----------------------------------
    # Accessors:
    #----------------------------------
    
    @property
    def x(self):
        
        "I'm the 'x' property."
        
        # Return the value of x:
        return self._x
    
    @x.setter
    def x(self, value):
        
        # Set the value of x:
        self._x = value
    
    @x.deleter
    def x(self):
        
        # Delete the value of x:
        del self._x

class Foo(BaseMixin):
    
    # What to do here?
    pass

def run():
    
    # Instanciate:
    f = Foo()
    
    # Set:
    f.x = 'Dogs!'
    
    # Interrogate:
    pprint.pprint(dir(f))
    pprint.pprint(dir(f.x))
    
    # Get:
    print f.x
    
    # Delete:
    del(f.x)
    
    #print f.x # AttributeError: 'Foo' object has no attribute '_x'
