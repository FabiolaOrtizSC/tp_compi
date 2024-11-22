from django.shortcuts import render
from .forms import ArchivoForm, LexemaForm
from .models import Archivo, Lexema
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
import io
import re

# Create your views here.

def home(request):
    return render(request,'base/home.html')

class ArchivoCreateView(CreateView):
    model = Archivo
    form_class = ArchivoForm
    template_name = 'base/archivo_create.html'
    success_url = reverse_lazy('base:archivo_list')  # Redirige a una lista de archivos o a otra página después de subir el archivo

class ArchivoListView(ListView):
    model = Archivo
    template_name = 'base/archivo_list.html'  # Ruta de la plantilla
    context_object_name = 'archivo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtiene el último archivo subido
        archivo = Archivo.objects.last()
        contenido = None

        # Lee el contenido del archivo si es un archivo de texto
        if archivo and archivo.archivo.name.endswith('.txt'):
            try:
                # Usa io.open() para abrir el archivo con la codificación correcta
                with archivo.archivo.open('rb') as f:  # 'rb' para leer como binario
                    contenido = io.TextIOWrapper(f, encoding='utf-8').read()  # Decodificación manual
            except UnicodeDecodeError:
                # Si no se puede decodificar en utf-8, intenta con ISO-8859-1
                with archivo.archivo.open('rb') as f:
                    contenido = io.TextIOWrapper(f, encoding='ISO-8859-1').read()

        # Procesar el contenido
        if contenido:
            # 1. Contenido en minúsculas
            contenido_completo = contenido.lower()

            # 2. Contenido solo del agente: extraemos texto entre [agente] y [cliente]
            contenido_agente = self.extraer_contenido_agente(contenido_completo)
            
            # 3. Contenido sin símbolos: eliminamos todo lo que no sea alfanumérico o espacios
            contenido_palabras = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]', '', contenido_completo)

            # Dividir el contenido en una lista de palabras
            palabras = contenido_palabras.split()

            reporte_sentimiento = self.analizar_sentimiento(palabras)
            protocolo_ok = self.verificar_protocolo(contenido_agente)
            
            # Agregar al contexto
            context['reporte_protocolo'] = protocolo_ok
            context['reporte_sentimiento'] = reporte_sentimiento
            context['contenido'] = contenido
        return context

    def extraer_contenido_agente(self, contenido_completo):
        # Utilizamos expresiones regulares para extraer todo el texto entre [agente] y [cliente]
        patron = r'\[agente\](.*?)\[cliente\]'
        
        # re.findall busca todas las coincidencias y las devuelve como una lista
        contenido_agente = re.findall(patron, contenido_completo, re.DOTALL)  # re.DOTALL permite que el . coincida con saltos de línea
        
        # Si encontramos alguna coincidencia, concatenamos todo lo que el agente ha dicho
        if contenido_agente:
            return " ".join([fragmento.strip() for fragmento in contenido_agente])
        
        return ""  # Si no hay contenido del agente, devolver una cadena vacía
    
    def verificar_protocolo(self, contenido_agente):
        protocolo_ok = {
            "saludo": 'Faltante',
            "identificacion_cliente": 'Faltante',
            "palabras_no_permitidas": 'Ninguna detectada',
            "despedida": 'Faltante'
        }

        # Verificar cada categoría de protocolo
        for lexema in Lexema.objects.filter(token='saludo'):
            if lexema.lexema in contenido_agente:
                protocolo_ok["saludo"] = 'Cumplido'
                break

        for lexema in Lexema.objects.filter(token='identificacion_cliente'):
            if lexema.lexema in contenido_agente:
                protocolo_ok["identificacion_cliente"] = 'Cumplido'
                break

        for lexema in Lexema.objects.filter(token='palabras_no_permitidas'):
            if lexema.lexema in contenido_agente:
                protocolo_ok["palabras_no_permitidas"] = 'Palabra no permitida detectada'
                break

        for lexema in Lexema.objects.filter(token='despedida'):
            if lexema.lexema in contenido_agente:
                protocolo_ok["despedida"] = 'Cumplido'
                break

        return protocolo_ok

    def analizar_sentimiento(self, palabras):
        puntuacion_total = 0
        palabras_positivas = []
        palabras_negativas = []
        palabra_mas_positiva = ("", 0)
        palabra_mas_negativa = ("", 0)
        
        # Iterar sobre cada palabra en el contenido
        for palabra in palabras:
            # Buscar el lexema correspondiente en la base de datos
            lexema = Lexema.objects.filter(lexema=palabra).first()  # Busca el lexema exacto

            if lexema:
                print(lexema)
                puntuacion = lexema.ponderacion  # Obtiene la ponderación del lexema encontrado
                puntuacion_total += puntuacion  # Sumar la puntuación total
                
                # Si la puntuación es positiva, la agregamos a la lista de palabras positivas
                if puntuacion > 0:
                    palabras_positivas.append((palabra, puntuacion))
                    if puntuacion > palabra_mas_positiva[1]:
                        palabra_mas_positiva = (palabra, puntuacion)
                # Si la puntuación es negativa, la agregamos a la lista de palabras negativas
                elif puntuacion < 0:
                    palabras_negativas.append((palabra, puntuacion))
                    if puntuacion < palabra_mas_negativa[1]:
                        palabra_mas_negativa = (palabra, puntuacion)
        
        sentimiento_general = "Neutral (0)"
        if puntuacion_total > 0:
            sentimiento_general = f"Positivo (+{puntuacion_total})"
        elif puntuacion_total < 0:
            sentimiento_general = f"Negativo ({puntuacion_total})"
        
        reporte = {
            "sentimiento_general": sentimiento_general,
            "palabras_positivas": len(palabras_positivas),
            "palabra_mas_positiva": palabra_mas_positiva if palabra_mas_positiva[1] != 0 else None,
            "palabras_negativas": len(palabras_negativas),
            "palabra_mas_negativa": palabra_mas_negativa if palabra_mas_negativa[1] != 0 else None
        }
        
        return reporte


# Vista para listar los lexemas
class LexemaListView(ListView):
    model = Lexema
    template_name = 'base/lexema_list.html'  # Plantilla para mostrar la lista
    context_object_name = 'lexemas'

# Vista para crear un lexema
class LexemaCreateView(CreateView):
    model = Lexema
    form_class = LexemaForm
    template_name = 'base/lexema_create.html'
    success_url = reverse_lazy('base:lexema_list')  # Redirige a la lista después de crear

# # Vista para editar un lexema
# class LexemaUpdateView(UpdateView):
#     model = Lexema
#     form_class = LexemaForm
#     template_name = 'base/lexema_form.html'
#     success_url = reverse_lazy('base:lexema_list')  # Redirige a la lista después de actualizar

# # Vista para eliminar un lexema
# class LexemaDeleteView(DeleteView):
#     model = Lexema
#     template_name = 'base/lexema_confirm_delete.html'  # Plantilla de confirmación de eliminación
#     success_url = reverse_lazy('base:lexema_list')  # Redirige a la lista después de eliminar