# main.py
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys
import platform
from matplotlib.patches import Rectangle
import random  # Para añadir ruido

from funciones import (
    filtroMediaMovil,
    inicializarGrafica,
    procesarLineaSerial
)

# Determinar puerto según sistema operativo
if platform.system() == "Linux":
    puerto_serial = '/dev/ttyACM0'
else:
    puerto_serial = 'COM3'

# Configuración del puerto serial con manejo de errores
try:
    ser = serial.Serial(puerto_serial, 115200, timeout=1)
    ser.flushInput()
except serial.SerialException as e:
    print(f"No se pudo abrir el puerto serial: {e}")
    ser = None

tamanoVentana = 5
maxPuntos = 100

# Configurar estilo oscuro
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='#1a1a1a')
fig.suptitle('Monitor de Señales del Seguidor Solar', fontsize=14, color='white')

# Buffers de datos
bufferTiempo = deque(maxlen=maxPuntos)
bufferServoH = deque(maxlen=maxPuntos)
bufferServoV = deque(maxlen=maxPuntos)

bufferLdrTl = deque(maxlen=maxPuntos)
bufferLdrTr = deque(maxlen=maxPuntos)
bufferLdrBl = deque(maxlen=maxPuntos)
bufferLdrBr = deque(maxlen=maxPuntos)

bufferLdrTlFiltrado = deque(maxlen=maxPuntos)
bufferLdrTrFiltrado = deque(maxlen=maxPuntos)
bufferLdrBlFiltrado = deque(maxlen=maxPuntos)
bufferLdrBrFiltrado = deque(maxlen=maxPuntos)

# Líneas gráficas (originales arriba, filtradas abajo)
lineaLdrTl, = ax1.plot([], [], 'lime', label='LDR Top Left')
lineaLdrTr, = ax1.plot([], [], 'cyan', label='LDR Top Right')
lineaLdrBl, = ax1.plot([], [], 'magenta', label='LDR Bottom Left')
lineaLdrBr, = ax1.plot([], [], 'yellow', label='LDR Bottom Right')

lineaLdrTlFiltrado, = ax2.plot([], [], 'lime', linestyle='--', label='LDR Top Left (Filtrado)')
lineaLdrTrFiltrado, = ax2.plot([], [], 'cyan', linestyle='--', label='LDR Top Right (Filtrado)')
lineaLdrBlFiltrado, = ax2.plot([], [], 'magenta', linestyle='--', label='LDR Bottom Left (Filtrado)')
lineaLdrBrFiltrado, = ax2.plot([], [], 'yellow', linestyle='--', label='LDR Bottom Right (Filtrado)')

# Cuadro de texto para servos - Posición ajustada más a la derecha y arriba
servo_box_props = dict(boxstyle='round', facecolor='#333333', edgecolor='white', alpha=0.9)
servo_text = fig.text(0.88, 0.65,  # Cambiado de 0.85, 0.5 a 0.88, 0.65
                     'Posición de Servomotores:\n\n'
                     'Horizontal: --°\n'
                     'Vertical: --°', 
                     color='white', 
                     bbox=servo_box_props,
                     fontsize=11,
                     verticalalignment='center',
                     horizontalalignment='center')

# Indicador de estado de conexión
status_text = fig.text(0.88, 0.55,  # Ajustado para mantener relación con servo_text
                      'Estado: Conectado' if ser else 'Estado: Desconectado',
                      color='lime' if ser else 'red',
                      bbox=dict(boxstyle='round', facecolor='#333333', alpha=0.7),
                      fontsize=10)

# Marca Oscarm
fig.text(0.88, 0.05, 'Oscarm', color='white', fontsize=12, style='italic', 
         bbox=dict(facecolor='#333333', alpha=0.5))

def inicializar():
    inicializarGrafica(ax1, ax2, maxPuntos)
    return (lineaLdrTl, lineaLdrTr, lineaLdrBl, lineaLdrBr,
            lineaLdrTlFiltrado, lineaLdrTrFiltrado, lineaLdrBlFiltrado, lineaLdrBrFiltrado)

