from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Recinto(models.Model):
    departamento = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    asiento_electoral = models.CharField(max_length=100)
    distrito = models.CharField(max_length=100)
    zona = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=255)
    nro_mesas = models.IntegerField(default=0)
    codigo = models.CharField(max_length=50, unique=True, db_index=True, blank=True, null=True)
    ruta = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"

class Soporte(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    ci = models.CharField(max_length=100, unique=True, db_index=True)
    celular = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"

class Monitor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    ci = models.CharField(max_length=100, unique=True, db_index=True)
    celular = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"
    
class Coordinador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    ci = models.CharField(max_length=100, unique=True, db_index=True)
    celular = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"


class Transmision(models.Model):
    descripcion = models.CharField(max_length=100)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"
    

class Operador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    celular = models.CharField(max_length=100)
    ci = models.CharField(max_length=50, unique=True, db_index=True)
    
    recinto = models.ForeignKey(Recinto, on_delete=models.SET_NULL, null=True, blank=True)
    monitor = models.ForeignKey(Monitor, on_delete=models.SET_NULL, null=True, blank=True)
    soporte = models.ForeignKey(Soporte, on_delete=models.SET_NULL, null=True, blank=True)
    coordinador = models.ForeignKey(Coordinador, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
    

class Acta(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True)
    recinto = models.ForeignKey(Recinto, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.numero

class ReporteTransmision(models.Model):
    ESTADOS = [
        ("TRANSMITIDO", "Transmitido"),
        ("REVISADO_RECHAZADO", "Revisado rechazado"),
        ("SIN_ENVIAR", "Sin enviar"),
        ("ENVIADO_NO_REVISADO", "Enviado no revisado")
    ]

    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, null=True, blank=True)
    acta = models.ForeignKey(Acta, on_delete=models.CASCADE)
    transmision = models.ForeignKey(Transmision, on_delete=models.CASCADE)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="SIN_ENVIAR"
    )

    observacion = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("acta", "transmision") 

        indexes = [
            models.Index(fields=["transmision"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["operador"])
        ]

    def __str__(self):
        return f"{self.acta} {self.estado}"
    

class Actividad(models.Model):
    descripcion = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()

    def __str__(self):
        return self.descripcion

class ReporteActividad(models.Model):
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)

    realizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.operador} {self.realizado}"
