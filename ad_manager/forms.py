from django.forms import models, ValidationError
from django.utils.translation import ugettext_lazy as _

# https://docs.djangoproject.com/en/dev/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other

class TargetAdminForm(models.ModelForm):
    
    """
    Validation of a Form is split into several steps, which can be customized or overridden:
    
    `to_python()`
    `validate()`
    `run_validators()`
    `clean()`
    `clean_<fieldname>()`
    `clean()`
    
    The `clean_<fieldname>()` method in a form subclass - where
    `<fieldname>` is replaced with the name of the form field attribute.
    This method does any cleaning that is specific to that particular
    attribute, unrelated to the type of field that it is. This method is
    not passed any parameters. You will need to look up the value of the
    field in `self.cleaned_data` and remember that it will be a Python
    object at this point, not the original string submitted in the form (it
    will be in `cleaned_data` because the general field `clean()` method,
    above, has already cleaned the data once).
    """
    
    def clean_parent(self):
        
        # Get the `parent` or None:
        parent = self.cleaned_data.get('parent', None)
        
        # Get the `slug` or None:
        slug = self.cleaned_data.get('slug', None)
        
        # Do both exist?
        if parent and slug:
            
            # Does the parent's slug match the current slug?
            if parent.slug == slug:
                
                # Not allowed:
                raise ValidationError(_(u'You may not save a target in itself!'))
            
            for p in parent._recurse_for_parents(parent):
                
                # ...what about parent slugs?
                if slug == p.slug:
                    
                    # Not allowed:
                    raise ValidationError(_(u'You may not save a target in itself!'))
        
        # Buh-bye!
        return parent # Return the cleaned data, regardless of whether it changed anything or not.