def actualizar(frame):
    if ser is None:
        status_text.set_text('Estado: Desconectado')
        status_text.set_color('red')
        return (lineaLdrTl, lineaLdrTr, lineaLdrBl, lineaLdrBr,
                lineaLdrTlFiltrado, lineaLdrTrFiltrado, lineaLdrBlFiltrado, lineaLdrBrFiltrado)

    status_text.set_text('Estado: Conectado')
    status_text.set_color('lime')

    while ser.in_waiting:
        try:
            linea = ser.readline().decode('utf-8').strip()
            procesado = procesarLineaSerial(linea, tamanoVentana,
                bufferTiempo, bufferServoH, bufferServoV,
                bufferLdrTl, bufferLdrTr, bufferLdrBl, bufferLdrBr,
                bufferLdrTlFiltrado, bufferLdrTrFiltrado,
                bufferLdrBlFiltrado, bufferLdrBrFiltrado)

            if procesado:
                # Añadir ruido a las señales originales (entre -20 y +20)
                bufferLdrTl_noisy = [x + random.randint(-20, 20) for x in bufferLdrTl]
                bufferLdrTr_noisy = [x + random.randint(-20, 20) for x in bufferLdrTr]
                bufferLdrBl_noisy = [x + random.randint(-20, 20) for x in bufferLdrBl]
                bufferLdrBr_noisy = [x + random.randint(-20, 20) for x in bufferLdrBr]

                # Actualizar gráficas con señales ruidosas
                lineaLdrTl.set_data(range(len(bufferLdrTl)), bufferLdrTl_noisy)
                lineaLdrTr.set_data(range(len(bufferLdrTr)), bufferLdrTr_noisy)
                lineaLdrBl.set_data(range(len(bufferLdrBl)), bufferLdrBl_noisy)
                lineaLdrBr.set_data(range(len(bufferLdrBr)), bufferLdrBr_noisy)

                lineaLdrTlFiltrado.set_data(range(len(bufferLdrTlFiltrado)), bufferLdrTlFiltrado)
                lineaLdrTrFiltrado.set_data(range(len(bufferLdrTrFiltrado)), bufferLdrTrFiltrado)
                lineaLdrBlFiltrado.set_data(range(len(bufferLdrBlFiltrado)), bufferLdrBlFiltrado)
                lineaLdrBrFiltrado.set_data(range(len(bufferLdrBrFiltrado)), bufferLdrBrFiltrado)

                # Actualizar cuadro de servos con formato mejorado
                if bufferServoH and bufferServoV:
                    servo_text.set_text(
                        'Posición de Servomotores:\n\n'
                        f'Horizontal: {bufferServoH[-1]:.1f}°\n'
                        f'Vertical: {bufferServoV[-1]:.1f}°'
                    )
                    fig.canvas.draw_idle()  # Fuerza la actualización de la figura

                if len(bufferLdrTl) >= maxPuntos:
                    ax1.set_xlim(len(bufferLdrTl) - maxPuntos, len(bufferLdrTl))
                    ax2.set_xlim(len(bufferLdrTlFiltrado) - maxPuntos, len(bufferLdrTlFiltrado))

        except Exception as e:
            print(f"Error durante lectura: {e}")

    return (lineaLdrTl, lineaLdrTr, lineaLdrBl, lineaLdrBr,
            lineaLdrTlFiltrado, lineaLdrTrFiltrado, lineaLdrBlFiltrado, lineaLdrBrFiltrado)

ani = FuncAnimation(fig, actualizar, init_func=inicializar, blit=True, interval=50)

plt.tight_layout()
plt.subplots_adjust(right=0.8)  # Ajustar para el cuadro de servos
plt.show()

# Cierre del puerto
if ser is not None:
    ser.close()
