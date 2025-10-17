import pandas as pd

import clips


def cargarCSV(file, templateCasilla):
    '''
    Carga un CSV con las casillas del laberinto y las inserta como hechos en el entorno CLIPS.
    
    Se debe proporcionar un archivo CSV con columnas: x, y, t, v, indicando la posición (x,y),
    el tipo de casilla (t) y un valor asociado (v). templateCasilla es el template CLIPS
    correspondiente a las casillas del laberinto que también debe tener los mismos campos.

    Parametros:
    -----------
    file : str
        Ruta al archivo CSV que contiene la definición del laberinto.
    templateCasilla : clips.Template
        Template CLIPS para las casillas del laberinto.

    Retorna:
    --------
    pd.DataFrame
        Un DataFrame de pandas con los datos cargados del CSV.  
    
    '''
    df = pd.read_csv(file)
    for index, row in df.iterrows():
        x1=row['x']
        y1=row['y']
        t1=row['t']
        v1=row['v']
        templateCasilla.assert_fact(x=x1,y=y1,tipo=t1,valor=v1)
    return df

def ImprimeLaberinto(Lab):
    '''
    Imprime el laberinto en la consola a partir de los hechos en el entorno CLIPS.
    
    Utiliza los hechos del template "Casilla" para determinar la disposición del laberinto.
    Cada casilla se imprime según su tipo, formando una representación visual del laberinto.
    
    Parametros:
    -----------
    Lab : clips.Environment
        El entorno CLIPS que contiene los hechos del laberinto.
    
    Retorna:
    --------
    None
        La función imprime directamente en la consola y no retorna ningún valor.
    '''
    X = []
    Y = []
    for f in env.facts():
        if f.template.name == "Casilla":
            X.append(f["x"])
            Y.append(f["y"])
    MaxX = max(X)
    MaxY = max(Y)
    for i in range(1, MaxX + 1):
        Lista = []
        for j in range(1, MaxY + 1):
            for f in env.facts():
                if f.template.name == "Casilla":
                    if f["x"] == i:
                        if f["y"] == j:
                            Lista.append(f["valor"])
        for e in Lista:
            print(e,end= ' ')
        print()

# Creamos el entorno CLIPS
env = clips.Environment()

# Definimos los templates necesarios

# Template para las casillas del laberinto
# Contiene las coordenadas (x,y), el tipo de casilla (tipo) y un valor asociado (valor)
templateCasilla = """(deftemplate Casilla
    (slot x (type INTEGER))
    (slot y (type INTEGER))
    (slot tipo (type STRING))
    (slot valor (type INTEGER))
    )"""

# Template para el agente
# Contiene las coordenadas (x,y) del agente en el laberinto
templateAgente = """(deftemplate Agente
    (slot x (type INTEGER))
    (slot y (type INTEGER))
    (slot valor (type INTEGER))
    )"""

# Template para los sensores del agente
# Contiene las coordenadas (x,y) que el agente puede "ver" desde su posición actual
templateSensor = """(deftemplate Sensor
    (slot x (type INTEGER))
    (slot y (type INTEGER))
    )"""

# Template para las fronteras fuertes
# Contiene las coordenadas (x,y) de las casillas que el agente puede explorar
templateFronteraFuerte = """(deftemplate FronteraFuerte
    (slot x (type INTEGER))
    (slot y (type INTEGER))
    )"""

# Template para las fronteras débiles
# Contiene las coordenadas (x,y) de las casillas que el agente puede explorar
templateFronteraDebil = """(deftemplate FronteraDebil
    (slot x (type INTEGER))
    (slot y (type INTEGER))
    )"""

# Template para desactivar fronteras
# No contiene atributos, se usa como señal para desactivar fronteras
templateDesactivaFrontera = """(deftemplate DesactivaFrontera
    )"""

# Template para indicar que se ha alcanzado el objetivo
# No contiene atributos, se usa como señal de que el agente ha llegado a la meta
templateOBJETIVO = """(deftemplate OBJETIVOALCANZADO
    )"""

# Template para el camino recorrido
# Contiene el número de pasos dados por el agente
templateCamino =""" (deftemplate Camino
    (slot Pasos (type INTEGER))
)"""


# Construimos los templates en el entorno CLIPS
env.build(templateCasilla)
env.build(templateAgente)
env.build(templateSensor)
env.build(templateFronteraFuerte)
env.build(templateFronteraDebil)
env.build(templateDesactivaFrontera)
env.build(templateOBJETIVO)
env.build(templateCamino)

