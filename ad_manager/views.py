import datetime

from django import http
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import BaseDetailView

from ad_manager.mixins.views import JSONResponseMixin
from ad_manager.models import AdGroup, PageType, Target
from ad_manager.utils import bad_or_missing # Seems a tad better than get_object_or_404 from from django.shortcuts.

# http://stackoverflow.com/questions/13180876/how-do-i-render-a-cached-jsonp-view-in-django
# http://stackoverflow.com/questions/5940856/python-using-args-kwargs-in-wrapper-functions
# https://github.com/mhulse/django-purr
# http://strftime.org/
# https://gist.github.com/4279705

"""
Renders JSON or JSONP to the view.

Example usage:

urlpatterns = patterns('',
    url(r'^(?P<hierarchy>[-\w:]+)/?(?P<page>[-\w]+)?/$', Api.as_view(), name='ad_manager_target_api',),
)
"""

class Api(JSONResponseMixin, BaseDetailView):
    
    # Override `BaseDetailView`'s `get()` method:
    def get(self, request, *args, **kwargs):
        
        """
        Handler for GET requests.
        
        This retrieves the object from the database and calls the
        `render_to_response` with the retrieved object in the `context` data.
        
        Returns:
        Ouput of `render_to_response` method implementation.
        """
        
        #----------------------------------
        # Setup:
        #----------------------------------
        
        # Get `hierarchy` `kwarg` from url:
        hierarchy = self.kwargs['hierarchy'].strip('/') # Example: foo:baz:bar:bing
        
        # Get `page`:
        page = kwargs.get('page', None)
        
        # Create/set the `cache_key`:
        self.cache_key = 'ad_manager_api_%s%s%s' % (hierarchy,  (':' if page else ''), page)
        
        # Cached JSON?
        data_cached = cache.get(self.cache_key)
        
        # Check if JSON is cached OR if we want to force-update the cache:
        if (data_cached is None) or (request.GET.get('cache') == 'busted'):
            
            #----------------------------------
            # Check and get targets:
            #----------------------------------
            
            # Clean up slashes and convert to a list:
            target_slugs = hierarchy.split(':')
            
            # Initialize `targets` list:
            targets = []
            
            # Pull `slug`s from list: 
            for slug in target_slugs:
                
                # Check for `parent`:
                if not targets:
                    
                     # There's no `parent`:
                    parent = None
                    
                else:
                    
                    # Set `parent` to the next `target` object:
                    parent = targets[-1]
                
                # Play it safe:
                try:
                    
                    # Get the `target` object:
                    target = Target.objects.get(slug__iexact=slug, parent=parent,)
                    
                # Can we continue?
                except Target.DoesNotExist:
                    
                    # Bad or missing `Target` request:
                    return bad_or_missing(request, _(u'The target you have requested does not exist.'))
                
                # Append the `target` object to the `target` list:
                targets.append(target)
            
            # Get the last `target`:
            target = targets[-1]
            
            #----------------------------------
            # Get ad groups:
            #----------------------------------
            
            # Filter `AdGroup` based on `target`:
            ad_groups = AdGroup.objects.filter(target=target)
                
            # Can we continue?
            if not ad_groups:
                
                # Bad or missing `AdGroup` request:
                return bad_or_missing(request, _(u'The ad group you have requested does not exist.'))
            
            #----------------------------------
            # Get page type:
            #----------------------------------
            
            # If `page` was included in the URI:
            if page:
                
                # Play it safe:
                try:
                    
                    # Filter `PageType` based on `page` slug:
                    page_type = PageType.objects.get(slug__iexact=page,)
                    
                # Can we continue?
                except PageType.DoesNotExist:
                    
                    # Bad or missing `PageType` request:
                    return bad_or_missing(request, _(u'The page type you have requested does not exist.'))
                
                # Filter `AdGroup` queryset based on `page_type` object: 
                ad_groups = ad_groups.filter(page_type=page_type)
                    
                # Can we continue?
                if not ad_groups:
                    
                    # Bad or missing `AdGroup`s request:
                    return bad_or_missing(request, _(u'The ad group and page type you have requested do not exist.'))
            
            #----------------------------------
            # Loops:
            #----------------------------------
            
            # Build data dict:
            data = {
                
                # Boilerplate:
                'now': str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M")), # For debug/cache purposes.
                
                # Showtime:
                'target': [
                    {
                        'name': target.name,
                        'slug': slugify(target.name),
                        'ad_group': [
                            {
                                'aug_id': ad_group.aug_id,
                                'page_type': getattr(ad_group.page_type, 'name', ''),
                                'ad': [
                                    {
                                        'id': ad.ad_id,
                                        'ad_type': [
                                            {
                                                'name': ad.ad_type.name,
                                                'slug': slugify(ad.ad_type.name),
                                                'width': ad.ad_type.width,
                                                'height': ad.ad_type.height,
                                                'tag_type': ad.ad_type.tag_type.name,
                                            }
                                        ],
                                    } for ad in ad_group.ad.active()
                                ],
                            } for ad_group in ad_groups
                        ],
                    }
                ],
                
            }
            
            #----------------------------------
            # Returns:
            #----------------------------------
            
            # JSON isn't cached OR we want to force-update: 
            return self.render_to_response(data) # Render to `JSONResponseMixin.render_to_response()`.
            
        else:
            
            # We're already cached; update `cache_exists` property:
            self.cache_exists = True
            
            # JSON is cached and we don't want to force-update:
            return self.render_to_response(data_cached)
