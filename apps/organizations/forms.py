from django import forms
from .models import LandingPageConfig


class LandingPageConfigForm(forms.ModelForm):
    """Formulario para configurar la landing page"""
    
    class Meta:
        model = LandingPageConfig
        fields = [
            # Navbar
            'navbar_style', 'navbar_bg_color', 'navbar_text_color', 'navbar_hover_color',
            # Hero
            'hero_style', 'hero_bg_gradient_start', 'hero_bg_gradient_end', 'hero_overlay_opacity',
            'hero_image', 'hero_title', 'hero_subtitle', 'hero_title_color', 'hero_subtitle_color',
            'cta_badge_text', 'cta_badge_color',
            # Servicios
            'services_layout', 'services_bg_color',
            'why_choose_title', 'why_choose_subtitle',
            'services_title', 'services_subtitle',
            'service_image_1', 'service_1_title', 'service_1_description',
            'service_image_2', 'service_2_title', 'service_2_description',
            'service_image_3', 'service_3_title', 'service_3_description',
            'service_image_4', 'service_4_title', 'service_4_description',
            # Contacto
            'contact_title', 'contact_subtitle',
            # Diseño y estilo
            'font_family', 'heading_font_size',
            'primary_button_color', 'secondary_button_color', 'button_border_radius', 'button_shadow',
            'card_border_radius', 'card_shadow_intensity',
            'section_spacing',
            # Efectos
            'animation_speed', 'enable_parallax', 'enable_hover_effects',
            'show_scroll_indicator', 'show_testimonials', 'show_stats',
            # Footer
            'footer_bg_color'
        ]
        widgets = {
            # Estilos
            'navbar_style': forms.RadioSelect(attrs={'class': 'style-selector'}),
            'hero_style': forms.RadioSelect(attrs={'class': 'style-selector'}),
            'services_layout': forms.RadioSelect(attrs={'class': 'style-selector'}),
            'font_family': forms.RadioSelect(attrs={'class': 'style-selector'}),
            'animation_speed': forms.RadioSelect(attrs={'class': 'style-selector'}),
            'card_shadow_intensity': forms.RadioSelect(attrs={'class': 'style-selector'}),
            'section_spacing': forms.RadioSelect(attrs={'class': 'style-selector'}),
            
            # Colores
            'navbar_bg_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'navbar_text_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'navbar_hover_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'primary_button_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'secondary_button_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'footer_bg_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'hero_image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'service_image_1': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'service_image_2': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'service_image_3': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'service_image_4': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'hero_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Cuida tu Salud Visual'
            }),
            'hero_subtitle': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Tecnología de última generación...'
            }),
            'hero_title_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'hero_subtitle_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'hero_bg_gradient_start': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'hero_bg_gradient_end': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'services_bg_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'cta_badge_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-input w-24 h-10 cursor-pointer'
            }),
            'why_choose_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': '¿Por qué elegirnos?'
            }),
            'why_choose_subtitle': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'La mejor atención para tus ojos'
            }),
            'services_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nuestros Servicios'
            }),
            'services_subtitle': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Cuidado integral para tu salud visual'
            }),
            'service_1_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Examen Visual Completo'
            }),
            'service_1_description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': 'Descripción del servicio...'
            }),
            'service_2_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Monturas y Lentes'
            }),
            'service_2_description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': 'Descripción del servicio...'
            }),
            'service_3_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Lentes de Contacto'
            }),
            'service_3_description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': 'Descripción del servicio...'
            }),
            'service_4_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Lentes de Sol'
            }),
            'service_4_description': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': 'Descripción del servicio...'
            }),
            'contact_title': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': '¿Tienes Preguntas?'
            }),
            'contact_subtitle': forms.Textarea(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 2,
                'placeholder': 'Estamos aquí para ayudarte...'
            }),
            # Números y sliders
            'hero_overlay_opacity': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg',
                'min': '0',
                'max': '100',
                'step': '5'
            }),
            'heading_font_size': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg',
                'min': '24',
                'max': '96',
                'step': '4'
            }),
            'button_border_radius': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg',
                'min': '0',
                'max': '999',
                'step': '2'
            }),
            'card_border_radius': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg',
                'min': '0',
                'max': '999',
                'step': '2'
            }),
            'cta_badge_text': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ej: Nuevo, Popular, Oferta'
            }),
            # Checkboxes
            'button_shadow': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
            'enable_parallax': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
            'enable_hover_effects': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
            'show_scroll_indicator': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
            'show_testimonials': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
            'show_stats': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }
