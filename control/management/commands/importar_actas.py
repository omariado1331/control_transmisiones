import csv
import unicodedata

from django.core.management.base import BaseCommand
from control.models import Acta, Recinto

# para activar el comando


def normalizar(texto):
    if not texto:
        return ""
    texto = texto.strip().lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


class Command(BaseCommand):
    help = "Importa actas desde CSV"

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str)

    def handle(self, *args, **kwargs):
        archivo = kwargs["archivo"]

        # 🔥 Cargar recintos en memoria (rápido)
        recintos_map = {
            normalizar(r.nombre): r
            for r in Recinto.objects.all()
        }

        total = 0
        creados = 0
        existentes = 0
        no_encontrados = []

        with open(archivo, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            # Normalizar encabezados
            reader.fieldnames = [f.strip().lower() for f in reader.fieldnames]

            for row in reader:
                row = {k.strip().lower(): v.strip() for k, v in row.items()}

                numero = row.get("numero")
                nombre_recinto = normalizar(row.get("recinto"))

                if not numero or not nombre_recinto:
                    self.stdout.write(f"Fila inválida: {row}")
                    continue

                recinto = recintos_map.get(nombre_recinto)

                if not recinto:
                    no_encontrados.append(nombre_recinto)
                    continue

                obj, created = Acta.objects.get_or_create(
                    numero=numero,
                    defaults={"recinto": recinto}
                )

                if created:
                    creados += 1
                else:
                    existentes += 1

                total += 1

                if total % 100 == 0:
                    self.stdout.write(f"Procesados: {total}")

        self.stdout.write(f"Total procesados: {total}")
        self.stdout.write(f"Creados: {creados}")
        self.stdout.write(f"Existentes: {existentes}")

        if no_encontrados:
            self.stdout.write(self.style.WARNING("Recintos no encontrados:"))
            for r in set(no_encontrados):
                self.stdout.write(f"- {r}")