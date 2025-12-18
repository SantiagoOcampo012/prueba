from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from .models import Bug, ComentarioBug
from .forms import BugForm, ComentarioBugForm
from apps.proyectos.models import Proyecto, Sprint
from apps.commons.models import Estado, Prioridad


@login_required
def lista_bugs(request):
    """Vista para listar todos los bugs"""
    bugs = Bug.objects.select_related(
        'proyecto', 'sprint', 'estado', 'prioridad', 'severidad',
        'reportado_por', 'asignado_a'
    ).order_by('-creacion')
    
    # Filtros opcionales
    proyecto_id = request.GET.get('proyecto')
    estado_id = request.GET.get('estado')
    prioridad_id = request.GET.get('prioridad')
    
    if proyecto_id:
        bugs = bugs.filter(proyecto_id=proyecto_id)
    if estado_id:
        bugs = bugs.filter(estado_id=estado_id)
    if prioridad_id:
        bugs = bugs.filter(prioridad_id=prioridad_id)
    
    # Para los filtros en el template
    proyectos = Proyecto.objects.all()
    estados = Estado.objects.all()
    # Filtrar prioridades para mostrar solo: Baja, Media, Alta, Crítica
    prioridades = Prioridad.objects.filter(
        nombre__in=['Baja', 'Media', 'Alta', 'Crítica']
    )
    
    # Importar Sprint desde el modelo correcto
    from apps.proyectos.models import Sprint
    sprints = Sprint.objects.select_related('proyecto').all()
    
    context = {
        'bugs': bugs,
        'proyectos': proyectos,
        'estados': estados,
        'prioridades': prioridades,
        'sprints': sprints,
        'form': BugForm(),
    }
    return render(request, 'bugtracker/lista_bugs.html', context)


@login_required
def crear_bug(request):
    """Vista para crear un nuevo bug"""
    if request.method == 'POST':
        form = BugForm(request.POST, request.FILES)
        if form.is_valid():
            bug = form.save(commit=False)
            bug.reportado_por = request.user
            bug.save()
            messages.success(request, f'Bug "{bug.titulo}" creado exitosamente.')
            return redirect('bugtracker:lista_bugs')
        else:
            messages.error(request, 'Error al crear el bug. Verifica los campos.')
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('bugtracker:lista_bugs')


@login_required
def editar_bug(request, bug_id):
    """Vista para editar un bug existente"""
    bug = get_object_or_404(Bug, id=bug_id)
    
    if request.method == 'POST':
        form = BugForm(request.POST, request.FILES, instance=bug)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bug "{bug.titulo}" actualizado exitosamente.')
            return redirect('bugtracker:detalle_bug', bug_id=bug.id)
        else:
            messages.error(request, 'Error al actualizar el bug.')
    
    return redirect('bugtracker:lista_bugs')


@login_required
def eliminar_bug(request, bug_id):
    """
    Vista DESHABILITADA - Los bugs no se deben eliminar
    Se mantiene por compatibilidad pero redirige a la lista
    """
    messages.warning(request, 'Los bugs no se pueden eliminar. Use la opción de revisión en su lugar.')
    return redirect('bugtracker:lista_bugs')


@login_required
def detalle_bug(request, bug_id):
    """Vista para ver el detalle de un bug y sus comentarios"""
    bug = get_object_or_404(
        Bug.objects.select_related(
            'proyecto', 'sprint', 'estado', 'prioridad', 'severidad',
            'reportado_por', 'asignado_a', 'archivo'
        ),
        id=bug_id
    )
    
    comentarios = ComentarioBug.objects.filter(bug=bug).select_related(
        'usuario', 'archivo'
    ).order_by('-creacion')
    
    context = {
        'bug': bug,
        'comentarios': comentarios,
        'form_bug': BugForm(instance=bug),
        'form_comentario': ComentarioBugForm(),
    }
    return render(request, 'bugtracker/detalle_bug.html', context)


@login_required
def agregar_comentario(request, bug_id):
    """Vista para agregar un comentario a un bug"""
    bug = get_object_or_404(Bug, id=bug_id)
    
    if request.method == 'POST':
        form = ComentarioBugForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.bug = bug
            comentario.usuario = request.user
            comentario.save()
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'Error al agregar el comentario.')
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('bugtracker:detalle_bug', bug_id=bug.id)


@login_required
def editar_comentario(request, comentario_id):
    """Vista para editar un comentario (solo el propietario)"""
    comentario = get_object_or_404(ComentarioBug, id=comentario_id)
    
    # Verificar que el usuario sea el propietario del comentario
    if comentario.usuario != request.user:
        messages.error(request, 'No tienes permiso para editar este comentario.')
        return redirect('bugtracker:detalle_bug', bug_id=comentario.bug.id)
    
    if request.method == 'POST':
        form = ComentarioBugForm(request.POST, request.FILES, instance=comentario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentario actualizado exitosamente.')
        else:
            messages.error(request, 'Error al actualizar el comentario.')
    
    return redirect('bugtracker:detalle_bug', bug_id=comentario.bug.id)


@login_required
def eliminar_comentario(request, comentario_id):
    """Vista para eliminar un comentario (solo el propietario)"""
    comentario = get_object_or_404(ComentarioBug, id=comentario_id)
    
    # Verificar que el usuario sea el propietario del comentario
    if comentario.usuario != request.user:
        messages.error(request, 'No tienes permiso para eliminar este comentario.')
        return redirect('bugtracker:detalle_bug', bug_id=comentario.bug.id)
    
    if request.method == 'POST':
        bug_id = comentario.bug.id
        comentario.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect('bugtracker:detalle_bug', bug_id=bug_id)
    
    return redirect('bugtracker:detalle_bug', bug_id=comentario.bug.id)


@login_required
def solicitar_revision(request, bug_id):
    """
    Vista para solicitar revisión de un bug
    
    TODO: Integrar con sistema de notificaciones
    - Enviar notificación al equipo de QA
    - Enviar email al asignado
    - Notificar a los administradores del proyecto
    """
    bug = get_object_or_404(Bug, id=bug_id)
    
    if request.method == 'POST':
        # Obtener el estado "En Revisión" o el que corresponda
        try:
            estado_revision = Estado.objects.get(nombre__icontains='revisión')
            bug.estado = estado_revision
            bug.save()
            
            # Crear un comentario automático
            ComentarioBug.objects.create(
                bug=bug,
                usuario=request.user,
                comentario=f'{request.user.nick} ha solicitado revisión de este bug.'
            )
            
            # TODO: INTEGRACIÓN CON NOTIFICACIONES
            # Aquí se debe implementar la lógica de notificaciones:
            # 1. Notificar al usuario asignado (si existe)
            # 2. Notificar al equipo de revisión/QA
            # 3. Enviar email de notificación
            # 4. Crear registro en el sistema de notificaciones
            # 
            # Ejemplo de implementación futura:
            # from apps.notificaciones.utils import enviar_notificacion_revision
            # enviar_notificacion_revision(bug, request.user)
            
            messages.success(request, 'Solicitud de revisión enviada exitosamente.')
        except Estado.DoesNotExist:
            messages.error(request, 'No se encontró el estado de revisión. Contacta al administrador.')
    
    return redirect('bugtracker:detalle_bug', bug_id=bug.id)