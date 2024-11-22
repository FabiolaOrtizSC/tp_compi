from django.urls import path
from base import views
from .views import *

# TEMPLATE TAGGING
app_name = 'base'

urlpatterns = [
    path('archivo_list/', ArchivoListView.as_view(), name='archivo_list'),
    path('archivo_create/', ArchivoCreateView.as_view(), name='archivo_create'),
    # path('<int:pk>/delete/', ArchivoDeleteView.as_view(), name='archivo_delete'),
    path('lexema_list/', views.LexemaListView.as_view(), name='lexema_list'),
    path('lexema_create/', views.LexemaCreateView.as_view(), name='lexema_create'),
    # path('lexema/<int:pk>/update/', views.LexemaUpdateView.as_view(), name='lexema_update'),
    # path('lexema/<int:pk>/delete/', views.LexemaDeleteView.as_view(), name='lexema_delete'),
]