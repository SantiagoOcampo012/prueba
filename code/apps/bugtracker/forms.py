from django import forms
from .models import Bug, ComentarioBug
from apps.commons.models import Estado, Prioridad, File
from apps.proyectos.models import Proyecto, Sprint
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def validate_file_size(file):
    """Validar que el archivo no exceda 10MB"""
    max_size = 10 * 1024 * 1024  # 10MB en bytes
    if file.size > max_size:
        raise ValidationError('El archivo no debe exceder 10MB.')


def validate_file_extension(file):
    """Validar que el archivo tenga una extensión permitida"""
    import os
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Tipo de archivo no permitido. Formatos aceptados: JPG, PNG, GIF, PDF, DOC, DOCX, TXT'
        )


class BugForm(forms.ModelForm):
    """Formulario para crear y editar bugs"""
    
    # Override del campo asignado_a para personalizar la visualización
    asignado_a = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_asignado_a'
        }),
        label='Asignado a'
    )
    
    # Override del campo archivo para manejar el modelo File correctamente
    archivo = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_archivo',
            'accept': '.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt'
        }),
        label='Archivo adjunto',
        help_text='Formatos: JPG, PNG, GIF, PDF, DOC, DOCX, TXT. Tamaño máximo: 10MB',
        validators=[validate_file_size, validate_file_extension]
    )
    
    class Meta:
        model = Bug
        fields = [
            'titulo', 'descripcion', 'severidad', 'prioridad',
            'estado', 'proyecto', 'sprint', 'asignado_a'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del bug',
                'id': 'id_titulo'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe el bug en detalle',
                'rows': 4,
                'id': 'id_descripcion'
            }),
            'severidad': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_severidad'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_prioridad'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_estado'
            }),
            'proyecto': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_proyecto'
            }),
            'sprint': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_sprint'
            }),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'severidad': 'Severidad',
            'prioridad': 'Prioridad',
            'estado': 'Estado',
            'proyecto': 'Proyecto',
            'sprint': 'Sprint',
            'asignado_a': 'Asignado a',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer algunos campos opcionales
        self.fields['sprint'].required = False
        self.fields['asignado_a'].required = False
        self.fields['archivo'].required = False
        self.fields['severidad'].required = False
        self.fields['prioridad'].required = False
        self.fields['estado'].required = False
        
        # Filtrar severidad para mostrar solo: Baja, Media, Alta, Crítica
        self.fields['severidad'].queryset = Prioridad.objects.filter(
            nombre__in=['Baja', 'Media', 'Alta', 'Crítica']
        )
        
        # Filtrar prioridad para mostrar solo: Baja, Media, Alta, Crítica
        self.fields['prioridad'].queryset = Prioridad.objects.filter(
            nombre__in=['Baja', 'Media', 'Alta', 'Crítica']
        )
        
        # Personalizar el label_from_instance para el campo asignado_a
        # Esto hace que se muestre 'nick' en lugar de 'username'
        self.fields['asignado_a'].label_from_instance = lambda obj: obj.nick
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Manejar el archivo manualmente
        archivo_subido = self.cleaned_data.get('archivo')
        if archivo_subido:
            # Crear una instancia de File
            file_obj = File()
            file_obj.ruta = archivo_subido
            file_obj.save()
            instance.archivo = file_obj
        
        if commit:
            instance.save()
        
        return instance


class ComentarioBugForm(forms.ModelForm):
    """Formulario para crear y editar comentarios de bugs"""
    
    # Override del campo archivo para manejar el modelo File correctamente
    archivo = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_archivo_comentario',
            'accept': '.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt'
        }),
        label='Archivo adjunto',
        help_text='Formatos: JPG, PNG, GIF, PDF, DOC, DOCX, TXT. Tamaño máximo: 10MB',
        validators=[validate_file_size, validate_file_extension]
    )
    
    class Meta:
        model = ComentarioBug
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu comentario aquí...',
                'rows': 3,
                'id': 'id_comentario'
            }),
        }
        labels = {
            'comentario': 'Comentario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Manejar el archivo manualmente
        archivo_subido = self.cleaned_data.get('archivo')
        if archivo_subido:
            # Crear una instancia de File
            file_obj = File()
            file_obj.ruta = archivo_subido
            file_obj.save()
            instance.archivo = file_obj
        
        if commit:
            instance.save()
        
        return instance