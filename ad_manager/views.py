from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from ad_manager.models import Target
from ad_manager.utils import bad_or_missing

# https://bitbucket.org/chris1610/satchmo/src/1730bf912bc1/satchmo/apps/product/views/__init__.py?at=default

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