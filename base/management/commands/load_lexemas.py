from django.core.management.base import BaseCommand
from base.models import Lexema

class Command(BaseCommand):
    help = 'Carga masiva de lexemas desde un archivo de texto'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str)

    def handle(self, *args, **kwargs):
        archivo = kwargs['archivo']
        with open(archivo, 'r', encoding='utf-8') as f:
            for line in f:
                lexema, token, ponderacion = line.strip().split(',')
                Lexema.objects.create(
                    lexema=lexema.lower(),  # Guarda el lexema en minúsculas
                    token=token,
                    ponderacion=ponderacion
                )
        self.stdout.write(self.style.SUCCESS('Lexemas cargados correctamente.'))