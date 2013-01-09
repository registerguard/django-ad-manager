import datetime
from django.db.models import Q
from django.db import models

class AdManager(models.Manager):
    
    def active(self):
        
        "Retrieves all active ads which have been published and have not yet expired."
        
        today = datetime.date.today()
        
        return self.get_query_set().filter(Q(expiration_date__isnull=True) | Q(expiration_date__gte=today), publish_date__lte=today, is_active=True,)

class TargetManager(models.Manager):
    
    def root_targets(self, **kwargs):
        
        "Get all root targets."
        
        return self.filter(parent__isnull=True, **kwargs)
