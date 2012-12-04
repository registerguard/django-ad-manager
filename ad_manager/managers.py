import datetime
from django.db.models import Q
from django.db import models

class AdStatusManager(models.Manager):
    
    def default(self):
        
        default = self.all()[:1]
        if len(default) == 0:
            return None
        else:
            return default[0]

class AdManager(models.Manager):
    
    def active(self):
        
        """
        Retrieves all active articles which have been published and have not yet expired.
        """
        
        now = datetime.datetime.now()
        return self.get_query_set().filter(Q(expiration_date__isnull=True) | Q(expiration_date__gte=now), publish_date__lte=now, is_active=True,)
    
    def live(self, user=None):
        
        """
        Retrieves all live articles.
        """
        
        qs = self.active()
        if user is not None and user.is_superuser:
            # superusers get to see all articles:
            return qs
        else:
            # only show live articles to regular users:
            return qs.filter(status__is_live=True,)