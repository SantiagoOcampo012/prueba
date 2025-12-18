import re
from datetime import timedelta
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import F
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail

from .models import Usuario, AutenticacionMultifactor, TokenActivacion
from .forms import (
    RegistroForm,
    LoginForm,
    MFAForm,
    SolicitudActivacionForm,
    RecuperacionPasswordForm,
    RestablecerPasswordForm,
)

# --- CONFIGURACIÓN DE RESTRICCIONES ---
MFA_EXPIRATION_MINUTES = 60
ACTIVATION_RESEND_LIMIT_HOURS = 24
PASSWORD_RESET_INTERVAL_HOURS = 5
PASSWORD_RESET_DAILY_LIMIT = 3


# ---------------------------------------------------------
# FUNCIÓN UTILITARIA PARA CONTROL DE CACHÉ
# Evita que el botón "Atrás" muestre contenido de inicio de sesión
# ---------------------------------------------------------
def _no_cache_response(response: HttpResponse) -> HttpResponse:
    """Añade encabezados para prevenir el cacheo del navegador."""
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


# ---------------------------------------------------------
#  FUNCIÓN DE ENVÍO DE CORREO REAL
# ---------------------------------------------------------
def enviar_correo(asunto: str, mensaje: str, destinatario: str) -> None:
    """Función real para el envío de correos electrónicos usando la configuración SMTP de Django."""
    try:
        send_mail(
            asunto,
            mensaje,
            "no-reply@tuproyecto.com",
            [destinatario],
            fail_silently=False,
        )
    except Exception as e:
        print(
            f"ERROR: No se pudo enviar el correo a {destinatario} con asunto '{asunto}'. Motivo: {e}"
        )


