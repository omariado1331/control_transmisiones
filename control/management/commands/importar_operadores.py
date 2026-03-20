import csv
import unicodedata
from django.core.management.base import BaseCommand
from control.models import Operador, Recinto, Monitor, Soporte, Coordinador


def limpiar(texto):
    if not texto:
        return None
    return texto.strip()


class Command(BaseCommand):
    help = "Importa operadores desde CSV"

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str)

    def handle(self, *args, **kwargs):
        archivo = kwargs["archivo"]

        # Precargar datos
        recintos_map = {r.codigo: r for r in Recinto.objects.all() if r.codigo}

        monitores_map = {m.id: m for m in Monitor.objects.all()}
        soportes_map = {s.id: s for s in Soporte.objects.all()}
        coordinadores_map = {c.id: c for c in Coordinador.objects.all()}

        total = 0
        creados = 0
        actualizados = 0
        errores = []

        with open(archivo, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            # normalizar encabezados
            reader.fieldnames = [f.strip().lower() for f in reader.fieldnames]

            for row in reader:
                row = {k.strip().lower(): v.strip() for k, v in row.items()}

                nombre = limpiar(row.get("nombre"))
                ap_p = limpiar(row.get("apellido_paterno"))
                ap_m = limpiar(row.get("apellido_materno"))
                ci = limpiar(row.get("ci"))
                celular = limpiar(row.get("celular"))

                codigo = limpiar(row.get("codigo"))
                monitor_id = limpiar(row.get("monitor_id"))
                soporte_id = limpiar(row.get("soporte_id"))
                coordinador_id = limpiar(row.get("coordinador_id")) 

                if not ci:
                    errores.append(f"Fila sin CI: {row}")
                    continue

                # 🔗 Relaciones
                recinto = recintos_map.get(codigo)
                monitor = monitores_map.get(int(monitor_id)) if monitor_id else None
                soporte = soportes_map.get(int(soporte_id)) if soporte_id else None
                coordinador = coordinadores_map.get(int(coordinador_id)) if coordinador_id else None

                if codigo and not recinto:
                    errores.append(f"Recinto no encontrado: {codigo}")

                # Crear o actualizar
                obj, created = Operador.objects.update_or_create(
                    ci=ci,
                    defaults={
                        "nombre": nombre,
                        "apellido_paterno": ap_p,
                        "apellido_materno": ap_m,
                        "celular": celular,
                        "recinto": recinto,
                        "monitor": monitor,
                        "soporte": soporte,
                        "coordinador": coordinador,
                    }
                )

                if created:
                    creados += 1
                else:
                    actualizados += 1

                total += 1

                if total % 100 == 0:
                    self.stdout.write(f"Procesados: {total}")

        self.stdout.write(f"Total: {total}")
        self.stdout.write(f"Creados: {creados}")
        self.stdout.write(f"Actualizados: {actualizados}")

        if errores:
            self.stdout.write(self.style.WARNING("Errores:"))
            for e in errores[:20]:  # limitar salida
                self.stdout.write(f"- {e}")