from django.contrib import admin
from .models import SubscriptionPlan, Organization, Subscription, OrganizationMember, LandingPageConfig, PlanFeature


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code', 'description']
    prepopulated_fields = {'code': ('name',)}


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_monthly', 'price_yearly', 'max_users', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['features']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'billing_cycle', 'start_date', 'end_date', 'is_active', 'payment_status']
    list_filter = ['billing_cycle', 'is_active', 'payment_status', 'plan']
    search_fields = ['organization__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__email', 'organization__name']


@admin.register(LandingPageConfig)
class LandingPageConfigAdmin(admin.ModelAdmin):
    list_display = ['organization', 'navbar_bg_color', 'primary_button_color', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['organization__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Organización', {
            'fields': ('organization',)
        }),
        ('Estilos y Diseños', {
            'fields': ('navbar_style', 'hero_style', 'services_layout', 'font_family'),
            'description': 'Selecciona los estilos principales de tu landing page'
        }),
        ('Navbar', {
            'fields': ('navbar_bg_color', 'navbar_text_color', 'navbar_hover_color')
        }),
        ('Sección Hero', {
            'fields': (
                'hero_bg_gradient_start', 'hero_bg_gradient_end', 
                'hero_overlay_opacity', 'hero_image', 
                'hero_title', 'hero_title_color', 
                'hero_subtitle', 'hero_subtitle_color',
                'heading_font_size'
            )
        }),
        ('Badge CTA', {
            'fields': ('cta_badge_text', 'cta_badge_color'),
            'classes': ('collapse',)
        }),
        ('Sección Por Qué Elegirnos', {
            'fields': ('why_choose_title', 'why_choose_subtitle')
        }),
        ('Sección Servicios', {
            'fields': ('services_bg_color', 'services_title', 'services_subtitle')
        }),
        ('Servicio 1', {
            'fields': ('service_image_1', 'service_1_title', 'service_1_description'),
            'classes': ('collapse',)
        }),
        ('Servicio 2', {
            'fields': ('service_image_2', 'service_2_title', 'service_2_description'),
            'classes': ('collapse',)
        }),
        ('Servicio 3', {
            'fields': ('service_image_3', 'service_3_title', 'service_3_description'),
            'classes': ('collapse',)
        }),
        ('Servicio 4', {
            'fields': ('service_image_4', 'service_4_title', 'service_4_description'),
            'classes': ('collapse',)
        }),
        ('Sección Contacto', {
            'fields': ('contact_title', 'contact_subtitle')
        }),
        ('Horarios de Atención', {
            'fields': (
                'schedule_weekday_start', 'schedule_weekday_end',
                'schedule_saturday_start', 'schedule_saturday_end',
                'schedule_sunday_closed', 'schedule_sunday_start', 'schedule_sunday_end',
                'has_lunch_break', 'lunch_break_start', 'lunch_break_end'
            ),
            'description': 'Configure los horarios de atención que se mostrarán en la landing page'
        }),
        ('Botones', {
            'fields': ('primary_button_color', 'secondary_button_color', 'button_border_radius', 'button_shadow')
        }),
        ('Tarjetas y Contenedores', {
            'fields': ('card_border_radius', 'card_shadow_intensity')
        }),
        ('Espaciado', {
            'fields': ('section_spacing',)
        }),
        ('Efectos y Animaciones', {
            'fields': ('animation_speed', 'enable_parallax', 'enable_hover_effects'),
            'description': 'Agrega vida a tu página con efectos visuales'
        }),
        ('Elementos Adicionales', {
            'fields': ('show_scroll_indicator', 'show_testimonials', 'show_stats')
        }),
        ('Footer', {
            'fields': ('footer_bg_color',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
