from django.contrib import admin
from .models import Role, Permission, RolePermission, UserRole, PermissionCache


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'is_system', 'is_active', 'user_count', 'permission_count', 'created_at']
    list_filter = ['is_system', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'organization')
        }),
        ('Configuración', {
            'fields': ('is_system', 'is_active')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'name', 'module', 'organization', 'is_active']
    list_filter = ['module', 'is_active']
    search_fields = ['codename', 'name', 'description']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codename', 'name', 'module', 'organization')
        }),
        ('Configuración', {
            'fields': ('description', 'actions', 'is_active')
        }),
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'organization', 'granted_at', 'granted_by']
    list_filter = ['granted_at']
    search_fields = ['role__name', 'permission__name']
    readonly_fields = ['granted_at', 'granted_by']
    autocomplete_fields = ['role', 'permission']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'organization', 'is_active', 'assigned_at', 'expires_at']
    list_filter = ['is_active', 'assigned_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'role__name']
    readonly_fields = ['assigned_at', 'assigned_by']
    autocomplete_fields = ['user', 'role']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('user', 'role', 'organization')
        }),
        ('Estado', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Auditoría', {
            'fields': ('assigned_by', 'assigned_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PermissionCache)
class PermissionCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_updated']
    
    actions = ['refresh_cache']
    
    def refresh_cache(self, request, queryset):
        for cache in queryset:
            cache.refresh_cache()
        self.message_user(request, f'{queryset.count()} cachés actualizados')
    refresh_cache.short_description = 'Actualizar cachés seleccionados'
