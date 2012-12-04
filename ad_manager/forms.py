from django.forms import models, ValidationError
from django.utils.translation import ugettext_lazy as _

class TargetAdminForm(models.ModelForm):
    
    def clean_parent(self):
        
        parent = self.cleaned_data.get('parent', None)
        
        slug = self.cleaned_data.get('slug', None)
        
        if parent and slug:
            
            if parent.slug == slug:
                raise ValidationError(_(u'You may not save a target in itself!'))
            
            for p in parent._recurse_for_parents(parent):
                
                if slug == p.slug:
                    raise ValidationError(_(u'You may not save a target in itself!'))
        
        return parent