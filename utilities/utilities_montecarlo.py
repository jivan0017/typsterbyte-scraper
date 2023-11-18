class UtilitiesMontecarlo():
    
    acents: str
    witout_acents: str
    transform: str
    
    def __init__(self):
        self.acents, self.witout_acents = 'áéíóúüÁÉÍÓÚÜ', 'aeiouuAEIOUU'
        self.transform = str.maketrans(self.acents, self.witout_acents)
        
    def retornar_cadena_sin_acento(self, cadena_in: str):
        return cadena_in.translate(self.transform)