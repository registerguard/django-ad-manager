from django.conf.urls.defaults import *

# https://bitbucket.org/chris1610/satchmo/src/1730bf912bc1/satchmo/apps/product/urls/category.py?at=default

urlpatterns = patterns('ad_manager.views',
    
    (r'^(?P<parent_slugs>([-\w]+/)*)?(?P<slug>[-\w]+)/$', 'target_detail', {}, 'ad_manager_target_detail'),
    (r'^$', 'target_list', {}, 'ad_manager_target_list'),
    
)