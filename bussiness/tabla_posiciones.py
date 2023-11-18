class TablaPosiciones():

    def transcribir_partidos_jugados(self, resultado):
        retorno_numerico = None
        
        if resultado == 'G':
            retorno_numerico = 1
        elif resultado == 'E':
            retorno_numerico = 0
        elif resultado == 'P':
            retorno_numerico = -1

        return retorno_numerico