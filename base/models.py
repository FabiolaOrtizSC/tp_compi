from django.db import models

# Create your models here.

class Archivo(models.Model):
    archivo = models.FileField(upload_to='archivos/')  # Define la ruta de almacenamiento
    fecha_subida = models.DateTimeField(auto_now_add=True)  # Fecha de subida del archivo

    def __str__(self):
        return self.archivo.name

class Lexema(models.Model):
    # Definición de las categorías posibles
    TOKENS = [
        ('saludo', 'Saludo'),
        ('despedida', 'Despedida'),
        ('identificacion_cliente', 'Identificación Cliente'),
        ('bueno', 'Bueno'),
        ('amable', 'Amable'),
        ('problema', 'Problema'),
        ('mal', 'Mal'),
        ('excelente', 'Excelente'),
        ('fatal', 'Fatal'),
    ]
    
    lexema = models.CharField(max_length=100, unique=True)
    token = models.CharField(max_length=50, choices=TOKENS)
    ponderacion = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Asegurarse de que el lexema se guarde en minúsculas
        self.lexema = self.lexema.lower()
        # Configura la ponderación en base al token antes de guardar
        if self.token == 'bueno':
            self.ponderacion = 1
        elif self.token == 'amable':
            self.ponderacion = 2
        elif self.token == 'excelente':
            self.ponderacion = 3
        elif self.token == 'problema':
            self.ponderacion = -1
        elif self.token == 'mal':
            self.ponderacion = -2
        elif self.token == 'fatal':
            self.ponderacion = -3
        else:
            self.ponderacion = 0  # Para saludos y despedidas o tokens neutros

        super().save(*args, **kwargs)

    def __str__(self):
        return self.lexema