from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Count
from django.urls import reverse

from apps.commons.models import Extension, File
from .models import TestSuite, Entorno, CasoPrueba, EjecucionPrueba
from .forms import TestSuiteForm, EntornoForm, CasoPruebaForm, EjecucionPruebaForm
from django.http import FileResponse, Http404
from django.conf import settings
import os

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
import os

from apps.commons.models import File 


@login_required
def lista_testsuites(request):
    testsuites = TestSuite.objects.all().select_related('proyecto')
    form = TestSuiteForm()
    testsuite_editar = None
    
    if 'editar' in request.GET:
        testsuite_editar = get_object_or_404(TestSuite, pk=request.GET['editar'])
        form = TestSuiteForm(instance=testsuite_editar)
    
    context = {
        'testsuites': testsuites,
        'form': form,
        'testsuite_editar': testsuite_editar
    }
    return render(request, 'testsuite/testsuites.html', context)


@login_required
def crear_testsuite(request):
    if request.method == 'POST':
        form = TestSuiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test Suite creado exitosamente.')
            return redirect('testsuite:lista_testsuites')
    return redirect('testsuite:lista_testsuites')


@login_required
def editar_testsuite(request, pk):
    testsuite = get_object_or_404(TestSuite, pk=pk)
    
    if request.method == 'POST':
        form = TestSuiteForm(request.POST, instance=testsuite)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test Suite actualizado exitosamente.')
            return redirect('testsuite:lista_testsuites')
    
    return redirect(f"{request.path.split('/editar')[0]}?editar={pk}")


@login_required
def eliminar_testsuite(request, pk):
    if request.method == 'POST':
        testsuite = get_object_or_404(TestSuite, pk=pk)
        testsuite.delete()
        messages.success(request, 'Test Suite eliminado exitosamente.')
    return redirect('testsuite:lista_testsuites')


@login_required
def detalle_testsuite(request, pk):
    testsuite = get_object_or_404(TestSuite, pk=pk)
    casos_prueba = CasoPrueba.objects.filter(test_suite=testsuite).select_related('estado', 'entorno').annotate(
        num_ejecuciones=Count('ejecucionprueba')
    )
    form_caso = CasoPruebaForm(initial={'test_suite': testsuite})
    
    context = {
        'testsuite': testsuite,
        'casos': casos_prueba,
        'form': form_caso,
    }
    return render(request, 'testsuite/detalle_testsuite.html', context)


@login_required
def lista_casos_prueba(request):
    casos = CasoPrueba.objects.all().select_related('test_suite', 'estado', 'entorno')
    form = CasoPruebaForm()
    caso_editar = None
    
    if 'editar' in request.GET:
        caso_editar = get_object_or_404(CasoPrueba, pk=request.GET['editar'])
        form = CasoPruebaForm(instance=caso_editar)
    
    context = {
        'casos': casos,
        'form': form,
        'caso_editar': caso_editar
    }
    return render(request, 'testsuite/casos_prueba.html', context)


@login_required
def crear_caso_prueba(request):
    if request.method == 'POST':
        form = CasoPruebaForm(request.POST)
        if form.is_valid():
            caso = form.save()
            messages.success(request, 'Caso de Prueba creado exitosamente.')
            if 'testsuite_id' in request.POST:
                return redirect('testsuite:detalle_testsuite', pk=request.POST['testsuite_id'])
            return redirect('testsuite:lista_casos')
    return redirect('testsuite:lista_casos')


