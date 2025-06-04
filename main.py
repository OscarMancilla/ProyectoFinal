# main.py
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys
import platform
from matplotlib.patches import Rectangle

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

# Cuadro de texto para servos
servo_text = fig.text(0.85, 0.7, '', color='white', bbox=dict(facecolor='#333333', edgecolor='white', boxstyle='round'))

# Marca Oscarm
fig.text(0.85, 0.05, 'Oscarm', color='white', fontsize=12, style='italic', bbox=dict(facecolor='#333333', alpha=0.5))

def inicializar():
    inicializarGrafica(ax1, ax2, maxPuntos)
    return (lineaLdrTl, lineaLdrTr, lineaLdrBl, lineaLdrBr,
            lineaLdrTlFiltrado, lineaLdrTrFiltrado, lineaLdrBlFiltrado, lineaLdrBrFiltrado)

def actualizar(frame):
    if ser is None:
        return (lineaLdrTl, lineaLdrTr, lineaLdrBl, lineaLdrBr,
                lineaLdrTlFiltrado, lineaLdrTrFiltrado, lineaLdrBlFiltrado, lineaLdrBrFiltrado)

    while ser.in_waiting:
        try:
            linea = ser.readline().decode('utf-8').strip()
            procesado = procesarLineaSerial(linea, tamanoVentana,
                bufferTiempo, bufferServoH, bufferServoV,
                bufferLdrTl, bufferLdrTr, bufferLdrBl, bufferLdrBr,
                bufferLdrTlFiltrado, bufferLdrTrFiltrado,
                bufferLdrBlFiltrado, bufferLdrBrFiltrado)

            if procesado:
                # Actualizar gráficas
                lineaLdrTl.set_data(range(len(bufferLdrTl)), bufferLdrTl)
                lineaLdrTr.set_data(range(len(bufferLdrTr)), bufferLdrTr)
                lineaLdrBl.set_data(range(len(bufferLdrBl)), bufferLdrBl)
                lineaLdrBr.set_data(range(len(bufferLdrBr)), bufferLdrBr)

                lineaLdrTlFiltrado.set_data(range(len(bufferLdrTlFiltrado)), bufferLdrTlFiltrado)
                lineaLdrTrFiltrado.set_data(range(len(bufferLdrTrFiltrado)), bufferLdrTrFiltrado)
                lineaLdrBlFiltrado.set_data(range(len(bufferLdrBlFiltrado)), bufferLdrBlFiltrado)
                lineaLdrBrFiltrado.set_data(range(len(bufferLdrBrFiltrado)), bufferLdrBrFiltrado)

                # Actualizar cuadro de servos
                if bufferServoH and bufferServoV:
                    servo_text.set_text(f'Servo Horizontal:\n{bufferServoH[-1]}°\n\nServo Vertical:\n{bufferServoV[-1]}°')

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
