from django.urls import path
from info import views as info_views

urlpatterns = [
    path('', info_views.inicio, name='info'),
    path('uniformes', info_views.uniformes, name='uniformes'),
    path('accidentes', info_views.accidentes, name='accidentes'),
    path('permisos', info_views.permisos, name='permisos'),
    path('requisitos_ips', info_views.requisitos_ips, name='requisitos_ips'),
    path('jubilacion', info_views.jubilacion, name='jubilacion'),
    path('reposo', info_views.reposo, name='reposo'),
    path('reposo_particular', info_views.reposo_particular, name='reposo_particular'),
    path('maternidad', info_views.maternidad, name='maternidad'),
    path('escolar', info_views.escolar, name='escolar'),
    path('fallecimiento', info_views.fallecimiento, name='fallecimiento'),
    path('bonificaciones', info_views.bonificaciones, name='bonificaciones'),
    path('talles', info_views.talles, name='talles'),
    path('procesar_imagen/', info_views.procesar_imagen, name='procesar_imagen'),
]
