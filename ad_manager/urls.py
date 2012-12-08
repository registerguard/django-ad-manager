from django.conf.urls.defaults import *

from ad_manager.views import *

# https://bitbucket.org/chris1610/satchmo/src/1730bf912bc1/satchmo/apps/product/urls/category.py?at=default
# http://stackoverflow.com/a/9492349/922323

urlpatterns = patterns('',
    
    #url(r'^/$', 'api',),
    
    # "/grand-parent:parent:child/page-type" OR "/parent:child/page-type" OR "/child/page-type" OR "/child"
    
    url(
        #r'(?P<targets>([-\w]+/)*)?(?P<pagetype>[-\w]+)/$',
        #r'^(?P<targets>[-\w]+)/',
        #r'^(?P<parent>[-\w]+)/(?P<child>[-\w]+)/(?P<page>[-\w]+)?/?$',
        r'^(?P<child>[-\w]+)/(?P<page>"section"|"story")/?$',
        Api.as_view(),
    ),
    
    url(
        r'^(?P<parent>[-\w]+)/(?P<child>[-\w]+)/?$',
        Api.as_view(),
    ),
    
    url(
        r'^(?P<parent>[-\w]+)/(?P<child>[-\w]+)/(?P<page>[-\w]+)?/?$',
        Api.as_view(),
    )
    
    #(r'^(?P<parent_slugs>([-\w]+/)*)?(?P<slug>[-\w]+)/$', 'target_detail', {}, 'ad_manager_target_detail',),
    #(r'^$', 'target_list', {}, 'ad_manager_target_list',),
    
)