# Recuperamos los templates para usarlos en la carga de datos y reglas
templateCasilla = env.find_template('Casilla')
templateAgente = env.find_template('Agente')
templateSensor = env.find_template('Sensor')
templateFronteraFuerte = env.find_template('FronteraFuerte')
templateFronteraDebil = env.find_template('FronteraDebil')
templateKillFrontera = env.find_template('DesactivaFrontera')
templateOBJETIVO = env.find_template('OBJETIVOALCANZADO')

# Cargamos el laberinto desde un archivo CSV
df_laberinto = cargarCSV('laberinto1.csv', templateCasilla)

# Insertamos el agente en la posición inicial (3,3)
# Hay que automatirar esto a partir del CSV o de otro sitio aún
factStart_Agent = templateAgente.assert_fact(x=4, y=3, valor=0)

# Comprobación inicial
#print('Listado de facts:')
#for f in env.facts():
    #print(f)


# Definimos las reglas del sistema

# Regla para detectar si el agente ha alcanzado el objetivo
# Si el agente está en la misma posición que una casilla de tipo "G" (goal),
# se asienta un hecho OBJETIVOALCANZADO para indicar que se ha llegado a la meta
ruleObjetivo = """
(defrule RuleObjetivo
    (declare (salience 9999))
    ?c <- (Casilla (x ?x)(y ?y)(tipo "G"))
    (Agente (x ?x)(y ?y)(valor ?v))
    =>
    (assert (OBJETIVOALCANZADO ))
    
    (modify ?c (valor (+ ?v 1)))
)
"""
# Regla para activar los sensores del agente
# Si no se ha alcanzado el objetivo, se generan hechos Sensor para las
# posiciones adyacentes (arriba, abajo, izquierda, derecha) del agente
ruleActivaSensor = """
(defrule RuleActivaSensor
    (not (exists (OBJETIVOALCANZADO )))
    (Agente (x ?x) (y ?y))
    =>
    (assert (Sensor (x ?x ) (y (+ ?y 1)) ))
    (assert (Sensor (x ?x ) (y (- ?y 1)) ))
    (assert (Sensor (x (+ ?x 1)) (y ?y) ))
    (assert (Sensor (x (- ?x 1)) (y ?y) ))
)
"""
# Reglas para descartar sensores inválidos
# Si un sensor apunta a una posición fuera del laberinto, se descarta.
ruleDescartaSensorFuera = """
(defrule RuleDescartaSensorFuera
    (declare (salience 9000))
    ?s <-(Sensor (x ?x) (y ?y))
    (not (exists (Casilla (x ?x) (y ?y))))
    =>
    (retract ?s)
)
"""
# Si un sensor apunta a una pared (tipo "X"), se descarta.
ruleDescartaSensorPared = """
(defrule RuleDescartaSensorOcupado
    (declare (salience 9000))
    ?s <-(Sensor (x ?x) (y ?y))
    (Casilla (x ?x) (y ?y) (tipo "X"))
    =>
    (retract ?s)
)
"""
# Si un sensor apunta a una casilla ya explorada (tipo "E"), se descarta.
ruleDescartaSensorExplorado= """
(defrule RuleDescartaSensorExplorado
    (declare (salience 9000))
    ?s <-(Sensor (x ?x) (y ?y))
    (Casilla (x ?x) (y ?y) (tipo "E"))
    =>
    (retract ?s)
)
"""
# Si un sensor apunta a una casilla ya visitada por el agente (tipo "V"), se descarta.
# Esta regla tiene menor prioridad que la de frontera fuerte para permitir
# que se explore primero las casillas no visitadas.
ruleDescartaSensorVisitado = """
(defrule RuleDescartaSensorVisitado
    (declare (salience 8250))
    ?s <-(Sensor (x ?x) (y ?y))
    (Casilla (x ?x) (y ?y) (tipo "V"))
    =>
    (retract ?s)
)
"""
# Regla para activar fronteras fuertes
# Si un sensor apunta a una casilla no visitada (ni explorada ni pared),
# se asienta un hecho FronteraFuerte para esa posición
ruleActivarFronteraFuerte = """
(defrule RuleActivarFronteraFuerte
    (declare (salience 8000))
    ?s <-(Sensor (x ?x) (y ?y))
    ?c <-(Casilla (x ?x) (y ?y) (tipo ?t))
    =>
    (retract ?s)
    (assert (FronteraFuerte (x ?x) (y ?y) ))
)
"""
# Regla para activar fronteras débiles
# Si un sensor apunta a una casilla ya visitada (tipo "V") o sin visitar,
# se asienta un hecho FronteraDebil para esa posición
ruleActivarFronteraDebil = """
(defrule RuleActivarFronteraDebil
    (declare (salience 8500))
    ?s <-(Sensor (x ?x) (y ?y))
    ?c <-(Casilla (x ?x) (y ?y) (tipo ?t))
    =>
    (assert (FronteraDebil (x ?x) (y ?y) ))
)
"""

