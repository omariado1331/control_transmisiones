import csv

from django.core.management.base import BaseCommand
from control.models import Acta, Operador


class Command(BaseCommand):
    help = "Asigna actas a operadores desde CSV"

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str)

    def handle(self, *args, **kwargs):
        archivo = kwargs["archivo"]

        # Precargar operadores
        operadores_map = {
            o.ci: o for o in Operador.objects.all()
        }

        # Precargar actas
        actas_map = {
            a.numero: a for a in Acta.objects.all()
        }

        total = 0
        asignadas = 0
        no_encontradas = []
        operadores_no_encontrados = []

        with open(archivo, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            # normalizar encabezados
            reader.fieldnames = [f.strip() for f in reader.fieldnames]
            actas_para_actualizar = []
            
            for row in reader:
                ci = row.get("ci")

                operador = operadores_map.get(ci)

                if not operador:
                    operadores_no_encontrados.append(ci)
                    continue

                # recorrer A1 a A14
                for i in range(1, 15):
                    key = f"A{i}"
                    numero_acta = row.get(key)

                    if not numero_acta:
                        continue

                    numero_acta = numero_acta.strip()

                    acta = actas_map.get(numero_acta)

                    if not acta:
                        no_encontradas.append(numero_acta)
                        continue

                    # asignar operador
                    if acta.operador_id != operador.id:
                        acta.operador = operador
                        actas_para_actualizar.append(acta)
                        asignadas += 1

                total += 1

                if total % 50 == 0:
                    self.stdout.write(f"Procesados: {total}")

                BATCH_SIZE = 1000
                if len(actas_para_actualizar) >= BATCH_SIZE:
                    Acta.objects.bulk_update(actas_para_actualizar, ['operador']) 
                    actas_para_actualizar.clear()
                    
            if actas_para_actualizar:
                Acta.objects.bulk_update(actas_para_actualizar, ['operador'])
        
        # resumen
        self.stdout.write(f"Filas procesadas: {total}")
        self.stdout.write(f"Actas asignadas: {asignadas}")

        if no_encontradas:
            self.stdout.write(self.style.WARNING("Actas no encontradas:"))
            for a in set(no_encontradas):
                self.stdout.write(f"- {a}")

        if operadores_no_encontrados:
            self.stdout.write(self.style.WARNING("Operadores no encontrados:"))
            for o in set(operadores_no_encontrados):
                self.stdout.write(f"- {o}")