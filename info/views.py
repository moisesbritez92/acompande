from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import datetime


def inicio(request):
    return render(request, 'info.html')

def uniformes(request):
    return render(request, 'uniformes.html')

def accidentes(request):
    return render(request, 'accidentes.html')

def permisos(request):
    return render(request, 'permisos.html')

def requisitos_ips(request):
    return render(request, 'requisitos_ips.html')

def jubilacion(request):
    return render(request, 'jubilacion.html')

def reposo(request):
    return render(request, 'reposo.html')

def reposo_particular(request):
    return render(request, 'reposo_particular.html')

def maternidad(request):
    return render(request, 'maternidad.html')

def escolar(request):
    return render(request, 'escolar.html')

def fallecimiento(request):
    return render(request, 'fallecimiento.html')

def bonificaciones(request):
    return render(request, 'bonificaciones.html')

def talles(request):
    return render(request, 'estimar.html')


import cv2
import numpy as np
import mediapipe as mp
import base64
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def procesar_imagen(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['image']
        altura_usuario_cm = float(data.get('altura', 170))  # Altura por defecto 170 cm
        # Decodificar la imagen base64
        format, imgstr = image_data.split(';base64,')
        nparr = np.frombuffer(base64.b64decode(imgstr), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Procesar la imagen para estimar el talle y obtener la imagen con puntos
        talle, img_con_puntos = estimar_talle(img, altura_usuario_cm)

        # Codificar la imagen con puntos a base64 para enviarla al frontend
        _, buffer = cv2.imencode('.jpg', img_con_puntos)
        img_con_puntos_base64 = base64.b64encode(buffer).decode('utf-8')
        img_con_puntos_data_url = 'data:image/jpeg;base64,' + img_con_puntos_base64

        return JsonResponse({'talle': talle, 'imagen': img_con_puntos_data_url})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def estimar_talle(img, altura_usuario_cm=170):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    # Convertir la imagen a RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        # Dibujar los puntos clave y conexiones en la imagen
        img_con_puntos = img.copy()
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(
            img_con_puntos,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )

        # El resto del código para calcular el talle...
        landmarks = results.pose_landmarks.landmark

        # Función para convertir coordenadas normalizadas a píxeles
        def coord_to_pixel(landmark):
            return int(landmark.x * img.shape[1]), int(landmark.y * img.shape[0])

        # Obtener coordenadas en píxeles
        hombro_izq_px = coord_to_pixel(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER])
        hombro_der_px = coord_to_pixel(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER])
        cadera_izq_px = coord_to_pixel(landmarks[mp_pose.PoseLandmark.LEFT_HIP])
        cadera_der_px = coord_to_pixel(landmarks[mp_pose.PoseLandmark.RIGHT_HIP])
        tobillo_izq_px = coord_to_pixel(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE])
        cabeza_px = coord_to_pixel(landmarks[mp_pose.PoseLandmark.NOSE])

        # Calcular altura de la persona en píxeles (de la cabeza al tobillo)
        altura_persona_px = calcular_distancia(cabeza_px, tobillo_izq_px)

        # Calcular escala píxeles a centímetros
        escala_px_cm = altura_persona_px / altura_usuario_cm

        # Calcular anchura de hombros y caderas en centímetros
        anchura_hombros_cm = calcular_distancia(hombro_izq_px, hombro_der_px) / escala_px_cm
        anchura_caderas_cm = calcular_distancia(cadera_izq_px, cadera_der_px) / escala_px_cm

        # Calcular circunferencia del pecho (aproximada)
        circunferencia_pecho_cm = anchura_hombros_cm * 2.0  # Ajuste el factor según sea necesario

        # Determinar el talle basado en medidas estándar
        if circunferencia_pecho_cm < 60:
            talle = 'S'
        elif circunferencia_pecho_cm < 80:
            talle = 'M'
        elif circunferencia_pecho_cm < 90:
            talle = 'L'
        else:
            talle = 'XL'

        return talle, img_con_puntos
    else:
        return 'No se pudieron detectar los puntos clave.', img

def calcular_distancia(punto1, punto2):
    x1, y1 = punto1
    x2, y2 = punto2
    distancia = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distancia
