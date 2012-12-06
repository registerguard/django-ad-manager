import json

from django import http
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import BaseDetailView

from ad_manager.models import *
from ad_manager.utils import bad_or_missing

# https://bitbucket.org/chris1610/satchmo/src/1730bf912bc1/satchmo/apps/product/views/__init__.py?at=default
# http://www.pioverpi.net/2012/05/14/ajax-json-responses-using-django-class-based-views/
# https://docs.djangoproject.com/en/1.3/topics/class-based-views/#more-than-just-html
# http://stackoverflow.com/a/7676907/922323
# http://stackoverflow.com/a/9492349/922323

def target_list(request, template='ad_manager/target_list.html', root_only=True):
    
    """
    Display all targets.
    Parameters:
    - root_only: If true, then only show root targets.
    """
    
    targets = Target.objects.root_targets()
    
    context = {
        'targetlist' : targets,
    }
    
    return render_to_response(template, context_instance=RequestContext(request, context))

def target_detail(request, slug, parent_slugs='', template='ad_manager/target_detail.html'):
    
    """
    Display the target and its child targets.
    Parameters:
     - slug: slug of target
     - parent_slugs: ignored
    """
    
    try:
        
        target = Target.objects.get(slug=slug)
        
    except Target.DoesNotExist:
        
        return bad_or_missing(request, _(u'The target you have requested does not exist.'))
    
    child_targets = target.get_all_children()
    
    context = {
        'target': target,
        'child_targets': child_targets,
    }
    
    return render_to_response(template, context_instance=RequestContext(request, context))

#--------------------------------------------------------------------------

class JSONResponseMixin(object):
    
    def render_to_response(self, context):
        
        """
        Returns a JSON response containing 'context' as payload
        """
        
        return self.get_json_response(self.convert_context_to_json(context))
    
    def get_json_response(self, content, **httpresponse_kwargs):
        
        """
        Construct an `HttpResponse` object.
        """
        
        return http.HttpResponse(content, content_type='application/json', **httpresponse_kwargs)
    
    def convert_context_to_json(self, context):
        
        """
        Convert the context dictionary into a JSON object
        """
        
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        
        return json.dumps(context)

class Api(JSONResponseMixin, BaseDetailView):
    
    def get(self, request, *args, **kwargs):
        
        # Do some queries here to collect your data for the response:
        
        target_slugs = self.kwargs['targets']
        
        target_slugs_split = target_slugs.split('/')
        
        target_list = []
        
        for slug in target_slugs_split:
            
            if not target_list:
                parent = None
            
            else:
                parent = target_list[-1]
            
            #target = get_object_or_404(Target, slug=slug, parent=parent)
            target = [slug, parent]
        
        context = {
            'target_slugs': target_slugs,
            'target_slugs_split': target_slugs_split,
            'target': target,
        }
        
        return self.render_to_response(context)
