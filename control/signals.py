from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Transmision, Acta, ReporteTransmision, Operador


from django.db.models.signals import post_save
from django.dispatch import receiver
from control.models import Transmision, Acta, ReporteTransmision


@receiver(post_save, sender=Transmision)
def crear_reporte_transmision(sender, instance, created, **kwargs):
    if not created:
        return

    BATCH_SIZE = 1000
    reportes_batch = []

    actas = Acta.objects.select_related("operador").iterator()

    for acta in actas:
        reportes_batch.append(
            ReporteTransmision(
                acta=acta,
                transmision=instance,
                operador=acta.operador,
                estado='SIN_ENVIAR'
            )
        )

        # insertar por bloques
        if len(reportes_batch) >= BATCH_SIZE:
            ReporteTransmision.objects.bulk_create(reportes_batch)
            reportes_batch.clear()

    # guardar lo restante
    if reportes_batch:
        ReporteTransmision.objects.bulk_create(reportes_batch)