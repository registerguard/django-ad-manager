from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ad_manager.models import *

# For future reference: http://stackoverflow.com/questions/3098681/is-there-a-naming-convention-for-django-apps (next app don't use underscores).
# https://bitbucket.org/codekoala/django-articles/src/fc6a1ae96dc8/articles/admin.py
# https://github.com/concentricsky/django-basic-models/blob/master/basic_models/admin.py

#--------------------------------------------------------------------------
#
# Model inlines:
#
#--------------------------------------------------------------------------

class AdInline(admin.TabularInline):
    
    fields = ('section', 'page_type', 'ad_type', 'site', 'ad_id', 'status', 'is_active', 'publish_date', 'expiration_date',)
    
    model = Ad
    extra = 0

#--------------------------------------------------------------------------
#
# Admin models:
#
#--------------------------------------------------------------------------

class SiteAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = ('slug', 'name', 'notes',)
    
    prepopulated_fields = {
        'slug': ['name',],
    }
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = ('__unicode__', 'name', 'slug',)
    list_editable = ('name', 'slug',)
    
    search_fields = ('name',)
    
    #----------------------------------
    # Inlines:
    #----------------------------------
    
    inlines = [
        AdInline,
    ]

class AdAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fieldsets = [
        
        (None, {
            'fields': (
                'site',
                'ad_id',
                'ad_type',
                'section',
                'status',
                'page_type',
                'notes',
            ),
        }),
        
        ('Scheduling', {
            'fields': [
                'is_active',
                (
                    'publish_date',
                    'expiration_date',
                ),
            ],
        }),
        
    ]
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = ('__unicode__', 'section', 'page_type', 'ad_type', 'site', 'ad_id', 'status', 'is_active', 'publish_date', 'expiration_date',)
    list_filter  = ('section', 'page_type', 'ad_type', 'site', 'status', 'is_active',)
    list_per_page = 250
    
    search_fields = ('name', 'site', 'ad_id',)
    
    actions = ['mark_active', 'mark_inactive',]
    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True
    
    #----------------------------------
    # Change list actions:
    #----------------------------------
    
    def mark_active(self, request, queryset):
        
        queryset.update(is_active=True)
        
    mark_active.short_description = _(u'Mark selected ads as active')
    
    #----------------------------------
    
    def mark_inactive(self, request, queryset):
        
        queryset.update(is_active=False)
        
    mark_inactive.short_description = _(u'Mark selected ads as inactive')
    
    #----------------------------------
    
    def get_actions(self, request):
        
        actions = super(AdAdmin, self).get_actions(request)
        
        def dynamic_status(name, status):
            
            def status_func(self, request, queryset):
                
                queryset.update(status=status)
            
            status_func.__name__ = name
            
            status_func.short_description = _(u'Set status of selected to "%s"' % status)
            
            return status_func
        
        for status in AdStatus.objects.all():
            
            name = 'mark_status_%i' % status.id
            
            actions[name] = (dynamic_status(name, status), name, _(u'Set status of selected to "%s"' % status))
            
        return actions
    
    #----------------------------------
    # Change forms:
    #----------------------------------
    
    save_on_top = True
    save_as     = True

class SectionAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = ('slug', 'name', 'parent', 'aug_id', 'notes',)
    
    prepopulated_fields = {
        'slug': ['name',],
    }
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = ('__unicode__', 'name', 'slug', 'aug_id', 'parent',)
    list_editable = ('name', 'slug', 'aug_id', 'parent',)
    
    search_fields = ('name', 'aug_id', 'parent',)

class PageTypeAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = ('slug', 'name', 'notes',)
    
    prepopulated_fields = {
        'slug': ['name',],
    }
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    actions_selection_counter = True

class AdTypeAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = ('tag_type', 'name', 'width', 'height', 'notes',)
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = ('__unicode__', 'name', 'width', 'height', 'tag_type',)
    list_editable = ('name', 'width', 'height', 'tag_type',)
    list_filter  = ('tag_type',)
    
    search_fields = ('name', 'width', 'height', 'tag_type',)

class AdStatusAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fieldsets = [
        
        (None, {
            'fields': [
                (
                    'name',
                    'is_live',
                ),
                'ordering',
                'notes',
            ],
        }),
        
    ]
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = ('__unicode__', 'name', 'is_live',)
    list_editable = ('name', 'is_live',)
    list_filter  = ('is_live',)
    
    search_fields = (
        'name',
    )
    
    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True

#--------------------------------------------------------------------------
#
# Registrations:
#
#--------------------------------------------------------------------------

admin.site.register(Site, SiteAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(PageType, PageTypeAdmin)
admin.site.register(AdType, AdTypeAdmin)
admin.site.register(AdStatus, AdStatusAdmin)