# Reglas para que el agente avance
# Si no hay sensores activos y hay una frontera fuerte,
# el agente avanza a esa posición, marcando la casilla actual como visitada.
ruleAvanzarBasico = """
(defrule RuleAvanzarBasico
    (declare (salience 1))
    (not (exists (Sensor )))
    ?f <-(FronteraFuerte (x ?x) (y ?y))
    ?c2 <-(Casilla (x ?x) (y ?y) (tipo ?t))
    
    ?a <-(Agente (x ?i) (y ?j) (valor ?va))
    ?c1 <-(Casilla (x ?i) (y ?j))
    =>
    (retract ?f)

    (modify ?c1 (tipo "V") (valor (+ ?va 1)))

    (retract ?a)
    (assert (Agente (x ?x) (y ?y) (valor (+ ?va 1))))

    (assert (DesactivaFrontera))
)
"""
# Si no hay sensores activos y no hay fronteras fuertes pero sí débiles,
# el agente avanza a esa posición, marcando la casilla actual como explorada.
ruleAvanzarBacktrack = """
(defrule RuleAvanzarBacktrack
    (not (exists (Sensor )))
    ?a <-(Agente (x ?i) (y ?j) (valor ?va))

    ?f <-(FronteraDebil (x ?x) (y ?y))
    ?c2 <-(Casilla (x ?x) (y ?y) (tipo ?t) (valor ?va ))

    ?c1 <-(Casilla (x ?i) (y ?j))
    =>
    (retract ?f)

    (modify ?c1 (tipo "E") (valor 0))

    (modify ?c2 (tipo "V"))

    (retract ?a)
    (assert (Agente (x ?x) (y ?y) (valor (- ?va 1))))

    (assert (DesactivaFrontera))
)
"""
# Regla para marcar la casilla del agente como "A" (agente)
# Si el agente está en una casilla que no es la meta (tipo distinto de "G"),
# se modifica el hecho Casilla correspondiente para marcar la presencia del agente
ruleAgente = """
(defrule ruleAgente
?Ag <- (Agente (x ?x) (y ?y))
?Ca <- (Casilla (x ?x) (y ?y) (tipo ?t))
(test(!= (str-compare ?t "G") 0))
=>
(modify ?Ca (tipo "A")))
"""
# Reglas para desactivar fronteras
# Si se ha asentado un hecho DesactivaFrontera y hay fronteras fuertes,
# se eliminan esas fronteras fuertes
ruleDesactivaFronteraFuerteStart = """
(defrule RuleDesactivaFronteraFuerteStart
    (declare (salience 90))
    (DesactivaFrontera)
    ?f <-(FronteraFuerte (x ?x) (y ?y))
    =>
    (retract ?f)
)
"""
# Si se ha asentado un hecho DesactivaFrontera y hay fronteras débiles,
# se eliminan esas fronteras débiles
ruleDesactivaFronteraDebilStart = """
(defrule RuleDesactivaFronteraDebilStart
    (declare (salience 80))
    (DesactivaFrontera)
    ?f <-(FronteraDebil (x ?x) (y ?y))
    =>
    (retract ?f)
)
"""
# Si se ha asentado un hecho DesactivaFrontera y no hay más fronteras,
# se elimina el hecho DesactivaFrontera para reiniciar el ciclo
ruleDesactivaFronteraStop = """
(defrule RuleDesactivaFronteraStop
    (declare (salience 90))
    ?front <-(DesactivaFrontera)
    (not (exists (FronteraDebil)))
    (not (exists (FronteraFuerte)))
    =>
    (retract ?front)
)
"""

# Construimos las reglas en el entorno CLIPS
env.build(ruleObjetivo)
env.build(ruleActivaSensor)
env.build(ruleDescartaSensorFuera)
env.build(ruleDescartaSensorPared)
env.build(ruleDescartaSensorExplorado)
env.build(ruleActivarFronteraFuerte)
env.build(ruleDescartaSensorVisitado)
env.build(ruleActivarFronteraDebil)
env.build(ruleAvanzarBasico)
env.build(ruleAvanzarBacktrack)
env.build(ruleAgente)
env.build(ruleDesactivaFronteraFuerteStart)
env.build(ruleDesactivaFronteraDebilStart)
env.build(ruleDesactivaFronteraStop)

# Imprimimos el estado inicial del laberinto
ImprimeLaberinto(env)

# Ejecutamos el entorno CLIPS hasta que se alcance el objetivo o no haya más movimientos posibles
env.run()

# Imprimimos el estado final del laberinto
print('----------------------------------')
ImprimeLaberinto(env)

for f in env.facts():
    print(f)
