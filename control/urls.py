from django.urls import path
from .views import (
    login_view,
    admin_inicio,
    admin_actividades,
    admin_transmisiones,
    soporte_dashboard,
    coordinador_dashboard,
    monitor_dashboard,
    api_login,
    api_transmisiones,
    api_user_info,
    api_logout,
    api_operadores_monitor,
    api_actualizar_estado,
    api_actualizar_observacion,
    api_admin_inicio,
)

urlpatterns = [
    path("", login_view, name="login"),
    path("admin-inicio/", admin_inicio),
    path("admin-transmisiones/", admin_transmisiones),
    path("admin-actividades/", admin_actividades),
    path("monitor-dashboard/", monitor_dashboard),
    path("soporte-dashboard/", soporte_dashboard),
    path("coordinador-dashboard/", coordinador_dashboard),
    path("api/login/", api_login, name='login'),
    path("api/transmisiones/", api_transmisiones, name='transmisiones'),
    path("api/user-info/", api_user_info, name="informacion de usuario"),
    path("api/logout/", api_logout, name="logout"),
    path("api/monitor/<int:transmision_id>/operadores/", api_operadores_monitor, name="operadores monitor"),
    path("api/reporte/<int:reporte_id>/estado/", api_actualizar_estado, name="actualizar estado"),
    path("api/reporte/<int:reporte_id>/observacion/", api_actualizar_observacion, name="actualizar observacion"),
    path("api/admin/inicio/", api_admin_inicio, name="Inicio administrador"),

]