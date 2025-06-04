import numpy as np

def filtroMediaMovil(datos, tamanoVentana):
    if len(datos) < tamanoVentana:
        return np.mean(datos)  # Si no hay suficientes datos, devuelve el promedio actual
    else:
        return np.mean(list(datos)[-tamanoVentana:])
