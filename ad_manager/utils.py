from django import http
from django.template import loader
from django.template import RequestContext

# https://bitbucket.org/chris1610/satchmo/src/7e5842d3c520/satchmo/apps/satchmo_store/shop/templates/404.html?at=default

def bad_or_missing(request, msg):
    
    """
    Return an HTTP 404 response for a date request that cannot possibly exist.
    The 'msg' parameter gives the message for the main panel on the page.
    """
    
    if request.is_ajax():
        
        resp = http.HttpResponse()
        
        resp.status_code = 404
        
        resp.content = {
            'message': msg
        }
        
        return resp
        
    else:
        
        template = loader.get_template('ad_manager/404.html')
        
        context = RequestContext(request, {
            'message': msg,
        })
        
        return http.HttpResponseNotFound(template.render(context))