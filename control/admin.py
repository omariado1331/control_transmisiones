from django.contrib import admin
from .models import (
    Recinto,
    Soporte,
    Monitor,
    Coordinador,
    Acta,
    Transmision,
    ReporteTransmision,
    Operador,
    Actividad,
    ReporteActividad
)

# Register your models here.

@admin.register(Recinto)
class RecintoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo",
        "departamento",
        "provincia",
        "municipio",
        "zona",
        "nro_mesas",
    )
    search_fields = ("nombre", "municipio", "zona", "codigo")
    list_filter = ("municipio", "provincia")


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ci", "celular", "user")
    search_fields = ("nombre", "ci", "celular")

@admin.register(Soporte)
class SoporteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ci", "celular", "user")
    search_fields = ("nombre", "celular", "ci")

@admin.register(Coordinador)
class CoordinadorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ci", "celular", "user")
    search_fields = ("nombre", "ci", "celular")

@admin.register(Operador)
class OperadorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido_materno", "ci", "celular", "recinto", "coordinador", "monitor", "soporte")
    search_fields = ("nombre", "apellido_paterno", "ci", "celular")
    list_filter = ("monitor", "soporte", "coordinador")

@admin.register(Acta)
class ActaAdmin(admin.ModelAdmin):
    list_display = ("numero", "recinto", "operador")
    search_fields = ("numero", "recinto__nombre", "operador__ci" )
    list_filter = ("recinto", )

@admin.register(Transmision)
class TransmisionAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "fecha", "hora")
    search_fields = ("fecha", )

@admin.register(ReporteTransmision)
class ReporteTransmisionAdmin(admin.ModelAdmin):
    list_display = ("transmision", "acta", "estado", "operador", "observacion")
    list_filter = ("operador", "transmision", "estado")
    search_fields = ("acta__numero", "operador__nombre")
    list_editable = ("estado", "observacion")
    autocomplete_fields = ("operador", "acta")

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "fecha", "hora")

@admin.register(ReporteActividad)
class ReporteActividadAdmin(admin.ModelAdmin):
    list_display = ("operador", "realizado", "actividad")
    list_filter = ("actividad", )
    search_fields = ("operador__ci", "operador__apellido_paterno", "operador__apellido_materno")

