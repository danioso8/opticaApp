"""
Vistas para AR Virtual Try-On
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg
from django.core.files.base import ContentFile
import base64
import json

from .models_ar_tryon import (
    FrameCategory,
    Frame,
    VirtualTryOnSession,
    FrameTryOnRecord,
    FaceShapeRecommendation
)
from apps.patients.models import Patient


@login_required
def ar_tryon_home(request):
    """Vista principal del AR Virtual Try-On"""
    if not request.organization:
        return redirect('dashboard:home')
    
    # Obtener categorías y monturas destacadas
    categories = FrameCategory.objects.filter(
        organization=request.organization,
        is_active=True
    )
    
    featured_frames = Frame.objects.filter(
        organization=request.organization,
        is_active=True,
        is_featured=True
    )[:8]
    
    # Estadísticas
    stats = {
        'total_frames': Frame.objects.filter(organization=request.organization, is_active=True).count(),
        'total_sessions': VirtualTryOnSession.objects.filter(organization=request.organization).count(),
        'total_categories': categories.count(),
    }
    
    context = {
        'categories': categories,
        'featured_frames': featured_frames,
        'stats': stats,
    }
    
    return render(request, 'dashboard/ar_tryon/home.html', context)


@login_required
def ar_tryon_camera(request):
    """Vista de la cámara para prueba virtual"""
    if not request.organization:
        return redirect('dashboard:home')
    
    # Crear sesión
    patient_id = request.GET.get('patient_id')
    patient = None
    
    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id, organization=request.organization)
    
    session = VirtualTryOnSession.objects.create(
        organization=request.organization,
        patient=patient
    )
    
    # Obtener todas las monturas disponibles
    frames = Frame.objects.filter(
        organization=request.organization,
        is_active=True
    ).select_related('category')
    
    # Agrupar por categoría
    frames_by_category = {}
    for frame in frames:
        category_name = frame.category.name
        if category_name not in frames_by_category:
            frames_by_category[category_name] = []
        frames_by_category[category_name].append(frame)
    
    context = {
        'session': session,
        'patient': patient,
        'frames': frames,
        'frames_by_category': frames_by_category,
        'categories': FrameCategory.objects.filter(organization=request.organization, is_active=True),
    }
    
    return render(request, 'dashboard/ar_tryon/camera.html', context)


@login_required
def ar_tryon_catalog(request):
    """Catálogo de monturas"""
    if not request.organization:
        return redirect('dashboard:home')
    
    # Filtros
    category_id = request.GET.get('category')
    gender = request.GET.get('gender')
    search = request.GET.get('search')
    
    frames = Frame.objects.filter(
        organization=request.organization,
        is_active=True
    ).select_related('category')
    
    if category_id:
        frames = frames.filter(category_id=category_id)
    
    if gender:
        frames = frames.filter(gender=gender)
    
    if search:
        frames = frames.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(brand__icontains=search)
        )
    
    categories = FrameCategory.objects.filter(
        organization=request.organization,
        is_active=True
    )
    
    context = {
        'frames': frames,
        'categories': categories,
        'selected_category': category_id,
        'selected_gender': gender,
        'search_query': search,
    }
    
    return render(request, 'dashboard/ar_tryon/catalog.html', context)


@login_required
@require_http_methods(["POST"])
def api_record_try_on(request):
    """API para registrar una prueba de montura"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        frame_id = data.get('frame_id')
        
        session = get_object_or_404(VirtualTryOnSession, id=session_id, organization=request.organization)
        frame = get_object_or_404(Frame, id=frame_id, organization=request.organization)
        
        # Crear registro
        record = FrameTryOnRecord.objects.create(
            session=session,
            frame=frame
        )
        
        # Incrementar contador de la montura
        frame.increment_try_on()
        
        return JsonResponse({
            'success': True,
            'record_id': record.id,
            'message': f'Prueba registrada: {frame.name}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_save_photo(request):
    """API para guardar foto con montura"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    try:
        data = json.loads(request.body)
        record_id = data.get('record_id')
        photo_data = data.get('photo')  # Base64 encoded
        
        record = get_object_or_404(FrameTryOnRecord, id=record_id, session__organization=request.organization)
        
        # Decodificar imagen base64
        if photo_data and 'base64,' in photo_data:
            format, imgstr = photo_data.split('base64,')
            ext = format.split('/')[-1].split(';')[0]
            
            photo_file = ContentFile(base64.b64decode(imgstr), name=f'tryon_{record_id}.{ext}')
            record.photo = photo_file
            record.save()
            
            return JsonResponse({
                'success': True,
                'photo_url': record.photo.url,
                'message': 'Foto guardada exitosamente'
            })
        
        return JsonResponse({'error': 'No photo data'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_rate_frame(request):
    """API para calificar una montura"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    try:
        data = json.loads(request.body)
        record_id = data.get('record_id')
        rating = data.get('rating')
        is_favorite = data.get('is_favorite', False)
        
        record = get_object_or_404(FrameTryOnRecord, id=record_id, session__organization=request.organization)
        
        if rating:
            record.rating = rating
        
        if is_favorite:
            record.is_favorite = True
            record.frame.favorite_count += 1
            record.frame.save(update_fields=['favorite_count'])
        
        record.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Calificación guardada'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_frame_details(request, frame_id):
    """API para obtener detalles de una montura"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    frame = get_object_or_404(Frame, id=frame_id, organization=request.organization)
    
    # Parsear anchor points si existen
    anchor_points = {}
    if frame.anchor_points:
        try:
            anchor_points = json.loads(frame.anchor_points)
        except:
            pass
    
    data = {
        'id': frame.id,
        'code': frame.code,
        'name': frame.name,
        'brand': frame.brand,
        'color': frame.color,
        'material': frame.get_material_display(),
        'gender': frame.get_gender_display(),
        'description': frame.description,
        'price': float(frame.price),
        'stock': frame.stock,
        'dimensions': {
            'lens_width': frame.lens_width,
            'bridge_width': frame.bridge_width,
            'temple_length': frame.temple_length,
            'total_width': frame.total_width,
        },
        'images': {
            'front': frame.front_image.url,
            'side': frame.side_image.url if frame.side_image else None,
            'overlay': frame.overlay_image.url if frame.overlay_image else None,
        },
        'anchor_points': anchor_points,
        'recommended_face_shapes': frame.recommended_face_shapes.split(',') if frame.recommended_face_shapes else [],
        'analytics': {
            'try_on_count': frame.try_on_count,
            'favorite_count': frame.favorite_count,
        }
    }
    
    return JsonResponse(data)


@login_required
def api_detect_face_shape(request):
    """API para detectar forma de rostro (placeholder)"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    # TODO: Implementar detección real con face-api.js
    # Por ahora retornamos un resultado simulado
    
    return JsonResponse({
        'success': True,
        'face_shape': 'oval',
        'confidence': 0.85,
        'measurements': {
            'face_width': 140,
            'face_height': 180,
            'eye_distance': 65,
        },
        'recommendations': [
            'Monturas rectangulares',
            'Monturas cuadradas',
            'Casi cualquier estilo te queda bien'
        ]
    })


@login_required
def ar_tryon_sessions(request):
    """Vista de historial de sesiones"""
    if not request.organization:
        return redirect('dashboard:home')
    
    sessions = VirtualTryOnSession.objects.filter(
        organization=request.organization
    ).select_related('patient').prefetch_related('try_records__frame').order_by('-created_at')
    
    # Stats
    total_sessions = sessions.count()
    avg_frames_per_session = sessions.annotate(
        frames_count=Count('try_records')
    ).aggregate(avg=Avg('frames_count'))['avg'] or 0
    
    context = {
        'sessions': sessions,
        'total_sessions': total_sessions,
        'avg_frames_per_session': round(avg_frames_per_session, 1),
    }
    
    return render(request, 'dashboard/ar_tryon/sessions.html', context)


@login_required
def ar_tryon_session_detail(request, session_id):
    """Detalle de una sesión"""
    if not request.organization:
        return redirect('dashboard:home')
    
    session = get_object_or_404(
        VirtualTryOnSession,
        id=session_id,
        organization=request.organization
    )
    
    records = session.try_records.select_related('frame').order_by('-tried_at')
    
    context = {
        'session': session,
        'records': records,
    }
    
    return render(request, 'dashboard/ar_tryon/session_detail.html', context)
