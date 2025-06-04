from .filtroMediaMovil import filtroMediaMovil
import time

def procesarLineaSerial(linea, tamanoVentana,
                        bufferTiempo, bufferServoH, bufferServoV,
                        bufferLdrTl, bufferLdrTr, bufferLdrBl, bufferLdrBr,
                        bufferLdrTlFiltrado, bufferLdrTrFiltrado,
                        bufferLdrBlFiltrado, bufferLdrBrFiltrado):
    if linea.startswith('Horizontal'):
        return False  # Línea de encabezado, ignorar
    
    datos = linea.split(',')
    if len(datos) == 6:
        servoH, servoV, ldrTl, ldrTr, ldrBl, ldrBr = map(int, datos)

        bufferTiempo.append(time.time())
        bufferServoH.append(servoH)
        bufferServoV.append(servoV)

        bufferLdrTl.append(ldrTl)
        bufferLdrTr.append(ldrTr)
        bufferLdrBl.append(ldrBl)
        bufferLdrBr.append(ldrBr)

        # Aplicar filtro
        ldrTlFiltrado = filtroMediaMovil(bufferLdrTl, tamanoVentana)
        ldrTrFiltrado = filtroMediaMovil(bufferLdrTr, tamanoVentana)
        ldrBlFiltrado = filtroMediaMovil(bufferLdrBl, tamanoVentana)
        ldrBrFiltrado = filtroMediaMovil(bufferLdrBr, tamanoVentana)

        bufferLdrTlFiltrado.append(ldrTlFiltrado)
        bufferLdrTrFiltrado.append(ldrTrFiltrado)
        bufferLdrBlFiltrado.append(ldrBlFiltrado)
        bufferLdrBrFiltrado.append(ldrBrFiltrado)

        return True
    return False
