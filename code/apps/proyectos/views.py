from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json

from apps.proyectos.models import Proyecto, ProyectoMetodologia, Sprint, Tarea
from apps.commons.models import Estado, Metodologias, Rol, Prioridad
from apps.empresas.models import Empresa, Empresa_Proyecto
from apps.autenticacion.models import Usuario

@never_cache
@login_required
def lista_proyectos(request):
    proyectos = Proyecto.objects.all().order_by('-creacion')
    
    # Contar sprints por proyecto
    proyectos_datos = []
    for proyecto in proyectos:
        sprints = Sprint.objects.filter(proyecto=proyecto)
        proyectos_datos.append({
            'proyecto': proyecto,
            'sprints_activos': sprints.filter(estado__nombre__icontains='activo').count(),
            'total_sprints': sprints.count()
        })
    
    context = {
        'proyectos_datos': proyectos_datos,
        'total_proyectos': proyectos.count()
    }
    
    return render(request, 'proyectos/lista_proyectos.html', context)

@never_cache
@login_required
def crear_proyecto(request):
    metodologias = Metodologias.objects.all()
    estados = Estado.objects.all()  # Todos los estados por ahora
    prioridades = Prioridad.objects.all()

    if request.method == "POST":
        # Datos del proyecto
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        estado_id = request.POST.get("estado")
        metodologia_id = request.POST.get("metodologia")

        if not nombre or not estado_id or not metodologia_id:
            messages.error(request, "Todos los campos obligatorios deben ser completados.")
            return redirect('proyectos:crear_proyecto')

        # Crear proyecto
        proyecto = Proyecto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            estado_id=estado_id
        )

        # Guardar metodología del proyecto
        ProyectoMetodologia.objects.create(
            proyecto=proyecto,
            metodologia_id=metodologia_id
        )

        # Procesar sprints si existen
        sprints_nombres = request.POST.getlist('sprint_nombre[]')
        sprints_descripciones = request.POST.getlist('sprint_descripcion[]')
        sprints_inicio = request.POST.getlist('sprint_inicio[]')
        sprints_fin = request.POST.getlist('sprint_fin[]')
        sprints_estado = request.POST.getlist('sprint_estado[]')

        sprints_creados = []
        for i in range(len(sprints_nombres)):
            if sprints_nombres[i] and sprints_inicio[i] and sprints_fin[i]:
                sprint = Sprint.objects.create(
                    nombre=sprints_nombres[i],
                    descripcion=sprints_descripciones[i] if i < len(sprints_descripciones) else '',
                    fecha_inicio=sprints_inicio[i],
                    fecha_fin=sprints_fin[i],
                    estado_id=sprints_estado[i] if i < len(sprints_estado) and sprints_estado[i] else None,
                    proyecto=proyecto
                )
                sprints_creados.append(sprint)

        # Procesar tareas si existen
        tareas_nombres = request.POST.getlist('tarea_nombre[]')
        tareas_descripciones = request.POST.getlist('tarea_descripcion[]')
        tareas_estado = request.POST.getlist('tarea_estado[]')
        tareas_prioridad = request.POST.getlist('tarea_prioridad[]')
        tareas_sprint = request.POST.getlist('tarea_sprint[]')

        for i in range(len(tareas_nombres)):
            if tareas_nombres[i] and i < len(tareas_estado) and tareas_estado[i]:
                # Mapear índice de sprint a sprint real
                sprint_idx = int(tareas_sprint[i]) if i < len(tareas_sprint) and tareas_sprint[i].isdigit() else None
                sprint_obj = sprints_creados[sprint_idx] if sprint_idx is not None and sprint_idx < len(sprints_creados) else None

                Tarea.objects.create(
                    nombre=tareas_nombres[i],
                    descripcion=tareas_descripciones[i] if i < len(tareas_descripciones) else '',
                    estado_id=tareas_estado[i],
                    prioridad_id=tareas_prioridad[i] if i < len(tareas_prioridad) and tareas_prioridad[i] else None,
                    sprint=sprint_obj,
                    proyecto=proyecto
                )

        messages.success(request, f"Proyecto '{proyecto.nombre}' creado correctamente.")
        return redirect('proyectos:detalle_proyecto', id=proyecto.id)

    return render(request, 'proyectos/crear_proyecto.html', {
        'metodologias': metodologias,
        'estados': estados,
        'prioridades': prioridades
    })

