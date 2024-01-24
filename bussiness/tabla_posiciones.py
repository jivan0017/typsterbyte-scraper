class TablaPosiciones():

    def transcribir_partidos_jugados(self, resultado):
        retorno_numerico = None
        
        if resultado == 'G' or resultado == 'W' or resultado == 'w':
            retorno_numerico = 1
        elif resultado == 'E' or resultado == 'D' or resultado == 'd':
            retorno_numerico = 0
        elif resultado == 'P' or resultado == 'L' or resultado == 'l':
            retorno_numerico = -1

        return retorno_numerico