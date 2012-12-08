import datetime

from django import forms
from django.core import urlresolvers
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from ad_manager import managers

# https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/

# https://bitbucket.org/codekoala/django-articles/src/f1dedb2723cbe66e1c849e1513eeba61dd4f59ec/articles/models.py?at=default
# https://github.com/praekelt/django-category
# https://bitbucket.org/chris1610/satchmo/src/1730bf912bc1/satchmo/apps/product/models.py?at=default
# http://thefekete.net/blog/sorting-hierarchical-categories-in-django/
# https://docs.djangoproject.com/en/1.4/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display

"""
    Notes to (future) self:
    
    * Ordering fields alphabetically.
    * Using slug fields for anything that shows in URI.
    * The db_index=True is set by default for SlugFields.
    * The permalink decorator is no longer recommended. You should use reverse() in the body of your get_absolute_url method instead.
    * PEP8: For flowing long blocks of text (docstrings or comments), limiting the length to 72 characters is recommended.
"""

#--------------------------------------------------------------------------
#
# Abstract:
#
#--------------------------------------------------------------------------

class Base(models.Model):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Hidden:
    created  = models.DateTimeField(auto_now_add=True, editable=False,)
    modified = models.DateTimeField(auto_now=True, editable=False,)
    
    # Base:
    notes = models.TextField(_(u'notes'), blank=True, help_text=_(u'Not published.'),)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        abstract = True
        get_latest_by = 'modified'
    
    #----------------------------------
    # Custom methods:
    #----------------------------------
    
    @property
    def is_modified(self):
        
        return self.modified > self.created

#--------------------------------------------------------------------------
#
# Models:
#
#--------------------------------------------------------------------------

