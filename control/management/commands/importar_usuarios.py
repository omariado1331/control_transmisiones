import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from control.models import Soporte, Monitor, Coordinador
import unicodedata
import re

def generar_username(nombre, apellido_paterno):
    # primer nombre
    primer_nombre = nombre.strip().split()[0]
    # quitar tildes
    def quitar_tildes(texto):
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

    primer_nombre = quitar_tildes(primer_nombre)
    apellido_paterno = quitar_tildes(apellido_paterno)
    # minúsculas
    username = f"{primer_nombre}.{apellido_paterno}".lower()
    # quitar caracteres raros
    username = re.sub(r'[^a-z0-9.]', '', username)

    return username

def username_unico(base_username):
    username = base_username
    contador = 1

    while User.objects.filter(username=username).exists():
        username = f"{base_username}{contador}"
        contador += 1

    return username

class Command(BaseCommand):
    help = 'Importar desde CSV'

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str)
        parser.add_argument("grupo", type=str)
    
    def handle(self, *args, **kwargs):
        archivo = kwargs["archivo"]
        grupo_nombre = kwargs["grupo"]

        grupo = Group.objects.get(name=grupo_nombre)

        modelo_map = {
            "Soporte": Soporte,
            "Monitor": Monitor,
            "Coordinador": Coordinador
        }

        modelo = modelo_map.get(grupo_nombre)

        if not modelo:
            self.stdout.write(self.style.ERROR("Grupo no valido"))
            return

        with open(archivo, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader.fieldnames)
            for row in reader:
                nombre = row['nombre']
                apellido_paterno = row['apellido_paterno']
                apellido_materno = row['apellido_materno']
                ci = row['ci']
                celular = row['celular']
                base_username = generar_username(nombre, apellido_paterno)
                username = username_unico(base_username)
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": nombre,
                        "is_staff": True
                    }
                )

                if created:
                    user.set_password("Sirepre2025") 
                    user.save()

                user.groups.add(grupo)

                modelo.objects.get_or_create(
                    user=user,
                    defaults={
                        "nombre": nombre,
                        "apellido_paterno": apellido_paterno,
                        "apellido_materno": apellido_materno,
                        "ci": ci,
                        "celular": celular,
                    }
                )

                self.stdout.write(f"Usuario procesado: {ci}")

        self.stdout.write(self.style.SUCCESS("Importación completada"))
