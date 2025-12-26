from django.core.management.base import BaseCommand
from apps.organizations.models import LandingPageConfig


class Command(BaseCommand):
    help = 'Actualiza las configuraciones de landing page con valores por defecto faltantes'

    def handle(self, *args, **options):
        configs = LandingPageConfig.objects.all()
        updated = 0
        
        for config in configs:
            needs_update = False
            
            # Verificar y actualizar campos que pueden estar vacíos o None
            if not config.navbar_hover_color:
                config.navbar_hover_color = '#2563eb'
                needs_update = True
            
            if not config.hero_style:
                config.hero_style = 'gradient'
                needs_update = True
            
            if config.hero_overlay_opacity is None:
                config.hero_overlay_opacity = 50
                needs_update = True
            
            if not config.cta_badge_color:
                config.cta_badge_color = '#10b981'
                needs_update = True
            
            if not config.services_layout:
                config.services_layout = 'grid'
                needs_update = True
            
            if not config.services_bg_color:
                config.services_bg_color = '#f9fafb'
                needs_update = True
            
            if config.heading_font_size is None or config.heading_font_size == 0:
                config.heading_font_size = 48
                needs_update = True
            
            if config.button_border_radius is None:
                config.button_border_radius = 8
                needs_update = True
            
            if config.card_border_radius is None:
                config.card_border_radius = 12
                needs_update = True
            
            if not config.card_shadow_intensity:
                config.card_shadow_intensity = 'md'
                needs_update = True
            
            if not config.section_spacing:
                config.section_spacing = 'normal'
                needs_update = True
            
            if not config.footer_bg_color:
                config.footer_bg_color = '#111827'
                needs_update = True
            
            if needs_update:
                config.save()
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Actualizado config para: {config.organization.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado. {updated} configuraciones actualizadas.'
            )
        )