class Target(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Meta:
    slug = models.SlugField(max_length=255, help_text=_(u'Short descriptive unique name for use in urls.'),)
    
    # Base:
    name = models.CharField(_(u'name'), max_length=200, help_text=_(u'Short descriptive name for this target.'),)
    
    # Foreign keys:
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child',)
    
    #----------------------------------
    # Custom manager attributes:
    #----------------------------------
    
    objects = managers.TargetManager()
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ['parent__name', 'name',]
        unique_together = ('slug', 'parent',)
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        name_list = [target.name.upper() for target in self._recurse_for_parents(self)]
        
        name_list.append(self.name)
        
        return _(u'%s') % self.get_separator().join(name_list)
    
    #----------------------------------
    # def save()
    #----------------------------------
    
    def save(self, **kwargs):
        
        if self.id:
            
            if self.parent and self.parent_id == self.id:
                raise forms.ValidationError(_(u'You may not save a target in itself!'))
            
            for p in self._recurse_for_parents(self):
                
                if self.id == p.id:
                    raise forms.ValidationError(_(u'You may not save a target in itself!'))
        
        if not self.slug:
            self.slug = slugify(self.name)
        
        super(Target, self).save(**kwargs) # Call the "real" save()
    
    #----------------------------------
    # def get_absolute_url()
    #----------------------------------
    
    def get_absolute_url(self):
        
        parents = self._recurse_for_parents(self)
        
        slug_list = [target.slug for target in parents]
        
        if slug_list:
            slug_list = '/'.join(slug_list) + '/'
        
        else:
            slug_list = ''
        
        return urlresolvers.reverse('ad_manager_target_detail', kwargs={'parent_slugs' : slug_list, 'slug' : self.slug})
    
    #----------------------------------
    # Custom methods:
    #----------------------------------
    
    def parents(self):
        
        return self._recurse_for_parents(self)
    
    #----------------------------------
    
    def children(self):
        
        return self.target_set.all().order_by('name')
    
    #----------------------------------
    
    def get_separator(self):
        
        return ' | '
    
    #----------------------------------
    
    def _recurse_for_parents(self, target_obj):
        
        p_list = []
        
        if target_obj.parent_id:
            
            p = target_obj.parent
            p_list.append(p)
            
            if p != self:
                
                more = self._recurse_for_parents(p)
                p_list.extend(more)
        
        if target_obj == self and p_list:
            p_list.reverse()
        
        return p_list
    
    #----------------------------------
    
    def _parents_repr(self):
        
        """
        Representation of targets.
        """
        
        name_list = [target.name for target in self._recurse_for_parents(self)]
        
        return self.get_separator().join(name_list)
        
    _parents_repr.short_description = _(u'Target parents')
    
    #----------------------------------
    
    def get_url_name(self):
        
        """
        Get all the absolute URLs and names for use in the site navigation.
        """
        
        name_list = []
        url_list = []
        
        for target in self._recurse_for_parents(self):
            
            name_list.append(target.name)
            url_list.append(target.get_absolute_url())
        
        name_list.append(self.name)
        
        url_list.append(self.get_absolute_url())
        
        return zip(name_list, url_list)
    
    #----------------------------------
    
    def _flatten(self, L):
        
        """
        Taken from a python newsgroup post.
        """
        
        if type(L) != type([]): return [L]
        
        if L == []: return L
        
        return self._flatten(L[0]) + self._flatten(L[1:])
    
    #----------------------------------
    
    def _recurse_for_children(self, node):
        
        children = []
        
        children.append(node)
        
        for child in node.child.all():
            
            if child != self:
                
                children_list = self._recurse_for_children(child)
                children.append(children_list)
        
        return children
    
    #----------------------------------
    
    def get_all_children(self, include_self=False):
        
        """
        Gets a list of all of the children targets.
        """
        
        children_list = self._recurse_for_children(self)
        
        if include_self:
            ix = 0
        else:
            ix = 1
        
        flat_list = self._flatten(children_list[ix:])
        
        return flat_list

class AdGroup(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Base:
    aug_id = models.IntegerField(_(u'ad unit group ID'),)
    
    # Foreign keys:
    page_type = models.ForeignKey('PageType', blank=True, null=True, related_name='ad_group',)
    target    = models.ForeignKey('Target', related_name='ad_group',)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ['target',]
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        #return _(u'%s') % ' | '.join(filter(None, (self.target, str(self.page_type))))
        
        return _(u'%s%s%s') % (self.target, (' | ' if self.page_type else ''), self.page_type)

class Ad(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Base:
    ad_id = models.IntegerField(_(u'ad unit ID'), unique=True,)
    
    # Scheduling:
    expiration_date = models.DateField(_(u'expiration date'), blank=True, null=True, help_text=_(u'Leave blank if the ad does not expire.'),)
    is_active       = models.BooleanField(_(u'active?'), default=True, blank=True, help_text=_(u'Disables/enables ad for everyone (including super admins).'),)
    publish_date    = models.DateField(_(u'publish date'), default=datetime.date.today, help_text=_(u'The date this ad shall appear online.'),)
    
    # Foreign keys:
    ad_group = models.ForeignKey('AdGroup', related_name='ad',)
    ad_type  = models.ForeignKey('AdType', related_name='ad',)
    
    #----------------------------------
    # Custom manager attributes:
    #----------------------------------
    
    objects = managers.AdManager()
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ['ad_group',]
        get_latest_by = 'modified'
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return _(u'%s | %s') % (self.ad_group, self.ad_type)
    
    #----------------------------------
    
    def __init__(self, *args, **kwargs):
        
        super(Ad, self).__init__(*args, **kwargs)
        
        if self.pk:
            
            # Mark the page as inactive if it's expired and still active:
            if self.expiration_date and self.expiration_date <= datetime.datetime.now() and self.is_active:
                
                self.is_active = False
                
                self.save()

class PageType(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Meta:
    slug = models.SlugField(max_length=255, unique=True, help_text=_(u'Short descriptive unique name for use in urls.'),)
    
    # Base:
    name = models.CharField(_(u'name'), max_length=200, help_text=_(u'Short descriptive name for page type.'),)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ['name',]
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return _(u'%s') % self.name
    
    #----------------------------------
    # def get_absolute_url()
    #----------------------------------
    
    def get_absolute_url(self):
        
        return reverse('pagetype_object_list', kwargs={'pagetype_slug': self.slug})

class AdType(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Base:
    height = models.IntegerField(_(u'height'),)
    name   = models.CharField(_(u'name'), max_length=200, help_text=_(u'Short descriptive name for this ad type.'),)
    width  = models.IntegerField(_(u'width'),)
    
    # Foreign keys:
    tag_type = models.ForeignKey('TagType', related_name='ad_type',)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ['name',]
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return _(u'%s | %s x %s') % (self.name, self.width, self.height)

class TagType(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Base:
    name = models.CharField(_(u'name'), max_length=200, help_text=_(u'Ad tag "type"; examples: &lt;iframe&gt;, &lt;script&gt;, &lt;img&gt;...'),)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        pass
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return _(u'%s') % self.name
