"""
Vistas para el módulo de promociones
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from apps.promotions.models import Promotion, PromotionCampaign, PromotionMessage
from apps.promotions.services import create_campaign_messages, start_campaign, CampaignSender
import logging

logger = logging.getLogger(__name__)


@login_required
def promotion_list(request):
    """Lista todas las promociones de la organización"""
    promotions = Promotion.objects.filter(
        organization=request.organization
    ).order_by('-created_at')
    
    # Estadísticas
    total_promotions = promotions.count()
    active_promotions = promotions.filter(status='active').count()
    
    context = {
        'promotions': promotions,
        'total_promotions': total_promotions,
        'active_promotions': active_promotions,
    }
    
    return render(request, 'promotions/promotion_list.html', context)


@login_required
def promotion_create(request):
    """Crear nueva promoción"""
    if request.method == 'POST':
        try:
            promotion = Promotion.objects.create(
                organization=request.organization,
                code=request.POST.get('code').upper(),
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                discount_percentage=int(request.POST.get('discount_percentage')),
                category=request.POST.get('category'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                status=request.POST.get('status', 'active'),
                max_uses=request.POST.get('max_uses') or None,
                created_by=request.user
            )
            
            messages.success(request, f'✅ Promoción "{promotion.code}" creada exitosamente')
            return redirect('/dashboard/promociones/')
            
        except Exception as e:
            messages.error(request, f'❌ Error al crear promoción: {e}')
            logger.error(f"Error creando promoción: {e}")
    
    context = {
        'categories': Promotion.CATEGORY_CHOICES,
    }
    
    return render(request, 'promotions/promotion_form.html', context)


@login_required
def promotion_edit(request, promotion_id):
    """Editar promoción existente"""
    promotion = get_object_or_404(
        Promotion,
        id=promotion_id,
        organization=request.organization
    )
    
    if request.method == 'POST':
        try:
            promotion.name = request.POST.get('name')
            promotion.description = request.POST.get('description')
            promotion.discount_percentage = int(request.POST.get('discount_percentage'))
            promotion.category = request.POST.get('category')
            promotion.start_date = request.POST.get('start_date')
            promotion.end_date = request.POST.get('end_date')
            promotion.status = request.POST.get('status')
            promotion.max_uses = request.POST.get('max_uses') or None
            promotion.save()
            
            messages.success(request, f'✅ Promoción "{promotion.code}" actualizada')
            return redirect('/dashboard/promociones/')
            
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar: {e}')
    
    context = {
        'promotion': promotion,
        'categories': Promotion.CATEGORY_CHOICES,
        'is_edit': True,
    }
    
    return render(request, 'promotions/promotion_form.html', context)


@login_required
def promotion_delete(request, promotion_id):
    """Eliminar promoción"""
    promotion = get_object_or_404(
        Promotion,
        id=promotion_id,
        organization=request.organization
    )
    
    if request.method == 'POST':
        code = promotion.code
        promotion.delete()
        messages.success(request, f'🗑️ Promoción "{code}" eliminada')
        return redirect('/dashboard/promociones/')
    
    return redirect('/dashboard/promociones/')


# ========== CAMPAÑAS ==========

@login_required
def campaign_list(request):
    """Lista todas las campañas"""
    campaigns = PromotionCampaign.objects.filter(
        organization=request.organization
    ).select_related('promotion').order_by('-created_at')
    
    # Estadísticas
    total_campaigns = campaigns.count()
    active_campaigns = campaigns.filter(status='in_progress').count()
    completed_campaigns = campaigns.filter(status='completed').count()
    
    context = {
        'campaigns': campaigns,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns,
    }
    
    return render(request, 'promotions/campaign_list.html', context)


@login_required
def campaign_create(request):
    """Crear nueva campaña"""
    if request.method == 'POST':
        try:
            # Obtener promoción
            promotion_id = request.POST.get('promotion')
            promotion = get_object_or_404(Promotion, id=promotion_id, organization=request.organization)
            
            # Crear campaña
            campaign = PromotionCampaign.objects.create(
                organization=request.organization,
                promotion=promotion,
                name=request.POST.get('name'),
                message_template=request.POST.get('message_template'),
                recipient_filter=request.POST.get('recipient_filter'),
                daily_limit=int(request.POST.get('daily_limit', 20)),
                delay_seconds=int(request.POST.get('delay_seconds', 10)),
                send_hour_start=int(request.POST.get('send_hour_start', 9)),
                send_hour_end=int(request.POST.get('send_hour_end', 19)),
                status='draft',
                created_by=request.user
            )
            
            # Crear mensajes
            recipients_count = create_campaign_messages(campaign)
            
            messages.success(request, f'✅ Campaña creada con {recipients_count} destinatarios')
            return redirect(f'/dashboard/promociones/campanas/{campaign.id}/')
            
        except Exception as e:
            messages.error(request, f'❌ Error al crear campaña: {e}')
            logger.error(f"Error creando campaña: {e}")
    
    # Obtener promociones activas
    promotions = Promotion.objects.filter(
        organization=request.organization,
        status='active'
    )
    
    # Mensaje template por defecto
    default_template = """🎉 ¡Hola {name}!

