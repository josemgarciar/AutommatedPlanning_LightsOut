from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner
from unified_planning.shortcuts import *

# Dimensiones del tablero
n, m = 5, 5

# Crear el problema
problem = Problem("lights_out")

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

# Fluent: si una celda (x, y) está encendida
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


# Resolver el problema
if __name__ == "__main__":
    with OneshotPlanner(name="enhsp") as planner:
        result = planner.solve(problem)
        if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
            print("Plan encontrado:")
            for action in result.plan.actions:
                print(action)
        else:
            print("No se pudo encontrar un plan.")
