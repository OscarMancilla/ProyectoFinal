import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys
import platform
from funciones import  filtroMediaMovil,inicializarGrafica,procesarLineaSerial
import random  # Para añadir ruido

#ACLARACION DE VARIABLES 
#Top Left = Arriba a la Izquierda
#Top Right = Arriba a la Derecha
#Bottom Left = Abajo a la Izquierda
#Bottom Right = Abajo a la derecha




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
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), facecolor='#1a1a1a')
fig.subplots_adjust(top=0.88)
fig.suptitle('Monitor de Señales del Seguidor Solar',fontsize=15, color='white', fontweight='bold', y=0.98)



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
lineaLdrTl, = ax1.plot([], [], 'lime', label='LDR Superior a la Izquierda')
lineaLdrTr, = ax1.plot([], [], 'cyan', label='LDR Superior a la Derecha')
lineaLdrBl, = ax1.plot([], [], 'magenta', label='LDR Inferior a la Izquierda')
lineaLdrBr, = ax1.plot([], [], 'yellow', label='LDR Inferior a la Derecha')

lineaLdrTlFiltrado, = ax2.plot([], [], 'lime', linestyle='--', label='LDR Superior a la Izquierda')
lineaLdrTrFiltrado, = ax2.plot([], [], 'cyan', linestyle='--', label='LDR Superior a la Derecha')
lineaLdrBlFiltrado, = ax2.plot([], [], 'magenta', linestyle='--', label='LDR Inferior a la Izquierda')
lineaLdrBrFiltrado, = ax2.plot([], [], 'yellow', linestyle='--', label='LDR Inferior a la Derecha')

# Cuadro de texto para servos 
servo_box_props = dict(boxstyle='round', facecolor='#333333', edgecolor='white', alpha=0.5)
servo_text = fig.text(0.90, 0.86,  
                     'Posición de Servomotores:\n\n'
                     'Horizontal: --°\n'
                     'Vertical: --°', 
                     color='white', 
                     bbox=servo_box_props,
                     fontsize=11,
                     verticalalignment='center',
                     horizontalalignment='center')

# Indicador de estado de conexión
Estado = fig.text(0.88, 0.79,  
                      'Estado: Conectado' if ser else 'Estado: Desconectado',
                      color='lime' if ser else 'red',
                      bbox=dict(boxstyle='round', facecolor='#333333', alpha=0.5),
                      fontsize=10)


def inicializar():
    inicializarGrafica(ax1, ax2, maxPuntos)
    return (lineaLdrTl, lineaLdrTr, lineaLdrBl, lineaLdrBr,
            lineaLdrTlFiltrado, lineaLdrTrFiltrado, lineaLdrBlFiltrado, lineaLdrBrFiltrado)

def actualizar(frame):
    if ser is None:
        Estado.set_text('Estado: Desconectado')
        Estado.set_color('red')
        return (lineaLdrTl, lineaLdrTr, lineaLdrBl, lineaLdrBr,
                lineaLdrTlFiltrado, lineaLdrTrFiltrado, lineaLdrBlFiltrado, lineaLdrBrFiltrado)

    Estado.set_text('Estado: Conectado')
    Estado.set_color('lime')

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

ani = FuncAnimation(fig, actualizar, init_func=inicializar, blit=False, interval=50, cache_frame_data=False)

plt.tight_layout()
plt.subplots_adjust(right=0.8)  # Ajustar para el cuadro de servos
plt.show()

# Cierre del puerto
if ser is not None:
    ser.close()