# ---------------------------------------------------------
#  FLUJO DE REGISTRO Y ACTIVACIÓN DE CUENTA
# ---------------------------------------------------------
def registro(request: HttpRequest) -> HttpResponse:
    """Registra al usuario y envía el enlace de activación."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user: Usuario = form.save()
            token_activacion: TokenActivacion = user.crear_token_activacion()

            activation_url = request.build_absolute_uri(
                reverse("activacion_cuenta", args=[user.pk, token_activacion.token])
            )

            mensaje = (
                f"¡Bienvenido, {user.nick}!\n\n"
                f"Por favor, haz clic en el siguiente enlace para activar tu cuenta:\n"
                f"{activation_url}\n\n"
                f"Este enlace, por tu petición, no tiene expiración."
            )
            enviar_correo("Activa tu cuenta de usuario", mensaje, user.correo)

            messages.success(
                request,
                "Tu cuenta ha sido creada. Por favor, revisa tu correo electrónico para activarla.",
            )
            return redirect("login_step1")
    else:
        form = RegistroForm()

    context = {"form": form, "title": "Registro de Usuario"}
    response = render(request, "auth/registro.html", context)
    return _no_cache_response(response)


@require_http_methods(["GET"])
def activacion_cuenta(request: HttpRequest, user_id: int, token: str) -> HttpResponse:
    """Activa la cuenta del usuario al hacer clic en el enlace."""
    try:
        user: Usuario = Usuario.objects.get(pk=user_id)
        token_obj: TokenActivacion = TokenActivacion.objects.get(
            usuario=user, token=token, usado=False
        )
    except (Usuario.DoesNotExist, TokenActivacion.DoesNotExist):
        messages.error(
            request, "El enlace de activación no es válido o ya fue utilizado."
        )
        return redirect("login_step1")

    if user.is_active:
        messages.warning(
            request, "Tu cuenta ya se encuentra activa. Puedes iniciar sesión."
        )
        return redirect("login_step1")

    user.is_active = True
    user.save(update_fields=["is_active"])
    token_obj.marcar_como_usado()

    messages.success(
        request, "¡Cuenta activada exitosamente! Ya puedes iniciar sesión."
    )
    return redirect("login_step1")


def solicitar_activacion(request: HttpRequest) -> HttpResponse:
    """Permite al usuario solicitar un nuevo enlace de activación (con rate limit)."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SolicitudActivacionForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"]
            try:
                user: Usuario = Usuario.objects.get(correo__iexact=correo)
            except Usuario.DoesNotExist:
                messages.success(
                    request,
                    "Si la cuenta existe y está inactiva, te hemos enviado un correo. Revisa tu bandeja de spam.",
                )
                return redirect("login_step1")

            if user.is_active:
                messages.info(request, "Tu cuenta ya está activa.")
                return redirect("login_step1")

            try:
                latest_token = TokenActivacion.objects.filter(usuario=user).latest(
                    "creacion"
                )
                time_since_last_token = timezone.now() - latest_token.creacion

                if time_since_last_token < timedelta(
                    hours=ACTIVATION_RESEND_LIMIT_HOURS
                ):
                    remaining_time = (
                        timedelta(hours=ACTIVATION_RESEND_LIMIT_HOURS)
                        - time_since_last_token
                    )
                    secs_total = int(remaining_time.total_seconds())
                    hours = secs_total // 3600
                    mins = (secs_total % 3600) // 60
                    secs = secs_total % 60

                    messages.warning(
                        request,
                        f"Ya se envió un enlace recientemente. Por favor, espera {hours} horas, {mins} minutos y {secs} segundos para solicitar uno nuevo.",
                    )
                    return redirect("solicitar_activacion")

            except TokenActivacion.DoesNotExist:
                pass

            token_activacion: TokenActivacion = user.crear_token_activacion()

            activation_url = request.build_absolute_uri(
                reverse("activacion_cuenta", args=[user.pk, token_activacion.token])
            )

            mensaje = (
                f"Solicitaste un nuevo enlace de activación.\n\n"
                f"Haz clic aquí: {activation_url}"
            )
            enviar_correo("Nuevo Enlace de Activación", mensaje, user.correo)
            messages.success(request, "Enlace de activación enviado. Revisa tu correo.")
            return redirect("login_step1")

    else:
        form = SolicitudActivacionForm()

    context = {"form": form, "title": "Solicitar Enlace de Activación"}
    return render(request, "auth/activar_cuenta.html", context)


