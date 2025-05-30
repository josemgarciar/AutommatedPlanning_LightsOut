from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner
from unified_planning.shortcuts import *
import copy

# Dimensiones del tablero
n, m = 5, 5

# s más similares a la solución de problema
s = 5

# Crear el problema
problem = Problem("light_out")

# Tipos
light = UserType("light")

# Crear objetos de posición
pos_i = {}  # filas
pos_j = {}  # columnas
for i in range(n):
    obj = problem.add_object(f"p{i}", light)
    pos_i[i] = obj
for j in range(m):
    obj = problem.add_object(f"q{j}", light)
    pos_j[j] = obj

# Fluente: si una celda (x, y) está encendida
state = Fluent("state", BoolType(), x=light, y=light)
problem.add_fluent(state)

# Inicialización: todas las luces encendidas
for i in range(n):
    for j in range(m):
        problem.set_initial_value(state(pos_i[i], pos_j[j]), True)

# Acción toggle(x, y): Pulsar el botón o la bombilla que se encuentra en la posición (x, y)
toggle = InstantaneousAction("toggle", x=light, y=light)
x = toggle.parameter("x")
y = toggle.parameter("y")

# Cambia el estado de la celda y sus adyacentes
deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
for i in range(n):
    for j in range(m):
        for dx, dy in deltas:
            ni, nj = i + dx, j + dy
            if 0 <= ni < n and 0 <= nj < m:
                toggle.add_effect(
                    state(pos_i[ni], pos_j[nj]),
                    Not(state(pos_i[ni], pos_j[nj])),
                    condition=And(Equals(x, pos_i[i]), Equals(y, pos_j[j]))
                )

problem.add_action(toggle)

# Objetivo: todas las luces apagadas
for i in range(n):
    for j in range(m):
        problem.add_goal(Not(state(pos_i[i], pos_j[j])))

# Dado un estado (matriz), retorna la matriz resultante de aplicar una acción sobre una luz, y los efectos sobre sus adyacentes.
def aplicar_accion(estado, i, j):
    nuevo_estado = copy.deepcopy(estado)
    for dx, dy in deltas:
        ni, nj = i + dx, j + dy
        if 0 <= ni < n and 0 <= nj < m:
            nuevo_estado[ni][nj] = not nuevo_estado[ni][nj]
    return nuevo_estado

def es_estado_objetivo(estado):
    return all(not estado[i][j] for i in range(n) for j in range(m))

def heuristica(estado):
    return sum(estado[i][j] for i in range(n) for j in range(m))

def busqueda_heuristica(estado_inicial, n_mejores=s, max_iter=1000):
    """
    1. Dado un estado se simulan todos los estados accesibles a través de este.
    2. Si alguno de los estados accesibles es el estado objetivo se termina y se devuelve la secuencia de acciones. En
    otro caso a cada estado accesible se le asigna como valor el número de celdas similares al estado objetivo.
    3. Se toman los n más similares y se sigue la búsqueda a partir de ellos, donde n es un número prefijado menor
    que la cantidad de acciones posibles
    """
    
    estados_actuales = [(estado_inicial, [])]
    visitados = set()
    
    for iteracion in range(max_iter):
        print(f"Iteración {iteracion+1}, explorando {len(estados_actuales)} estados")
        nuevos_estados = []
        
        for estado, acciones in estados_actuales:
            estado_tupla = tuple(tuple(fila) for fila in estado)
            if estado_tupla in visitados:
                continue
                
            visitados.add(estado_tupla)
    
            for i in range(n):
                for j in range(m):
                    nuevo_estado = aplicar_accion(estado, i, j)
                    nueva_secuencia = acciones + [(i, j)]
                    if es_estado_objetivo(nuevo_estado):
                        print(f"¡Solución encontrada en {len(nueva_secuencia)} pasos!")
                        return nueva_secuencia
                    
                    nuevos_estados.append((nuevo_estado, nueva_secuencia))
        
        if not nuevos_estados:
            print("No hay más estados para explorar")
            return None
            
        estados_valorados = [(estado, acciones, heuristica(estado)) 
                             for estado, acciones in nuevos_estados]
        estados_valorados.sort(key=lambda x: x[2])
        estados_actuales = [(estado, acciones) 
                            for estado, acciones, _ in estados_valorados[:n_mejores]]
        
        if estados_actuales:
            mejor_estado, _ = estados_actuales[0]
            luces_encendidas = sum(sum(fila) for fila in mejor_estado)
            print(f"  Mejor estado: {luces_encendidas} luces encendidas")
    
    return None

print("\nEjecutando algoritmo:\n")
estado_inicial = [[True for _ in range(m)] for _ in range(n)]
solucion = busqueda_heuristica(estado_inicial, n_mejores=s)

if solucion:
    print("\nPlan encontrado:")
    for idx, (i, j) in enumerate(solucion):
        print(f"{idx+1}. toggle({i},{j})")     
else:
    print("\nNo se pudo encontrar un plan.")

