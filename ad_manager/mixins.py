try: import simplejson as json
except ImportError: import json

from django import http
from django.core.cache import cache

# http://stackoverflow.com/a/712799/922323
# https://docs.djangoproject.com/en/1.3/topics/class-based-views/#more-than-just-html
# https://groups.google.com/d/topic/django-users/mJyzQhEL-eE/discussion

# How to make these `JSONResponseMixin` properties?
# Doing so would make the class more flexible.
CACHE_TIMEOUT = 86400 # 24 hours.
CACHE_NAME = 'ad_manager_api'

"""
A simple JSON mixin.

Example usage:

class Api(JSONResponseMixin, BaseDetailView):
    pass
"""

class JSONResponseMixin(object):
    
    def render_to_response(self, context=None, is_cache=False):
        
        """
        Returns a JSON response containing 'context' as payload.
        
        Note: Because of how `render_to_response` is implemented, the only way
        to specify `is_cache` (for example) is by using a named argument.
        Anything passed as a positional arguments (`kwargs`) will be passed on
        to `loader.render_to_string`.
        """
        
        if is_cache:
            
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
        
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        
        # Serialize `context` to a JSON formatted str:
        jsonstring = json.dumps(context, sort_keys=True, indent=4, separators=(',', ': '))
        
        # Set the cache:
        cache.set(CACHE_NAME, jsonstring, CACHE_TIMEOUT)
        
        # Return the serialized JSON string:
        return jsonstring