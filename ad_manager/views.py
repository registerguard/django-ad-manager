# http://stackoverflow.com/a/712799/922323
try: import simplejson as json
except ImportError: import json

from django import http
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.views.generic.detail import BaseDetailView

from ad_manager.models import AdGroup, PageType, Target

# https://docs.djangoproject.com/en/1.3/topics/class-based-views/#more-than-just-html
class JSONResponseMixin(object):
    
    def render_to_response(self, context):
        
        "Returns a JSON response containing 'context' as payload."
        
        return self.get_json_response(self.convert_context_to_json(context))
    
    def get_json_response(self, content, **httpresponse_kwargs):
        
        "Construct an `HttpResponse` object."
        
        callback = self.request.GET.get('callback')
        
        if callback:
            
            json = '%s(%s)' % (callback, content)
            
        else:
            
            json = '{' + content + '}'
        
        return http.HttpResponse(json, content_type='application/json', **httpresponse_kwargs)
    
    def convert_context_to_json(self, context):
        
        "Convert the context dictionary into a JSON object."
        
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        
        return json.dumps(context, indent=4)

class Api(JSONResponseMixin, BaseDetailView):
    
    def get(self, request, *args, **kwargs):
        
        hierarchy = self.kwargs['hierarchy']
        
        page = kwargs.get('page', None)
        
        target_slugs = hierarchy.strip('/').split(':')
        
        targets = []
        
        for slug in target_slugs:
            
            if not targets:
                
                parent = None
                
            else:
                
                parent = targets[-1]
            
            target = get_object_or_404(Target, slug__iexact=slug, parent=parent,)
            
            targets.append(target)
        
        target = targets[-1]
        
        ad_groups = AdGroup.objects.filter(target=target)
        
        if not ad_groups:
            
            raise http.Http404
        
        if page:
            
            page_type = get_object_or_404(PageType, slug__iexact=page)
            
            ad_groups = ad_groups.filter(page_type=page_type)
        
        data = [
            {
                'target': [
                    {
                        'callback': request.GET.get('callback'),
                        'name': target.name,
                        'ad_group': [
                            {
                                'aug_id': ad_group.aug_id,
                                'page_type': [
                                    {
                                        'name': ad_group.page_type.name,
                                    }
                                ],
                                'ad': [
                                    {
                                        'id': ad.ad_id,
                                        'ad_type': [
                                            {
                                                'name': ad.ad_type.name,
                                                'width': ad.ad_type.width,
                                                'height': ad.ad_type.height,
                                                'tag_type': [
                                                    {
                                                        'name': ad.ad_type.tag_type.name,
                                                    }
                                                ],
                                            }
                                        ],
                                    } for ad in ad_group.ad.active()
                                ],
                            } for ad_group in ad_groups
                        ],
                    }
                ]
            }
        ]
        
        return self.render_to_response(data)
