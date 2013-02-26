try: import simplejson as json
except ImportError: import json

from django import http
from django.core.cache import cache

# http://stackoverflow.com/a/712799/922323
# https://docs.djangoproject.com/en/1.3/topics/class-based-views/#more-than-just-html
# https://groups.google.com/d/topic/django-users/mJyzQhEL-eE/discussion

"""
A simple JSON mixin.

Example usage:

class Api(JSONResponseMixin, BaseDetailView):
    pass
"""

class JSONResponseMixin(object):
    
    #----------------------------------
    # Properties:
    #----------------------------------
    
    # Loading from the cache?
    cache_exists = False
    
    # How long to cache?
    cache_timeout = 43200 # 12 hours.
    
    # Unique cache key string:
    cache_key = None
    
    # If `True`, then output of dictionaries will be sorted by key:
    json_sort_keys = True # Default: False
    
    # JSON array elements and object members will be pretty-printed at this indent level:
    json_indent = 4 # Default: None
    
    # Control trailing whitespace when indent is specified:
    json_separators = (',', ': ') # Default: (', ', ': ')
    
    #----------------------------------
    # Methods:
    #----------------------------------
    
    def render_to_response(self, context=None):
        
        "Returns a JSON response containing 'context' as payload."
        
        if self.cache_exists:
            
            # Reading from cache so skip context's conversion to JSON:
            return self.get_json_response(context)
            
        else:
            
            # No cache so convert the context to JSON:
            return self.get_json_response(self.convert_context_to_json(context))
    
    def get_json_response(self, content, **httpresponse_kwargs):
        
        "Construct an `HttpResponse` object."
        
        # Get `callback` from URI:
        callback = self.request.GET.get('callback')
        
        if callback:
            
            # JSONP content type:
            content_type = 'application/javascript; charset=utf-8'
            
            # The `callback` exists, format content as JSONP:
            json = '%s(%s);' % (callback, content)
            
        else:
            
            # JSON content type:
            content_type = 'application/json; charset=utf-8'
            
            # No callback; regular JSON:
            json = content
        
        # Render outgoing HTTP response:
        return http.HttpResponse(json, content_type=content_type, **httpresponse_kwargs)
    
    def convert_context_to_json(self, context):
        
        "Convert the `context` dictionary into a JSON object."
        
        # Playing it safe:
        try:
            
            # Serialize `context` to a JSON formatted string:
            json_string = json.dumps(context, sort_keys=self.json_sort_keys, indent=self.json_indent, separators=self.json_separators)
            
        # Doh!
        except TypeError:
            
            # Convert `context` to a string and dump it:
            json.dumps(str(context))
        
        # Has the `cache_key` property been set?
        if self.cache_key:
            
            # Set the `cache`:
            cache.set(self.cache_key, json_string, self.cache_timeout)
        
        # Return the serialized JSON string:
        return json_string