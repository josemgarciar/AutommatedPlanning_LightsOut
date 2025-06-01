from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
import copy

# Parámetros
n, m = 5, 5
s = 5  
deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

class LightsOut:
    def __init__(self, n, m, beam_width):
        self.n, self.m, self.s = n, m, beam_width

    def crear_estado_inicial(self):
        return [[True for _ in range(self.m)] for _ in range(self.n)]

    def aplicar_toggle(self, estado, i, j):
        nuevo = copy.deepcopy(estado)
        for dx, dy in deltas:
            ni, nj = i + dx, j + dy
            if 0 <= ni < self.n and 0 <= nj < self.m:
                nuevo[ni][nj] = not nuevo[ni][nj]
        return nuevo

    def luces_encendidas(self, estado):
        return sum(cell for fila in estado for cell in fila)

    def crear_problema(self, estado):
        prob = Problem("lights_out")
        cell = UserType("cell")
        X = [prob.add_object(f"x{i}", cell) for i in range(self.n)]
        Y = [prob.add_object(f"y{j}", cell) for j in range(self.m)]

        state = Fluent("on", BoolType(), x=cell, y=cell)
        prob.add_fluent(state)

        for i in range(self.n):
            for j in range(self.m):
                prob.set_initial_value(state(X[i], Y[j]), estado[i][j])

        toggle = InstantaneousAction("toggle", x=cell, y=cell)
        x = toggle.parameter("x")
        y = toggle.parameter("y")

        for i in range(self.n):
            for j in range(self.m):
                for dx, dy in deltas:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < self.n and 0 <= nj < self.m:
                        toggle.add_effect(
                            state(X[ni], Y[nj]),
                            Not(state(X[ni], Y[nj])),
                            condition=And(Equals(x, X[i]), Equals(y, Y[j]))
                        )

        prob.add_action(toggle)

        for i in range(self.n):
            for j in range(self.m):
                prob.add_goal(Not(state(X[i], Y[j])))

        return prob

    def buscar_con_anchura_poda(self, estado_inicial=None, max_iter=30):
        if estado_inicial is None:
            estado_inicial = self.crear_estado_inicial()

        frontera = [(estado_inicial, [])]
        visitados = set()

        for _ in range(max_iter):
            nuevos = []
            for estado, acciones in frontera:
                estado_hash = tuple(tuple(fila) for fila in estado)
                if estado_hash in visitados:
                    continue
                visitados.add(estado_hash)

                problema = self.crear_problema(estado)
                with OneshotPlanner(name="enhsp") as planner:
                    result = planner.solve(problema)
                    if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                        plan_acciones = []
                        for a in result.plan.actions:
                            i = int(str(a.actual_parameters[0]).replace("x", ""))
                            j = int(str(a.actual_parameters[1]).replace("y", ""))
                            plan_acciones.append((i, j))
                        return acciones + plan_acciones

                # Expandir vecinos
                for i in range(self.n):
                    for j in range(self.m):
                        nuevo = self.aplicar_toggle(estado, i, j)
                        nuevos.append((nuevo, acciones + [(i, j)]))

            # Poda
            nuevos.sort(key=lambda x: -self.luces_encendidas(x[0]))
            frontera = nuevos[:self.s]

        return None

if __name__ == "__main__":
    solver = LightsOut(n, m, beam_width=s)
    plan = solver.buscar_con_anchura_poda()

    if plan:
        print("\n¡Plan encontrado!")
        for idx, (i, j) in enumerate(plan):
            print(f"{idx+1}. toggle({i},{j})")
    else:
        print("No se encontró solución.")