# ---------------------------------------------------------
#  FLUJO DE LOGIN CON MFA
# ---------------------------------------------------------
def login_step1(request: HttpRequest) -> HttpResponse:
    """Paso 1: Validación de credenciales. Envía código MFA si es exitoso."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=correo, password=password)

            if user is not None:
                # 1. Bloqueo por contraseña
                if user.esta_bloqueado():
                    # Calculamos el tiempo restante FRESCO y lo mostramos
                    remaining_time = user.bloqueado_hasta - timezone.now()
                    secs_total = int(remaining_time.total_seconds())
                    mins = secs_total // 60
                    secs = secs_total % 60

                    messages.error(
                        request,
                        f"Tu cuenta está bloqueada por demasiados intentos fallidos. Debes esperar {mins} minutos y {secs} segundos para volver a intentarlo.",
                    )
                    return redirect("login_step1")

                # 2. Cuenta activa?
                if not user.is_active:
                    messages.warning(
                        request,
                        "Tu cuenta está inactiva. Por favor, revisa tu correo o solicita un nuevo enlace de activación.",
                    )
                    return redirect("solicitar_activacion")

                # --- Generación de código MFA (omitiendo la lógica de chequeo de código activo por simplicidad en esta corrección) ---

                # B. Generar código nuevo
                import random

                mfa_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
                expiration_time = timezone.now() + timedelta(
                    minutes=MFA_EXPIRATION_MINUTES
                )

                AutenticacionMultifactor.objects.create(
                    usuario=user,
                    codigo_verificacion=mfa_code,
                    fecha_expiracion=expiration_time,
                    ip=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                )

                mensaje = (
                    f"Tu código de verificación de inicio de sesión es: {mfa_code}\n"
                    f"Expira en {MFA_EXPIRATION_MINUTES} minutos."
                )
                enviar_correo("Código de Verificación MFA", mensaje, user.correo)

                request.session["mfa_user_id"] = user.pk
                messages.info(
                    request,
                    "Se ha enviado un código de verificación de 6 dígitos a tu correo electrónico.",
                )
                return redirect("login_step2")

            else:
                # Manejo de intentos fallidos
                try:
                    user_to_block = Usuario.objects.get(correo__iexact=correo)
                    now = timezone.now()

                    # Limpiar bloqueo si ha expirado antes de sumar
                    if user_to_block.esta_bloqueado():
                        # Si está bloqueado, solo recalculamos y mostramos el tiempo restante
                        remaining_time = user_to_block.bloqueado_hasta - now
                        secs_total = int(remaining_time.total_seconds())
                        mins = secs_total // 60
                        secs = secs_total % 60
                        messages.error(
                            request,
                            f"Tu cuenta está bloqueada. Debes esperar {mins} minutos y {secs} segundos.",
                        )
                        return redirect("login_step1")

                    # Sumar intento fallido
                    new_attempts = user_to_block.intentos_fallidos + 1

                    user_to_block.intentos_fallidos = F("intentos_fallidos") + 1
                    user_to_block.ultimo_intento = now

                    # -------------------------------------------------------------
                    # CORRECCIÓN DE MENSAJERÍA: Solo un mensaje (el dinámico)
                    # -------------------------------------------------------------
                    if new_attempts >= 5:
                        # Bloqueo por 30 min
                        user_to_block.bloqueado_hasta = now + timedelta(minutes=30)
                        user_to_block.save(
                            update_fields=[
                                "intentos_fallidos",
                                "ultimo_intento",
                                "bloqueado_hasta",
                            ]
                        )

                        # Recargamos para obtener el tiempo exacto de bloqueo
                        user_to_block.refresh_from_db()

                        # Calculamos y mostramos el tiempo dinámico y ÚNICO
                        remaining_time = user_to_block.bloqueado_hasta - now
                        secs_total = int(remaining_time.total_seconds())
                        mins = secs_total // 60
                        secs = secs_total % 60

                        messages.error(
                            request,
                            f"Credenciales incorrectas. Tu cuenta ha sido bloqueada por demasiados intentos. Debes esperar {mins} minutos y {secs} segundos.",
                        )
                    else:
                        user_to_block.save(
                            update_fields=["intentos_fallidos", "ultimo_intento"]
                        )
                        messages.error(request, "Credenciales incorrectas.")

                except Usuario.DoesNotExist:
                    messages.error(request, "Credenciales incorrectas.")

                # Asegura la redirección después del POST, necesaria para mostrar los mensajes
                return redirect("login_step1")

    else:
        form = LoginForm()

    context = {"form": form, "title": "Iniciar Sesión"}
    response = render(request, "auth/login.html", context)
    return _no_cache_response(response)


def login_step2(request: HttpRequest) -> HttpResponse:
    """Paso 2: Validación del código MFA e inicio de sesión."""
    if request.user.is_authenticated:
        return redirect("home")

    user_id = request.session.get("mfa_user_id")

    if not user_id:
        messages.warning(
            request, "Por favor, inicia sesión con tu correo y contraseña primero."
        )
        return redirect("login_step1")

    try:
        user: Usuario = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        messages.error(
            request,
            "Error de sesión. Por favor, reinicia el proceso de inicio de sesión.",
        )
        return redirect("login_step1")

    if request.method == "POST":
        form = MFAForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data["codigo"]

            try:
                mfa_code_obj: AutenticacionMultifactor = (
                    AutenticacionMultifactor.objects.get(
                        usuario=user,
                        codigo_verificacion=codigo,
                        fecha_expiracion__gt=timezone.now(),
                        usado=False,
                    )
                )

                mfa_code_obj.marcar_como_usado()

                user.intentos_fallidos = 0
                user.bloqueado_hasta = None
                user.mfa_fallos_consecutivos = 0
                user.mfa_nivel_bloqueo = 0
                user.mfa_bloqueo_expiracion = None

                user.save(
                    update_fields=[
                        "intentos_fallidos",
                        "bloqueado_hasta",
                        "mfa_fallos_consecutivos",
                        "mfa_nivel_bloqueo",
                        "mfa_bloqueo_expiracion",
                    ]
                )

                login(request, user)
                del request.session["mfa_user_id"]

                messages.success(
                    request, f"¡Bienvenido, {user.nick}! Has iniciado sesión."
                )
                return redirect("home")

            except AutenticacionMultifactor.DoesNotExist:
                messages.error(
                    request, "El código de verificación es incorrecto o ha expirado."
                )

                # --- Manejo de bloqueo MFA ---
                new_mfa_fallos = user.mfa_fallos_consecutivos + 1

                user.mfa_fallos_consecutivos = F("mfa_fallos_consecutivos") + 1
                user.mfa_bloqueo_expiracion = None

                if new_mfa_fallos >= 5:
                    user.mfa_nivel_bloqueo = 1
                    user.mfa_bloqueo_expiracion = timezone.now() + timedelta(minutes=10)

                user.save(
                    update_fields=[
                        "mfa_fallos_consecutivos",
                        "mfa_nivel_bloqueo",
                        "mfa_bloqueo_expiracion",
                    ]
                )

                user.refresh_from_db()
                if user.esta_bloqueado_mfa():
                    # Muestra el tiempo restante de bloqueo MFA
                    remaining_time = user.mfa_bloqueo_expiracion - timezone.now()
                    secs_total = int(remaining_time.total_seconds())
                    mins = secs_total // 60
                    secs = secs_total % 60

                    messages.error(
                        request,
                        f"Tu acceso MFA está bloqueado temporalmente. Debes esperar {mins} minutos y {secs} segundos para volver a intentarlo.",
                    )
                    return redirect("login_step1")

    else:
        # Verificar si el usuario está bloqueado por MFA al cargar la página
        if user.esta_bloqueado_mfa():
            remaining_time = user.mfa_bloqueo_expiracion - timezone.now()
            secs_total = int(remaining_time.total_seconds())
            mins = secs_total // 60
            secs = secs_total % 60

            messages.error(
                request,
                f"Tu acceso MFA está bloqueado temporalmente. Debes esperar {mins} minutos y {secs} segundos para volver a intentarlo.",
            )
            return redirect("login_step1")

        form = MFAForm()

    context = {"form": form, "title": "Verificación MFA", "user_correo": user.correo}
    return render(request, "auth/verificar_otp.html", context)


# ---------------------------------------------------------
#  FLUJO DE RECUPERACIÓN DE CONTRASEÑA
# ---------------------------------------------------------
def recuperar_password(request: HttpRequest) -> HttpResponse:
    """Paso 1: Solicitud de recuperación. Envía enlace al correo."""
    if request.user.is_authenticated:
        return redirect("home")

    GENERIC_SUCCESS_MESSAGE = "Si el correo está registrado, se te ha enviado un enlace para restablecer tu contraseña. Revisa tu bandeja de spam."

    if request.method == "POST":
        form = RecuperacionPasswordForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"]

            try:
                user: Usuario = Usuario.objects.get(correo__iexact=correo)
            except Usuario.DoesNotExist:
                messages.success(request, GENERIC_SUCCESS_MESSAGE)
                return redirect("login_step1")

            now = timezone.now()

            # 1. Control de intervalo (5 horas entre solicitudes)
            try:
                latest_reset_token = TokenActivacion.objects.filter(
                    usuario=user
                ).latest("creacion")
                time_since_last = now - latest_reset_token.creacion

                if time_since_last < timedelta(hours=PASSWORD_RESET_INTERVAL_HOURS):
                    messages.success(request, GENERIC_SUCCESS_MESSAGE)
                    return redirect("login_step1")
            except TokenActivacion.DoesNotExist:
                pass

            # 2. Control de límite diario (3 veces en 24 horas)
            twenty_four_hours_ago = now - timedelta(hours=24)
            tokens_today = TokenActivacion.objects.filter(
                usuario=user, creacion__gte=twenty_four_hours_ago
            ).count()

            if tokens_today >= PASSWORD_RESET_DAILY_LIMIT:
                messages.error(
                    request,
                    "Has excedido el límite de 3 solicitudes de restablecimiento de contraseña en las últimas 24 horas. Por favor, espera.",
                )
                return redirect("login_step1")

            reset_token: TokenActivacion = TokenActivacion.objects.create(usuario=user)

            reset_url = request.build_absolute_uri(
                reverse("restablecer_password", args=[user.pk, reset_token.token])
            )

            mensaje = (
                f"Hola {user.nick},\n\n"
                f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n"
                f"{reset_url}\n\n"
                f"Este enlace expirará en {reset_token.DURACION_HORAS} horas."
            )
            enviar_correo("Restablecer Contraseña", mensaje, user.correo)

            messages.success(request, GENERIC_SUCCESS_MESSAGE)
            return redirect("login_step1")

    else:
        form = RecuperacionPasswordForm()

    context = {"form": form, "title": "Recuperar Contraseña"}

    response = render(request, "auth/recuperar_password.html", context)
    return _no_cache_response(response)


def restablecer_password(
    request: HttpRequest, user_id: int, token: str
) -> HttpResponse:
    """Paso 2: Validación del token y cambio de contraseña."""
    if request.user.is_authenticated:
        return redirect("home")

    try:
        user: Usuario = Usuario.objects.get(pk=user_id)
        token_obj: TokenActivacion = TokenActivacion.objects.get(
            usuario=user, token=token, usado=False
        )
    except (Usuario.DoesNotExist, TokenActivacion.DoesNotExist):
        messages.error(request, "El enlace de restablecimiento no es válido.")
        return redirect("login_step1")

    if token_obj.expirado():
        messages.error(
            request,
            "El enlace de restablecimiento ha expirado. Por favor, solicita uno nuevo.",
        )
        return redirect("recuperar_password")

    if request.method == "POST":
        form = RestablecerPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]

            user.set_password(new_password)
            user.save(update_fields=["password"])
            token_obj.marcar_como_usado()

            messages.success(
                request,
                "¡Contraseña restablecida exitosamente! Ya puedes iniciar sesión.",
            )
            return redirect("login_step1")
    else:
        form = RestablecerPasswordForm()

    context = {
        "form": form,
        "title": "Restablecer Contraseña",
        "user_id": user_id,
        "token": token,
    }
    return render(request, "auth/restablecer_password_confirm.html", context)


# ---------------------------------------------------------
#  VISTA DE EJEMPLO PARA LOGOUT
# ---------------------------------------------------------
def user_logout(request: HttpRequest) -> HttpResponse:
    """Cierra la sesión del usuario."""
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("login_step1")


# ---------------------------------------------------------
#  VISTA DE EJEMPLO PARA HOME
# ---------------------------------------------------------
def home(request: HttpRequest) -> HttpResponse:
    """Vista de inicio simple para usuarios logueados."""
    if not request.user.is_authenticated:
        return redirect("login_step1")

    current_time = timezone.now()

    context = {
        "title": "Página Principal",
        "user": request.user,
        "server_time": current_time,
        "location": "Popayán, Cauca, Colombia",
    }
    response = render(request, "auth/home.html", context)
    # También aplicamos no-cache a la vista principal por seguridad
    return _no_cache_response(response)
