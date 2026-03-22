from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Prefetch, Count, Q
from .models import Monitor, Soporte, Coordinador
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from .models import (
    Monitor, 
    Soporte, 
    Coordinador, 
    Operador, 
    ReporteTransmision, 
    Transmision, 
    Acta, 
    Recinto,
    Actividad
)

def api_login(request):

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    import json
    data = json.loads(request.body)

    username = data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"error": "Credenciales incorrectas"}, status=400)

    login(request, user)

    # detectar rol
    if user.is_superuser:
        return JsonResponse({"redirect": "/control/admin-inicio/"})

    if Monitor.objects.filter(user=user).exists():
        return JsonResponse({"redirect": "/control/monitor-dashboard/"})

    if Soporte.objects.filter(user=user).exists():
        return JsonResponse({"redirect": "/control/soporte-dashboard/"})

    if Coordinador.objects.filter(user=user).exists():
        return JsonResponse({"redirect": "/control/coordinador-dashboard/"})

    return JsonResponse({"error": "Usuario sin rol"}, status=400)

def login_view(request):
    return render(request, "login.html")

@login_required
def admin_inicio(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("NO AUTORIZADO")
    return render(request, "admin/inicio.html")

@login_required
def admin_transmisiones(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("NO AUTORIZADO")
    return render(request, "admin/transmisiones.html")

@login_required
def admin_actividades(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("NO AUTORIZADO")
    return render(request, "admin/actividades.html")

@login_required
def soporte_dashboard(request):
    if not Soporte.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("NO AUTORIZADO")

    return render(request, "soporte/dashboard.html")

@login_required
def monitor_dashboard(request):
    if not Monitor.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("NO AUTORIZADO")
    return render(request, "monitor/dashboard.html")

@login_required
def coordinador_dashboard(request):
    if not Coordinador.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("NO AUTORIZADO")
    return render(request, "coordinador/dashboard.html")

# api para obtener los operadores asignados al monitor, por transmision id
@login_required
def api_operadores_monitor(request, transmision_id):

    user = request.user

    # validar que sea monitor
    try:
        monitor = Monitor.objects.get(user=user)
    except Monitor.DoesNotExist:
        return JsonResponse({"error": "No autorizado"}, status=403)

    # traer operadores del monitor
    operadores = Operador.objects.filter(
        monitor=monitor
    ).select_related("recinto")

    # traer reportes filtrados por transmisión
    reportes_qs = ReporteTransmision.objects.filter(
        transmision_id=transmision_id
    ).select_related("acta")

    # prefetch para evitar N+1
    operadores = operadores.prefetch_related(
        Prefetch(
            "reportetransmision_set",
            queryset=reportes_qs,
            to_attr="reportes_filtrados"
        )
    )

    data = []

    for op in operadores:

        operador_data = {
            "id": op.id,
            "nombre": op.nombre,
            "apellido_paterno": op.apellido_paterno,
            "apellido_materno": op.apellido_materno,
            "ci": op.ci,
            "celular": op.celular,
            "recinto": {
                "id": op.recinto.id if op.recinto else None,
                "nombre": op.recinto.nombre if op.recinto else None,
            },
            "actas": []
        }

        # reportes del operador en esa transmisión
        for rep in op.reportes_filtrados:

            operador_data["actas"].append({
                "id": rep.id,
                "numero": rep.acta.numero,
                "estado": rep.estado,
                "observacion": rep.observacion
            })

        data.append(operador_data)

    return JsonResponse(data, safe=False)

@login_required
def api_transmisiones(request):
    transmisiones = Transmision.objects.all().order_by("-fecha", "-hora")

    data = [
        {
            "id": t.id,
            "descripcion": t.descripcion,
            "fecha": t.fecha,
            "hora": t.hora
        }
        for t in transmisiones
    ]
    return JsonResponse(data, safe=False)

@login_required
def api_user_info(request):

    user = request.user

    # detectar rol
    if user.is_superuser:
        rol = "ADMINISTRADOR"

    elif Monitor.objects.filter(user=user).exists():
        rol = "MONITOR"

    elif Soporte.objects.filter(user=user).exists():
        rol = "SOPORTE"

    elif Coordinador.objects.filter(user=user).exists():
        rol = "COORDINADOR"

    else:
        rol = "SIN_ROL"

    data = {
        "username": user.username,
        "rol": rol
    }

    return JsonResponse(data)

@require_POST
def api_logout(request):

    logout(request)

    return JsonResponse({"message": "Sesión cerrada"})

@login_required
@require_POST
def api_actualizar_estado(request, reporte_id):

    # validar rol monitor
    if not Monitor.objects.filter(user=request.user).exists():
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        reporte = ReporteTransmision.objects.select_related("operador").get(id=reporte_id)
    except ReporteTransmision.DoesNotExist:
        return JsonResponse({"error": "Reporte no encontrado"}, status=404)

    # seguridad extra
    if reporte.operador and reporte.operador.monitor.user != request.user:
        return JsonResponse({"error": "No autorizado"}, status=403)

    data = json.loads(request.body)
    estado = data.get("estado")

    estados_validos = dict(ReporteTransmision.ESTADOS).keys()

    if estado not in estados_validos:
        return JsonResponse({"error": "Estado inválido"}, status=400)

    reporte.estado = estado
    reporte.save(update_fields=["estado"])

    return JsonResponse({
        "message": "Estado actualizado",
        "id": reporte.id,
        "estado": reporte.estado
    })

@login_required
@require_POST
def api_actualizar_observacion(request, reporte_id):

    # validar rol monitor
    if not Monitor.objects.filter(user=request.user).exists():
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        reporte = ReporteTransmision.objects.select_related("operador").get(id=reporte_id)
    except ReporteTransmision.DoesNotExist:
        return JsonResponse({"error": "Reporte no encontrado"}, status=404)

    # seguridad
    if reporte.operador and reporte.operador.monitor.user != request.user:
        return JsonResponse({"error": "No autorizado"}, status=403)

    data = json.loads(request.body)
    observacion = data.get("observacion")

    reporte.observacion = observacion
    reporte.save(update_fields=["observacion"])

    return JsonResponse({
        "message": "Observación actualizada",
        "id": reporte.id,
        "observacion": reporte.observacion
    })

@login_required
def api_admin_inicio(request):

    # solo administradores
    if not request.user.is_superuser:
        return JsonResponse({"error": "No autorizado"}, status=403)

    # totales
    total_actas = Acta.objects.count()

    total_recintos = Recinto.objects.count()

    recintos_urbanos = Recinto.objects.filter(tipo="Urbano").count()

    recintos_rurales = Recinto.objects.exclude(tipo="Urbano").count()

    # transmisiones
    transmisiones = list(
        Transmision.objects.all()
        .order_by("-fecha", "-hora")
        .values("id", "descripcion", "fecha", "hora")
    )

    # actividades
    actividades = list(
        Actividad.objects.all()
        .order_by("-fecha", "-hora")
        .values("id", "descripcion", "fecha", "hora")
    )

    data = {
        "total_actas": total_actas,
        "total_recintos": total_recintos,
        "recintos_urbanos": recintos_urbanos,
        "recintos_rurales": recintos_rurales,
        "transmisiones": transmisiones,
        "actividades": actividades,
    }

    return JsonResponse(data)

@login_required
def api_estadisticas_actas(request, transmision_id):

    qs = ReporteTransmision.objects.filter(
        transmision_id=transmision_id
    )

    conteo_qs = qs.values("estado").annotate(total=Count("id"))

    # estructura base
    conteo = {
        "TRANSMITIDO": 0,
        "REVISADO_RECHAZADO": 0,
        "ENVIADO_NO_REVISADO": 0,
        "SIN_ENVIAR": 0
    }

    for item in conteo_qs:
        conteo[item["estado"]] = item["total"]

    total = sum(conteo.values())

    # calcular porcentajes
    porcentajes = {}

    for estado, cantidad in conteo.items():
        if total > 0:
            porcentaje = (cantidad / total) * 100
        else:
            porcentaje = 0

        porcentajes[estado] = round(porcentaje, 2)

    data = {
        "total": total,
        "conteo": conteo,
        "porcentajes": porcentajes
    }

    return JsonResponse(data)
