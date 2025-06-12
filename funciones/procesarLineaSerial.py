from .filtroMediaMovil import filtroMediaMovil
import time

def procesarLineaSerial(linea, tamanoVentana,
                        bufferTiempo, bufferServoH, bufferServoV,
                        bufferLdrTl, bufferLdrTr, bufferLdrBl, bufferLdrBr,
                        bufferLdrTlFiltrado, bufferLdrTrFiltrado,
                        bufferLdrBlFiltrado, bufferLdrBrFiltrado):
    if linea.startswith('Horizontal'):
        return False  
    
    datos = linea.split(',')
    if len(datos) == 6:

        #covierte los datos a enteros
        servoH, servoV, ldrTl, ldrTr, ldrBl, ldrBr = map(int, datos)

        bufferTiempo.append(time.time()) 

        #pocisiones de los servos
        bufferServoH.append(servoH)
        bufferServoV.append(servoV)

        #valores sin filtrar
        bufferLdrTl.append(ldrTl)
        bufferLdrTr.append(ldrTr)
        bufferLdrBl.append(ldrBl)
        bufferLdrBr.append(ldrBr)

        #valores filtrados
        ldrTlFiltrado = filtroMediaMovil(bufferLdrTl, tamanoVentana)
        ldrTrFiltrado = filtroMediaMovil(bufferLdrTr, tamanoVentana)
        ldrBlFiltrado = filtroMediaMovil(bufferLdrBl, tamanoVentana)
        ldrBrFiltrado = filtroMediaMovil(bufferLdrBr, tamanoVentana)

        #guarda valores filtrados
        bufferLdrTlFiltrado.append(ldrTlFiltrado)
        bufferLdrTrFiltrado.append(ldrTrFiltrado)
        bufferLdrBlFiltrado.append(ldrBlFiltrado)
        bufferLdrBrFiltrado.append(ldrBrFiltrado)

        return True
    return False