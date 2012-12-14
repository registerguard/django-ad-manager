import pprint
import pdb

# http://stackoverflow.com/a/712799/922323
try: import simplejson as json
except ImportError: import json

from ad_manager.models import Ad as a
from ad_manager.models import Target as t

# http://blog.brendel.com/2012/01/how-to-use-djangextensions-runscript.html
# http://blog.leahculver.com/2008/08/python-dir-is-my-fav-debugging-thing-ever.html

# $ python manage.py runscript am_script2

def run():
    
    #pdb.set_trace()
    
    #parent = self.kwargs['parent']
    parent = 'sports'
    #child = self.kwargs['child']
    child = 'football'
    #page = self.kwargs['page']
    page = 'section'
    
    #pprint.pprint(dir(a))
    
    targets = t.objects.filter(parent__slug__iexact=parent, slug__iexact=child,)
    
    #print targets # [<Target: SPORTS | Football>]
    
    data = [
        {
            'target': [
                {
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
                                } for ad in ad_group.ad.all()
                            ],
                        } for ad_group in target.ad_group.filter(page_type__slug__iexact=page,)
                    ],
                }
            ],
        } for target in targets
    ]
    
    """
    data = {
        'comment': 'foo',
        'blah': ad_group_chunk,
    }
    """
    
    print json.dumps(data, indent=4)
    
    """
    pprint.pprint(target)
    
    ads = a.objects.filter(ad_group__target__slug__iexact=child, ad_group__target__parent__slug__iexact=parent, ad_group__page_type__slug__iexact=page,)
    
    ads_chunk = [
        {
            'aug_id': ad.ad_group.aug_id,
            'ad_id': ad.ad_id,
            'ad_name': ad.ad_type.name,
        } for ad in ads
    ]
    
    data = {
        'comment': 'foo',
        'blah': ads_chunk,
    }
    
    print json.dumps(data, indent=4)
    """