{category_emoji} Tenemos una promoción especial para ti:

💰 {discount}% de descuento en {category}
🎁 Código: {code}

📅 Válido hasta el {end_date}

¡Visítanos y aprovecha esta oferta!

- {organization}"""
    
    context = {
        'promotions': promotions,
        'filters': PromotionCampaign.FILTER_CHOICES,
        'default_template': default_template,
    }
    
    return render(request, 'promotions/campaign_form.html', context)


@login_required
def campaign_detail(request, campaign_id):
    """Ver detalles de una campaña"""
    campaign = get_object_or_404(
        PromotionCampaign,
        id=campaign_id,
        organization=request.organization
    )
    
    # Estadísticas de mensajes
    messages_stats = {
        'pending': campaign.messages.filter(status='pending').count(),
        'sent': campaign.messages.filter(status='sent').count(),
        'failed': campaign.messages.filter(status='failed').count(),
    }
    
    # Últimos mensajes
    recent_messages = campaign.messages.select_related('patient').order_by('-created_at')[:20]
    
    context = {
        'campaign': campaign,
        'messages_stats': messages_stats,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'promotions/campaign_detail.html', context)


@login_required
def campaign_start(request, campaign_id):
    """Iniciar una campaña"""
    if request.method == 'POST':
        try:
            success = start_campaign(campaign_id)
            
            if success:
                messages.success(request, '🚀 Campaña iniciada. Los mensajes se enviarán gradualmente.')
            else:
                messages.error(request, '❌ No se pudo iniciar la campaña')
                
        except Exception as e:
            messages.error(request, f'❌ Error: {e}')
            logger.error(f"Error iniciando campaña: {e}")
    
    return redirect(f'/dashboard/promociones/campanas/{campaign_id}/')


@login_required
def campaign_pause(request, campaign_id):
    """Pausar una campaña"""
    campaign = get_object_or_404(
        PromotionCampaign,
        id=campaign_id,
        organization=request.organization
    )
    
    if request.method == 'POST':
        campaign.status = 'paused'
        campaign.save()
        messages.success(request, '⏸️ Campaña pausada')
    
    return redirect(f'/dashboard/promociones/campanas/{campaign_id}/')


@login_required
def campaign_resume(request, campaign_id):
    """Reanudar una campaña pausada"""
    campaign = get_object_or_404(
        PromotionCampaign,
        id=campaign_id,
        organization=request.organization
    )
    
    if request.method == 'POST':
        campaign.status = 'in_progress'
        campaign.save()
        messages.success(request, '▶️ Campaña reanudada')
    
    return redirect(f'/dashboard/promociones/campanas/{campaign_id}/')


@login_required
def campaign_stats_json(request, campaign_id):
    """API para estadísticas en tiempo real"""
    campaign = get_object_or_404(
        PromotionCampaign,
        id=campaign_id,
        organization=request.organization
    )
    
    # Actualizar stats
    campaign.update_stats()
    
    data = {
        'status': campaign.status,
        'total_recipients': campaign.total_recipients,
        'messages_sent': campaign.messages_sent,
        'messages_failed': campaign.messages_failed,
        'messages_pending': campaign.messages_pending,
        'progress_percent': round((campaign.messages_sent / campaign.total_recipients * 100) if campaign.total_recipients > 0 else 0, 1),
    }
    
    return JsonResponse(data)


@login_required
def campaign_send_batch(request, campaign_id):
    """Enviar un lote manualmente"""
    campaign = get_object_or_404(
        PromotionCampaign,
        id=campaign_id,
        organization=request.organization
    )
    
    if request.method == 'POST':
        try:
            sender = CampaignSender(campaign)
            sent = sender.process_batch()
            
            messages.success(request, f'✅ Lote procesado: {sent} mensajes enviados')
            
        except Exception as e:
            messages.error(request, f'❌ Error: {e}')
            logger.error(f"Error enviando lote: {e}")
    
    return redirect(f'/dashboard/promociones/campanas/{campaign_id}/')


@login_required
def campaign_delete(request, campaign_id):
    """Eliminar una campaña"""
    campaign = get_object_or_404(
        PromotionCampaign,
        id=campaign_id,
        organization=request.organization
    )
    
    if request.method == 'POST':
        campaign_name = campaign.name
        campaign.delete()
        messages.success(request, f'🗑️ Campaña "{campaign_name}" eliminada correctamente')
        return redirect('/dashboard/promociones/campanas/')
    
    return redirect(f'/dashboard/promociones/campanas/{campaign_id}/')
