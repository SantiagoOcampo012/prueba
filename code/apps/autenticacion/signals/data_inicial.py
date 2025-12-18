from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.db import transaction


@receiver(post_migrate)
def create_default_data(sender, **kwargs):
    # 1. Verificar que estamos en la app correcta
    if sender.name != 'apps.autenticacion':
        return

    # --- MENSAJE INICIAL ---
    print("\n[INICIO] Iniciando la generación de roles, dominios permitidos y usuario desarrollador inicial...")
    # -----------------------

    try:
        # Usar transacciones atómicas para asegurar que todo se crea o nada se crea
        with transaction.atomic():

            # 2. Obtener los modelos
            Rol = apps.get_model('commons', 'Rol')
            Usuario = apps.get_model('autenticacion', 'Usuario')
            DominioPermitido = apps.get_model('autenticacion', 'DominioPermitido')

            # -------------------------------------
            # A. Crear/Actualizar Roles de Negocio
            # -------------------------------------
            default_roles = [
                {
                    "nombre": "Usuario",
                    "descripcion": "Usuario base, se asigna al registrarse. Solo acceso a perfil.",
                },
                {
                    "nombre": "Propietario",
                    "descripcion": "Dueño de un negocio. Permisos de gestión de la empresa y usuarios.",
                  
                },
                {
                    "nombre": "Trabajador",
                    "descripcion": "Personal con acceso a funciones laborales.",
            
                }
            ]

            print("  [Roles] Procesando roles de negocio: Usuario, Propietario y Trabajador.")
            roles_creados = 0
            roles_existentes = 0

            for role_data in default_roles:
                role, created = Rol.objects.get_or_create(
                    nombre=role_data["nombre"],
                    defaults=role_data
                )
                if created:
                    roles_creados += 1
                else:
                    roles_existentes += 1

            print(f"    - Resultado de Roles: {roles_creados} creados, {roles_existentes} ya existentes.")

            # -------------------------------------
            # B. Crear Dominios de Correo Permitidos
            # -------------------------------------
            allowed_domains = [
                "gmail.com", "outlook.com", "hotmail.com", "yahoo.com",
                "icloud.com", "proton.me", "protonmail.com", "zoho.com",
                "gmx.com", "gmx.net", "aol.com", "mail.com", "live.com",
                "msn.com", "yandex.com", "yandex.ru", "tutanota.com",
                "fastmail.com", "hey.com", "daromanx.com", "dxcontrol.com"
            ]

            print("  [Dominios] Procesando dominios de correo permitidos.")
            dominios_creados = 0
            dominios_existentes = 0

            for domain_name in allowed_domains:
                domain, created = DominioPermitido.objects.get_or_create(
                    nombre=domain_name,
                    defaults={'activo': True}
                )
                if created:
                    dominios_creados += 1
                else:
                    # Si ya existe, nos aseguramos que esté activo.
                    if not domain.activo:
                        domain.activo = True
                        domain.save(update_fields=['activo'])
                    dominios_existentes += 1

            print(
                f"    - Dominios procesados correctamente: {dominios_creados} creados, {dominios_existentes} ya existentes.")

            # -------------------------------------
            # C. Crear Usuario Superadmin (Solo flags de Django)
            # -------------------------------------
            superadmin_email = "developerdaro@gmail.com"

            if not Usuario.objects.filter(correo=superadmin_email).exists():
                print(f"  [Usuario] Creando Superusuario inicial con correo: {superadmin_email}")

                # Creamos el usuario con las banderas de Superusuario
                superusuario = Usuario.objects.create(
                    correo=superadmin_email,
                    nick="DaromanX",
                    password=make_password("1234"),
                    is_staff=True,
                    is_superuser=True,  # El flag que le da todos los permisos
                    is_active=True
                )

                # Asignar el rol base de 'Usuario' visible
                try:
                    rol_usuario_base = Rol.objects.get(nombre='Usuario')
                    superusuario.roles.add(rol_usuario_base)
                    print("    - Rol 'Usuario' asignado al Superusuario.")
                except Rol.DoesNotExist:
                    print("    - ADVERTENCIA: Rol 'Usuario' no encontrado para asignación.")

                print("    - Superusuario inicial creado correctamente.")

            else:
                print(f"  [Usuario] El Superusuario con correo {superadmin_email} ya existe. Omitiendo creación.")

        # --- MENSAJE FINAL ---
        print("[FIN] Generación de datos iniciales completada con éxito.\n")
        # ---------------------

    except Exception as e:
        print(f"\n[ERROR CRÍTICO] Fallo en la señal post_migrate: {e}")
        # La transacción atómica se encargará del rollback
