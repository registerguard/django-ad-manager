import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ad_manager import managers

# https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/

# https://bitbucket.org/codekoala/django-articles/src/f1dedb2723cbe66e1c849e1513eeba61dd4f59ec/articles/models.py?at=default
# https://github.com/praekelt/django-category

"""
    Notes to (future) self:
    
    * Ordering fields alphabetically.
    * Using slug fields for anything that shows in URI.
    * The db_index=True is set by default for SlugFields.
    * The permalink decorator is no longer recommended. You should use reverse() in the body of your get_absolute_url method instead.
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

class Site(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Meta:
    slug = models.SlugField(max_length=255, unique=True, help_text='Short descriptive unique name for use in urls.',)
    
    # Base:
    name = models.CharField(_(u'name'), max_length=200, help_text=_(u'Short descriptive name for this site.'),)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        pass
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return self.name
    
    #----------------------------------
    # Custom methods:
    #----------------------------------
    
    def get_absolute_url(self):
        
        return reverse('site_object_list', kwargs={'site_slug': self.slug})

class Ad(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Base:
    ad_id  = models.IntegerField(_(u'Ad id'), unique=True,)
    status = models.ForeignKey('AdStatus', default='AdStatus.objects.default', help_text=_(u'Ads with non-"live" statuses will still be visible to super admins.'),)
    
    # Scheduling:
    is_active       = models.BooleanField(_(u'active?'), default=True, blank=True, help_text=_(u'Disables/enables ad for everyone (including super admins).'),)
    publish_date    = models.DateTimeField(_(u'publish date'), default=datetime.datetime.now, help_text=_(u'The date and time this ad shall appear online.'),)
    expiration_date = models.DateTimeField(_(u'expiration date'), blank=True, null=True, help_text=_(u'Leave blank if the ad does not expire.'),)
    
    # Foreign keys:
    ad_type   = models.ForeignKey('AdType',)
    page_type = models.ForeignKey('PageType', blank=True, null=True,)
    section   = models.ForeignKey('Section',)
    site      = models.ForeignKey('Site',)
    
    #----------------------------------
    # Custom manager attributes:
    #----------------------------------
    
    objects = managers.AdManager()
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        pass
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return _(u'%s | %s | %s') % (self.section, self.page_type, self.ad_type)
    
    #----------------------------------
    
    def __init__(self, *args, **kwargs):
        
        super(Ad, self).__init__(*args, **kwargs)
        
        if self.pk:
            
            # Mark the page as inactive if it's expired and still active:
            if self.expiration_date and self.expiration_date <= datetime.datetime.now() and self.is_active:
                self.is_active = False
                self.save()

class Section(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Meta:
    slug = models.SlugField(max_length=255, unique=True, help_text='Short descriptive unique name for use in urls.',)
    
    # Base:
    aug_id = models.IntegerField(_(u'AUG id'),)
    name   = models.CharField(_(u'name'), max_length=200, help_text=_(u'Short descriptive name for this section.'),)
    
    # Foreign keys:
    parent = models.ForeignKey('self', null=True, blank=True,)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ('name',)
        verbose_name = 'section'
        verbose_name_plural = 'sections'
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        #return _(u'%s%s %s') % (self.get('name', ''), (' | ' if self.parent else ''), self.name)
        
        # Add " | " between fields with values:
        #return _(u'%s') % ' | '.join(filter(None, (self.parent.name, self.name)))
        return self.name
    
    #----------------------------------
    # def save()
    #----------------------------------
    
    def save(self, *args, **kwargs):
        
        # Raise on circular reference:
        parent = self.parent
        while parent is not None:
            if parent == self:
                raise RuntimeError, 'Circular references not allowed!'
            parent = parent.parent
        
        super(Section, self).save(*args, **kwargs)
    
    #----------------------------------
    # def get_absolute_url()
    #----------------------------------
    
    def get_absolute_url(self):
        
        return reverse('section_object_list', kwargs={'section_slug': self.slug}) # Doc example: return reverse('people.views.details', args=[str(self.id)])
    
    #----------------------------------
    # Custom methods:
    #----------------------------------
    
    @property
    def children(self):
        
        return self.category_set.all().order_by('name')

class PageType(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Meta:
    slug = models.SlugField(max_length=255, unique=True, help_text='Short descriptive unique name for use in urls.',)
    
    # Base:
    name = models.CharField(_(u'name'), max_length=200, help_text=_(u'Short descriptive name for page type.'),)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        pass
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return self.name
    
    #----------------------------------
    # def get_absolute_url()
    #----------------------------------
    
    def get_absolute_url(self):
        
        return reverse('pagetype_object_list', kwargs={'pagetype_slug': self.slug})

class AdType(Base):
    
    #----------------------------------
    # Choices:
    #----------------------------------
    
    IFRAME = 1
    SCRIPT = 2
    TAG_CHOICES = (
        (IFRAME, _(u'<iframe>')),
        (SCRIPT, _(u'<script>')),
    )
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Base:
    name     = models.CharField(_(u'name'), max_length=200, help_text=_(u'Short descriptive name for this ad type.'),)
    height   = models.IntegerField(_(u'height'),)
    tag_type = models.IntegerField(_(u'tag type'), choices=TAG_CHOICES,)
    width    = models.IntegerField(_(u'width'),)
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ('name',)
        verbose_name = 'ad type'
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        return _(u'%s | %s x %s') % (self.name, self.width, self.height)

class AdStatus(Base):
    
    #----------------------------------
    # All database fields:
    #----------------------------------
    
    # Meta:
    is_live  = models.BooleanField(_(u'live?'), default=True, blank=True,)
    ordering = models.IntegerField(_(u'ordering'), default=0,)
    
    # Base:
    name = models.CharField(_(u'name'), max_length=50,)
    
    #----------------------------------
    # Custom manager attributes:
    #----------------------------------
    
    objects = managers.AdStatusManager()
    
    #----------------------------------
    # Class Meta:
    #----------------------------------
    
    class Meta:
        
        ordering = ('ordering', 'name',)
        verbose_name_plural = _(u'Ad statuses')
    
    #----------------------------------
    # def __XXX__()
    #----------------------------------
    
    def __unicode__(self):
        
        if self.is_live:
            return u'%s (live)' % self.name
        else:
            return self.name
