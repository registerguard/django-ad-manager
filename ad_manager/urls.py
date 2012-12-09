from django.conf.urls.defaults import *

from ad_manager.views import Api

# https://bitbucket.org/chris1610/satchmo/src/1730bf912bc1/satchmo/apps/product/urls/category.py?at=default
# http://stackoverflow.com/a/9492349/922323

urlpatterns = patterns('',
    
    # "/grand-parent:parent:child/page-type" OR "/parent:child/page-type" OR "/child/page-type" OR "/child"
    
    url(
        r'^(?P<hierarchy>[-\w:]+)/?(?P<page>[-\w]+)?/$',
        Api.as_view(),
        name='ad_manager_target_api',
    ),
    
)