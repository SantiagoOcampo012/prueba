# apps/autenticacion/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from ..models import Tipo, Metodologias, Estado, Prioridad


@receiver(post_migrate)
def crear_metadatos_base(sender, **kwargs):
    """
    Crear tipos y registros base si no existen después de migraciones.
    """

    # --- TIPOS ---
    tipos = [
        {"nombre": "Metodologia", "tipo": "metodologia"},
        {"nombre": "Estado", "tipo": "estado"},
        {"nombre": "Prioridad", "tipo": "prioridad"},
    ]

    tipo_obj = {}
    for t in tipos:
        obj, created = Tipo.objects.get_or_create(
            nombre=t["nombre"], defaults={"tipo": t["tipo"]}
        )
        tipo_obj[t["nombre"].lower()] = obj

    # --- METODOLOGIAS ---
    metodologias = [
        "Scrum",
        "Kanban",
        "Scrumban",
        "XP",
        "Lean",
        "Cascada",
        "RUP",
        "DevOps",
        "Agile",
        "TDD(Test-Driven Development)",
        "BDD(Behavior-Driven Development)",
        "ATDD(Acceptance Test Driven Development)",
        "CI/CD Pipeline Testing",
        "Exploratory Testing",
        "Regression Testing",
        "Black Box Testing",
        "White Box Testing",
        "Gray Box Testing",
        "Performance Testing",
        "Security Testing",
        "Automation Testing",
        "Manual Testing",
        "ITIL",
        "COBIT",    
    ]

    for m in metodologias:
        Metodologias.objects.get_or_create(nombre=m, tipo=tipo_obj["metodologia"])

    # --- ESTADOS ---
    estados = [
        # Estado general
        "Abierto",
        "Nuevo",
        "En proceso",
        "En análisis",
        "En revisión",
        "En prueba",
        "En validación",
        "Pendiente",
        "Bloqueado",
        "Escalado",
        "Reabierto",
        "Listo",
        "Resuelto",
        "Cerrado",
        "Rechazado",
        # Estado Sprint / proyecto
        "Planeado",
        "En progreso",
        "En revisión",
        "Completado",
        "Cancelado",
        # Estado Pruebas
        "Pendiente de ejecución",
        "En ejecución",
        "Ejecutado(Correcto)",
        "Ejecutado(Falló)",
        "Ejecutado(Con advertencias)",
        "No aplica",
        "Bloqueado",
        # Estado Notificaciones
        "Leída",
        "No leída",
        "Archivada",
    ]

    for e in estados:
        Estado.objects.get_or_create(nombre=e, tipo=tipo_obj["estado"])

    # --- PRIORIDADES ---
    prioridades = [
        "Baja",
        "Media",
        "Alta",
        "Crítica",
        "Urgente",
        "Trivial",
        "Menor",
        "Mayor",
        "Showstopper",
    ]

    for p in prioridades:
        Prioridad.objects.get_or_create(nombre=p, tipo=tipo_obj["prioridad"])
