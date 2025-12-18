# apps/core/utils.py
from django.utils.text import slugify

def generar_slug_unico(instance, base_field: str, slug_field: str = "slug"):
    """
    Genera un slug único basado en otro campo (por ejemplo, nick o nombre).
    - instance: el objeto que se está guardando.
    - base_field: nombre del campo base (str).
    - slug_field: nombre del campo slug (default: 'slug').
    """
    base_value = getattr(instance, base_field)
    base_slug = slugify(base_value)
    slug = base_slug
    contador = 1

    ModelClass = instance.__class__
    slugs_existentes = set(
        ModelClass.objects.filter(**{f"{slug_field}__startswith": base_slug})
        .exclude(pk=instance.pk)
        .values_list(slug_field, flat=True)
    )

    while slug in slugs_existentes:
        contador += 1
        slug = f"{base_slug}-{contador}"

    return slug
