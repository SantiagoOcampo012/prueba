from django import forms
from django.core.exceptions import ValidationError
import re
from .models import TestSuite, CasoPrueba, EjecucionPrueba, Entorno


def validar_texto_seguro(value):
    """Valida que el texto no contenga scripts maliciosos"""
    patrones_peligrosos = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onload\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]
    
    for patron in patrones_peligrosos:
        if re.search(patron, value, re.IGNORECASE):
            raise ValidationError(
                'El texto contiene contenido no permitido. Por favor, ingrese solo texto normal.'
            )
    return value


class TestSuiteForm(forms.ModelForm):
    class Meta:
        model = TestSuite
        fields = ['nombre', 'descripcion', 'proyecto']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Test Suite',
                'required': True,
                'maxlength': 200  # Added max length
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada del Test Suite',
                'rows': 4,
                'required': True,
                'maxlength': 1000  # Added max length
            }),
            'proyecto': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'proyecto': 'Proyecto'
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return validar_texto_seguro(nombre)
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        return validar_texto_seguro(descripcion)


class CasoPruebaForm(forms.ModelForm):
    class Meta:
        model = CasoPrueba
        fields = ['nombre', 'descripcion', 'test_suite', 'estado', 'version', 'entorno']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Caso de Prueba',
                'required': True,
                'maxlength': 200  # Added max length
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del caso de prueba',
                'rows': 4,
                'required': True,
                'maxlength': 1000  # Added max length
            }),
            'test_suite': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1.0.0',
                'required': True,
                'maxlength': 50  # Added max length
            }),
            'entorno': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'test_suite': 'Test Suite',
            'estado': 'Estado',
            'version': 'Versión',
            'entorno': 'Entorno'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('test_suite'):
            self.fields['test_suite'].widget.attrs['readonly'] = True
            self.fields['test_suite'].widget.attrs['disabled'] = True
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return validar_texto_seguro(nombre)
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        return validar_texto_seguro(descripcion)
    
    def clean_version(self):
        version = self.cleaned_data.get('version')
        return validar_texto_seguro(version)


class EjecucionPruebaForm(forms.ModelForm):
    archivo_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf,.doc,.docx,.txt',  # Restricted to images, PDFs and text documents
            'id': 'id_archivo_upload'
        }),
        label='Subir Archivo (Imágenes, PDF o Documentos)',
        help_text='Solo se permiten imágenes (JPG, PNG, GIF), PDF o documentos de texto'
    )
    
    class Meta:
        model = EjecucionPrueba
        fields = ['caso_prueba', 'estado', 'resultado', 'observaciones']
        widgets = {
            'caso_prueba': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'resultado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Exitoso, Fallido, Bloqueado',
                'required': True,
                'maxlength': 100  # Added max length
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones sobre la ejecución (opcional)',
                'rows': 4,
                'maxlength': 1000  # Added max length
            })
        }
        labels = {
            'caso_prueba': 'Caso de Prueba',
            'estado': 'Estado',
            'resultado': 'Resultado',
            'observaciones': 'Observaciones'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('caso_prueba'):
            self.fields['caso_prueba'].widget.attrs['readonly'] = True
            self.fields['caso_prueba'].widget.attrs['disabled'] = True
    
    def clean_archivo_upload(self):
        archivo = self.cleaned_data.get('archivo_upload')
        if archivo:
            # Validar tamaño (max 10MB)
            if archivo.size > 10 * 1024 * 1024:
                raise ValidationError('El archivo no puede ser mayor a 10MB')
            
            # Validar tipo de archivo por extensión
            nombre_archivo = archivo.name.lower()
            extensiones_permitidas = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt']
            if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                raise ValidationError(
                    'Tipo de archivo no permitido. Solo se aceptan imágenes (JPG, PNG, GIF), PDF o documentos de texto.'
                )
        
        return archivo
    
    def clean_resultado(self):
        resultado = self.cleaned_data.get('resultado')
        return validar_texto_seguro(resultado)
    
    def clean_observaciones(self):
        observaciones = self.cleaned_data.get('observaciones')
        if observaciones:
            return validar_texto_seguro(observaciones)
        return observaciones


class EntornoForm(forms.ModelForm):
    class Meta:
        model = Entorno
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Entorno',
                'required': True,
                'maxlength': 200  # Added max length
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del entorno',
                'rows': 3,
                'required': True,
                'maxlength': 500  # Added max length
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción'
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return validar_texto_seguro(nombre)
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        return validar_texto_seguro(descripcion)
