"""
Script para ejecutar DIRECTAMENTE en el Shell de Render
Copia todo el contenido de este archivo y pégalo en el shell de Render
"""

from apps.organizations.models import LandingPageConfig

# Obtener todas las configuraciones
configs = LandingPageConfig.objects.all()
print(f'📋 Total configuraciones encontradas: {configs.count()}')

updated = 0

for config in configs:
    print(f'\n🔧 Procesando: {config.organization.name}')
    needs_update = False
    
    # Campos que deben tener valores por defecto
    updates = []
    
    if not config.navbar_hover_color or config.navbar_hover_color == '':
        config.navbar_hover_color = '#2563eb'
        updates.append('navbar_hover_color')
        needs_update = True
    
    if not config.hero_style or config.hero_style == '':
        config.hero_style = 'gradient'
        updates.append('hero_style')
        needs_update = True
    
    if config.hero_overlay_opacity is None:
        config.hero_overlay_opacity = 50
        updates.append('hero_overlay_opacity')
        needs_update = True
    
    if not config.cta_badge_color or config.cta_badge_color == '':
        config.cta_badge_color = '#10b981'
        updates.append('cta_badge_color')
        needs_update = True
    
    if not config.services_layout or config.services_layout == '':
        config.services_layout = 'grid'
        updates.append('services_layout')
        needs_update = True
    
    if not config.services_bg_color or config.services_bg_color == '':
        config.services_bg_color = '#f9fafb'
        updates.append('services_bg_color')
        needs_update = True
    
    if config.heading_font_size is None or config.heading_font_size == 0:
        config.heading_font_size = 48
        updates.append('heading_font_size')
        needs_update = True
    
    if config.button_border_radius is None:
        config.button_border_radius = 8
        updates.append('button_border_radius')
        needs_update = True
    
    if config.card_border_radius is None:
        config.card_border_radius = 12
        updates.append('card_border_radius')
        needs_update = True
    
    if not config.card_shadow_intensity or config.card_shadow_intensity == '':
        config.card_shadow_intensity = 'md'
        updates.append('card_shadow_intensity')
        needs_update = True
    
    if not config.section_spacing or config.section_spacing == '':
        config.section_spacing = 'normal'
        updates.append('section_spacing')
        needs_update = True
    
    if not config.footer_bg_color or config.footer_bg_color == '':
        config.footer_bg_color = '#111827'
        updates.append('footer_bg_color')
        needs_update = True
    
    # Asegurar campos de color del hero
    if not config.hero_bg_gradient_start or config.hero_bg_gradient_start == '':
        config.hero_bg_gradient_start = '#3b82f6'
        updates.append('hero_bg_gradient_start')
        needs_update = True
    
    if not config.hero_bg_gradient_end or config.hero_bg_gradient_end == '':
        config.hero_bg_gradient_end = '#8b5cf6'
        updates.append('hero_bg_gradient_end')
        needs_update = True
    
    if needs_update:
        try:
            config.save()
            updated += 1
            print(f'   ✅ Actualizado: {", ".join(updates)}')
        except Exception as e:
            print(f'   ❌ Error al guardar: {str(e)}')
    else:
        print(f'   ℹ️  No necesita actualización')

print(f'\n🎉 Proceso completado!')
print(f'📊 Total actualizadas: {updated}/{configs.count()}')
print('\n✅ Ahora intenta subir el logo de nuevo')
