from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ad_manager.forms import *
from ad_manager.models import *

# For future reference: http://stackoverflow.com/questions/3098681/is-there-a-naming-convention-for-django-apps (next app don't use underscores).
# https://bitbucket.org/codekoala/django-articles/src/fc6a1ae96dc8/articles/admin.py
# https://github.com/concentricsky/django-basic-models/blob/master/basic_models/admin.py
# https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields

#--------------------------------------------------------------------------
#
# Model inlines:
#
#--------------------------------------------------------------------------

class AdAdminInline(admin.TabularInline):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = (
        'ad_id',
        'is_active',
        'publish_date',
        'expiration_date',
        'ad_type',
        'ad_group',
    )
    
    #----------------------------------
    # Inline-specific options:
    #----------------------------------
    
    model = Ad
    
    extra = 0

#--------------------------------------------------------------------------
#
# Admin models:
#
#--------------------------------------------------------------------------

class TargetAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fieldsets = [
        
        ('Meta', {
            'fields': (
                'slug',
            ),
            'classes': (
                'collapse',
            ),
        },),
        
        (None, {
            'fields': [
                'parent',
                'name',
                'notes',
            ],
        },),
        
    ]
    
    prepopulated_fields = {
        'slug': ['name',],
    }
    
    #----------------------------------
    # Forms:
    #----------------------------------
    
    form = TargetAdminForm
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = (
        '__unicode__',
        'parent',
        'name',
        'slug',
    )
    
    list_editable = (
        'name',
        'parent',
        'slug',
    )
    
    list_per_page = 50
    
    search_fields = (
        'name',
        'parent__name',
    )
    
    actions_on_top = True
    
    actions_on_bottom = True
    
    actions_selection_counter = True

class AdGroupAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = (
        'target',
        'page_type',
        'aug_id',
        'notes',
    )
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = (
        '__unicode__',
        'target',
        'page_type',
        'aug_id',
    )
    
    list_editable = (
        'aug_id',
        'page_type',
        'target',
    )
    
    list_per_page = 50
    
    search_fields = (
        'aug_id',
        'notes',
        'page_type__name',
        'target__name',
        'target__parent__name',
    )
    
    actions_on_top = True
    
    actions_on_bottom = True
    
    actions_selection_counter = True
    
    #----------------------------------
    # Inlines:
    #----------------------------------
    
    inlines = [
        AdAdminInline,
    ]

class AdAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fieldsets = [
        
        (None, {
            'fields': (
                'ad_group',
                'ad_type',
                'ad_id',
                'notes',
            ),
        },),
        
        ('Scheduling', {
            'fields': [
                'is_active',
                (
                    'publish_date',
                    'expiration_date',
                ),
            ],
        },),
        
    ]
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = (
        '__unicode__',
        'ad_group',
        'ad_type',
        'ad_id',
        'is_active',
        'publish_date',
        'expiration_date',
    )
    
    list_editable = (
        'ad_group',
        'ad_id',
        'ad_type',
        'expiration_date',
        'is_active',
        'publish_date',
    )
    
    list_filter  = (
        'ad_group',
        'ad_type',
        'is_active',
    )
    
    list_per_page = 50
    
    search_fields = (
        'ad_group__aug_id',
        'ad_group__page_type__name',
        'ad_group__target__name',
        'ad_group__target__parent__name',
        'ad_id',
        'ad_type__height',
        'ad_type__name',
        'ad_type__width',
        'notes',
    )
    
    actions = [
        'mark_active',
        'mark_inactive',
    ]
    
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
    # Change forms:
    #----------------------------------
    
    save_on_top = True
    
    save_as     = True

class PageTypeAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fieldsets = [
        
        ('Meta', {
            'fields': (
                'slug',
            ),
            'classes': (
                'collapse',
            ),
        },),
        
        (None, {
            'fields': [
                'name',
                'notes',
            ],
        },),
        
    ]
    
    prepopulated_fields = {
        'slug': ['name',],
    }
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = (
        '__unicode__',
        'name',
        'slug',
    )
    
    list_editable = (
        'name',
        'slug',
    )
    
    list_per_page = 50
    
    actions_on_top = True
    
    actions_on_bottom = True
    
    actions_selection_counter = True
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    actions_selection_counter = True

class AdTypeAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = (
        'name',
        'width',
        'height',
        'tag_type',
        'notes',
    )
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = (
        '__unicode__',
        'name',
        'width',
        'height',
        'tag_type',
    )
    
    list_editable = (
        'height',
        'name',
        'tag_type',
        'width',
    )
    
    list_filter  = (
        'tag_type',
    )
    
    list_per_page = 50
    
    search_fields = (
        'height',
        'name',
        'notes',
        'tag_type__name',
        'width',
    )
    
    actions_on_top = True
    
    actions_on_bottom = True
    
    actions_selection_counter = True

class TagTypeAdmin(admin.ModelAdmin):
    
    #----------------------------------
    # Fields:
    #----------------------------------
    
    fields = (
        'name',
    )
    
    #----------------------------------
    # Change lists:
    #----------------------------------
    
    list_display = (
        '__unicode__',
        'name',
    )
    
    list_editable = (
        'name',
    )
    
    list_per_page = 50
    
    actions_on_top = True
    
    actions_on_bottom = True
    
    actions_selection_counter = True

#--------------------------------------------------------------------------
#
# Registrations:
#
#--------------------------------------------------------------------------

admin.site.register(Target, TargetAdmin)
admin.site.register(AdGroup, AdGroupAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(PageType, PageTypeAdmin)
admin.site.register(AdType, AdTypeAdmin)
admin.site.register(TagType, TagTypeAdmin)