@login_required
def editar_caso_prueba(request, pk):
    caso = get_object_or_404(CasoPrueba, pk=pk)
    
    if request.method == 'POST':
        form = CasoPruebaForm(request.POST, instance=caso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Caso de Prueba actualizado exitosamente.')
            if 'testsuite_id' in request.POST:
                return redirect('testsuite:detalle_testsuite', pk=request.POST['testsuite_id'])
            return redirect('testsuite:lista_casos')
    
    return redirect(f"/testsuite/casos-prueba/?editar={pk}")


@login_required
def eliminar_caso_prueba(request, pk):
    if request.method == 'POST':
        caso = get_object_or_404(CasoPrueba, pk=pk)
        testsuite_id = caso.test_suite.id if caso.test_suite else None
        caso.delete()
        messages.success(request, 'Caso de Prueba eliminado exitosamente.')
        if 'testsuite_id' in request.POST and testsuite_id:
            return redirect('testsuite:detalle_testsuite', pk=testsuite_id)
    return redirect('testsuite:lista_casos')


@login_required
def detalle_caso_prueba(request, pk):
    caso = get_object_or_404(CasoPrueba, pk=pk)
    ejecuciones = EjecucionPrueba.objects.filter(caso_prueba=caso).select_related('ejecutado_por', 'estado')
    form_ejecucion = EjecucionPruebaForm(initial={'caso_prueba': caso})
    
    context = {
        'caso': caso,
        'ejecuciones': ejecuciones,
        'form': form_ejecucion,
    }
    return render(request, 'testsuite/detalle_caso_prueba.html', context)


@login_required
def lista_ejecuciones(request):
    ejecuciones = EjecucionPrueba.objects.all().select_related(
        'caso_prueba', 'ejecutado_por', 'estado'
    )
    form = EjecucionPruebaForm()
    ejecucion_editar = None
    
    if 'editar' in request.GET:
        ejecucion_editar = get_object_or_404(EjecucionPrueba, pk=request.GET['editar'])
        form = EjecucionPruebaForm(instance=ejecucion_editar)
    
    context = {
        'ejecuciones': ejecuciones,
        'form': form,
        'ejecucion_editar': ejecucion_editar
    }
    return render(request, 'testsuite/ejecuciones_prueba.html', context)


@login_required
def crear_ejecucion(request):
    if request.method == "POST":
        caso_id = request.POST.get("caso_prueba")
        caso = CasoPrueba.objects.get(pk=caso_id)

        archivo_subido = request.FILES.get("archivo_upload")
        archivo_obj = None

        if archivo_subido:
            # Guardar el archivo en File.ruta
            archivo_obj = File.objects.create(
                ruta=archivo_subido
            )

        ejecucion = EjecucionPrueba.objects.create(
            caso_prueba=caso,
            ejecutado_por=request.user,
            estado_id=request.POST.get("estado"),
            resultado=request.POST.get("resultado"),
            observaciones=request.POST.get("observaciones"),
            archivo=archivo_obj
        )

        return redirect("testsuite:detalle_caso_prueba", caso.pk)


@login_required
def editar_ejecucion(request, pk):
    ejecucion = get_object_or_404(EjecucionPrueba, pk=pk)

    if request.method == 'POST':
        archivo_upload = request.FILES.get('archivo_upload')

        if archivo_upload:
            # Eliminar archivo anterior si existe
            if ejecucion.archivo:
                try:
                    if ejecucion.archivo.ruta:
                        ejecucion.archivo.ruta.delete()
                    ejecucion.archivo.delete()
                except:
                    pass

            # Crear nuevo File
            archivo_obj = File.objects.create(
                ruta=archivo_upload
            )
            ejecucion.archivo = archivo_obj

        # Actualizar campos restantes
        ejecucion.estado_id = request.POST.get("estado")
        ejecucion.resultado = request.POST.get("resultado")
        ejecucion.observaciones = request.POST.get("observaciones")
        ejecucion.save()

        return redirect("testsuite:detalle_caso_prueba", ejecucion.caso_prueba.pk)


@login_required
def eliminar_ejecucion(request, pk):
    if request.method == 'POST':
        ejecucion = get_object_or_404(EjecucionPrueba, pk=pk)
        caso_id = ejecucion.caso_prueba.id if ejecucion.caso_prueba else None
        ejecucion.delete()
        messages.success(request, 'Ejecución de Prueba eliminada exitosamente.')
        if 'caso_id' in request.POST and caso_id:
            return redirect('testsuite:detalle_caso_prueba', pk=caso_id)
    return redirect('testsuite:lista_ejecuciones')


@login_required
def detalle_ejecucion(request, pk):
    ejecucion = get_object_or_404(EjecucionPrueba, pk=pk)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        
        # -----------------------------
        # SECCIÓN DE ARCHIVO ADJUNTO - SIEMPRE AMBOS BOTONES
        # -----------------------------
        archivo_html = ''

        if ejecucion.archivo and ejecucion.archivo.ruta:
            # Construimos la URL correcta para descargar el archivo
            archivo_nombre = os.path.basename(ejecucion.archivo.ruta.name)
            url_descarga = reverse('testsuite:descargar_archivo', args=[ejecucion.archivo.id])
            archivo_url = ejecucion.archivo.ruta.url
            
            # Determinar extensión
            extension = archivo_nombre.split('.')[-1].lower()

            # SIEMPRE MOSTRAR AMBOS BOTONES (Vista Previa + Descargar)
            botones_html = f"""
                <button onclick="previewFile('{archivo_url}', '{archivo_nombre}')" class="btn-secondary btn-sm">
                    <i class="fas fa-eye"></i> Vista Previa
                </button>
                <a href="{url_descarga}" class="btn-primary btn-sm">
                    <i class="fas fa-download"></i> Descargar
                </a>
            """

            archivo_html = f"""
            <div class="detail-section">
                <h3><i class="fas fa-paperclip"></i> Archivos Adjuntos</h3>
                <div class="file-list">
                    <div class="file-item">
                        <div class="file-icon">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <div class="file-info">
                            <span class="file-name">{archivo_nombre}</span>
                            <span class="file-size text-muted">Tipo: {extension.upper()}</span>
                        </div>
                        <div class="file-actions">
                            {botones_html}
                        </div>
                    </div>
                </div>
            </div>
            """
        else:
            archivo_html = """
            <div class="detail-section">
                <h3><i class="fas fa-paperclip"></i> Archivos Adjuntos</h3>
                <div class="empty-files">
                    <i class="fas fa-folder-open"></i>
                    <p class="text-muted">No hay archivos adjuntos para esta ejecución</p>
                </div>
            </div>
            """

        # -----------------------------
        # CONTENIDO PRINCIPAL DEL MODAL
        # -----------------------------
        html = f"""
        <div class="detalle-info">
            <div class="detail-section">
                <h3><i class="fas fa-info-circle"></i> Información de la Ejecución</h3>
                <div class="info-grid">
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-clipboard-list"></i> Caso de Prueba:</span>
                        <span class="info-value">{ejecucion.caso_prueba.nombre if ejecucion.caso_prueba else 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-user"></i> Ejecutado Por:</span>
                        <span class="info-value">{str(ejecucion.ejecutado_por) if ejecucion.ejecutado_por else 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-tag"></i> Estado:</span>
                        <span class="info-value">
                            <span class="badge badge-{ejecucion.estado.nombre.lower() if ejecucion.estado else 'secondary'}">
                                {ejecucion.estado.nombre if ejecucion.estado else 'N/A'}
                            </span>
                        </span>
                    </div>
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-check-circle"></i> Resultado:</span>
                        <span class="info-value">
                            <span class="badge badge-resultado-{ejecucion.resultado.lower() if ejecucion.resultado else 'pendiente'}">
                                {ejecucion.resultado or 'N/A'}
                            </span>
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3><i class="fas fa-clipboard"></i> Observaciones</h3>
                <div class="observaciones-content">
                    <p>{ejecucion.observaciones or '<em class="text-muted">Sin observaciones registradas</em>'}</p>
                </div>
            </div>
            
            {archivo_html}
        </div>
        """

        return JsonResponse({'html': html})
    
    return redirect('testsuite:lista_ejecuciones')


@login_required
def lista_entornos(request):
    entornos = Entorno.objects.all()
    context = {'entornos': entornos}
    return render(request, 'testsuite/entornos.html', context)


@login_required
def crear_entorno(request):
    if request.method == 'POST':
        form = EntornoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entorno creado exitosamente.')
            return redirect('testsuite:lista_entornos')
    else:
        form = EntornoForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('testsuite/partials/form_entorno.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'testsuite/entornos.html', {'form': form})


@login_required
def editar_entorno(request, pk):
    entorno = get_object_or_404(Entorno, pk=pk)
    
    if request.method == 'POST':
        form = EntornoForm(request.POST, instance=entorno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entorno actualizado exitosamente.')
            return redirect('testsuite:lista_entornos')
    else:
        form = EntornoForm(instance=entorno)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('testsuite/partials/form_entorno.html', 
                               {'form': form, 'entorno': entorno}, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'testsuite/entornos.html', {'form': form, 'entorno': entorno})


@login_required
def eliminar_entorno(request, pk):
    entorno = get_object_or_404(Entorno, pk=pk)
    
    if request.method == 'POST':
        entorno.delete()
        messages.success(request, 'Entorno eliminado exitosamente.')
    return redirect('testsuite:lista_entornos')


@login_required
def descargar_archivo_ejecucion(request, pk):
    ejecucion = get_object_or_404(EjecucionPrueba, pk=pk)

    # Verificamos que tenga archivo
    if not ejecucion.archivo or not ejecucion.archivo.ruta:
        raise Http404("El archivo no existe")

    ruta_fisica = ejecucion.archivo.ruta.path
    nombre_descarga = os.path.basename(ruta_fisica)

    if not os.path.exists(ruta_fisica):
        raise Http404("El archivo no está en el servidor")

    return FileResponse(open(ruta_fisica, 'rb'), as_attachment=True, filename=nombre_descarga)


@login_required
def descargar_archivo(request, pk):
    # Obtener el objeto File
    file_obj = get_object_or_404(File, pk=pk)

    if not file_obj.ruta:
        raise Http404("El archivo no está asociado en la base de datos.")

    file_path = file_obj.ruta.path

    # Validar que el archivo exista en el filesystem
    if not os.path.exists(file_path):
        raise Http404("El archivo no fue encontrado en el servidor.")

    # Leer archivo y responder para descarga
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response