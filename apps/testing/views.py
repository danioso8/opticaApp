"""
Vistas para el Bot de Testing en SaaS Admin
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import TestBot, TestRun, TestResult
from .services import TestBotService
from apps.organizations.models import Organization


@login_required
def test_bot_list(request):
    """
    Lista de bots de testing
    """
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta sección")
        return redirect('dashboard:home')
    
    bots = TestBot.objects.all().select_related('organization', 'created_by')
    
    context = {
        'bots': bots,
        'title': 'Bots de Testing Automatizado'
    }
    
    return render(request, 'testing/bot_list.html', context)


@login_required
def test_bot_create(request):
    """
    Crear nuevo bot de testing
    """
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos")
        return redirect('testing:bot_list')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            test_type = request.POST.get('test_type')
            frequency = request.POST.get('frequency')
            org_id = request.POST.get('organization')
            
            # Crear bot
            bot = TestBot.objects.create(
                name=name,
                description=description,
                test_type=test_type,
                frequency=frequency,
                organization_id=org_id if org_id else None,
                created_by=request.user
            )
            
            messages.success(request, f"Bot '{name}' creado exitosamente")
            return redirect('testing:bot_detail', bot_id=bot.id)
            
        except Exception as e:
            messages.error(request, f"Error creando bot: {str(e)}")
    
    organizations = Organization.objects.filter(is_active=True)
    
    context = {
        'organizations': organizations,
        'title': 'Crear Bot de Testing'
    }
    
    return render(request, 'testing/bot_form.html', context)


@login_required
def test_bot_detail(request, bot_id):
    """
    Detalle del bot y sus ejecuciones
    """
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos")
        return redirect('dashboard:home')
    
    bot = get_object_or_404(TestBot, id=bot_id)
    runs = bot.runs.all()[:10]  # Últimas 10 ejecuciones
    
    context = {
        'bot': bot,
        'runs': runs,
        'title': f'Bot: {bot.name}'
    }
    
    return render(request, 'testing/bot_detail.html', context)


@login_required
def test_bot_run(request, bot_id):
    """
    Ejecutar un bot manualmente
    """
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'No tienes permisos'})
    
    bot = get_object_or_404(TestBot, id=bot_id)
    
    try:
        # Ejecutar test
        service = TestBotService(bot)
        test_run = service.run_test()
        
        return JsonResponse({
            'success': True,
            'message': 'Test ejecutado exitosamente',
            'errors_found': test_run.errors_found,
            'run_id': test_run.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def test_run_detail(request, run_id):
    """
    Detalle de una ejecución específica
    """
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos")
        return redirect('dashboard:home')
    
    run = get_object_or_404(TestRun, id=run_id)
    results = run.test_results.all()
    
    context = {
        'run': run,
        'results': results,
        'title': f'Ejecución: {run.test_bot.name}'
    }
    
    return render(request, 'testing/run_detail.html', context)


@login_required
def test_bot_toggle(request, bot_id):
    """
    Activar/desactivar bot
    """
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'No tienes permisos'})
    
    bot = get_object_or_404(TestBot, id=bot_id)
    bot.is_active = not bot.is_active
    bot.save()
    
    return JsonResponse({
        'success': True,
        'is_active': bot.is_active
    })