@never_cache
@login_required
def detalle_proyecto(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    sprints = Sprint.objects.filter(proyecto=proyecto).order_by('-fecha_inicio')
    tareas = Tarea.objects.filter(proyecto=proyecto).order_by('-creacion')
    miembros = Empresa_Proyecto.objects.filter(proyecto=proyecto)
    metodologias_proyecto = ProyectoMetodologia.objects.filter(proyecto=proyecto)
    
    # Datos para los modales
    metodologias = Metodologias.objects.all()
    empresas = Empresa.objects.all()
    usuarios = Usuario.objects.all()
    estados = Estado.objects.all()  # Todos los estados
    prioridades = Prioridad.objects.all()
    
    # Verificar si la metodología permite sprints
    proyecto_metodologia = ProyectoMetodologia.objects.filter(proyecto=proyecto).first()
    permite_sprints = False
    if proyecto_metodologia:
        metodologia_nombre = proyecto_metodologia.metodologia.nombre.lower()
        permite_sprints = metodologia_nombre in ["scrum", "xp", "agile", "scrumban"]
    
    context = {
        'proyecto': proyecto,
        'sprints': sprints,
        'tareas': tareas,
        'miembros': miembros,
        'metodologias_proyecto': metodologias_proyecto,
        'total_sprints': sprints.count(),
        'total_tareas': tareas.count(),
        'permite_sprints': permite_sprints,
        # Para modales
        'metodologias': metodologias,
        'empresas': empresas,
        'usuarios': usuarios,
        'estados': estados,
        'prioridades': prioridades,
    }
    
    return render(request, 'proyectos/detalle_proyecto.html', context)

@require_POST
@login_required
def agregar_miembro(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    empresa_id = request.POST.get("empresa")
    usuario_id = request.POST.get("usuario")

    if not empresa_id or not usuario_id:
        messages.error(request, "Debe seleccionar empresa y usuario.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)

    # Verificar si ya existe
    if Empresa_Proyecto.objects.filter(
        proyecto=proyecto, 
        empresa_id=empresa_id, 
        usuario_id=usuario_id
    ).exists():
        messages.warning(request, "Este miembro ya está en el proyecto.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)

    Empresa_Proyecto.objects.create(
        proyecto=proyecto,
        empresa_id=empresa_id,
        usuario_id=usuario_id
    )

    messages.success(request, "Miembro agregado correctamente.")
    return redirect('proyectos:detalle_proyecto', id=proyecto_id)

@require_POST
@login_required
def crear_sprint(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Verificar si la metodología permite sprints
    proyecto_metodologia = ProyectoMetodologia.objects.filter(proyecto=proyecto).first()
    if not proyecto_metodologia:
        messages.error(request, "Este proyecto no tiene metodología asignada.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)
    
    metodologia_nombre = proyecto_metodologia.metodologia.nombre.lower()
    if metodologia_nombre not in ["scrum", "xp", "agile", "scrumban"]:
        messages.error(request, "La metodología de este proyecto no permite sprints.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)

    nombre = request.POST.get("nombre")
    descripcion = request.POST.get("descripcion")
    fecha_inicio = request.POST.get("fecha_inicio")
    fecha_fin = request.POST.get("fecha_fin")
    estado_id = request.POST.get("estado")

    if not nombre or not fecha_inicio or not fecha_fin:
        messages.error(request, "Debe completar todos los campos obligatorios.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)

    Sprint.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado_id=estado_id if estado_id else None,
        proyecto=proyecto
    )

    messages.success(request, "Sprint creado correctamente.")
    return redirect('proyectos:detalle_proyecto', id=proyecto_id)

@require_POST
@login_required
def crear_tarea(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    nombre = request.POST.get("nombre")
    descripcion = request.POST.get("descripcion")
    estado_id = request.POST.get("estado")
    prioridad_id = request.POST.get("prioridad")
    sprint_id = request.POST.get("sprint")

    if not nombre or not estado_id:
        messages.error(request, "Debe completar todos los campos obligatorios.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)

    Tarea.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        estado_id=estado_id,
        prioridad_id=prioridad_id if prioridad_id else None,
        sprint_id=sprint_id if sprint_id else None,
        proyecto=proyecto
    )

    messages.success(request, "Tarea creada correctamente.")
    return redirect('proyectos:detalle_proyecto', id=proyecto_id)

@require_POST
@login_required
def agregar_metodologia(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    metodologia_id = request.POST.get("metodologia")

    if not metodologia_id:
        messages.error(request, "Debe seleccionar una metodología.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)

    # Verificar si ya existe
    if ProyectoMetodologia.objects.filter(proyecto=proyecto, metodologia_id=metodologia_id).exists():
        messages.warning(request, "Esta metodología ya está asignada al proyecto.")
        return redirect('proyectos:detalle_proyecto', id=proyecto_id)

    ProyectoMetodologia.objects.create(
        proyecto=proyecto,
        metodologia_id=metodologia_id
    )

    messages.success(request, "Metodología agregada correctamente.")
    return redirect('proyectos:detalle_proyecto', id=proyecto_id)