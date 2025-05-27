from py2pddl import Domain, create_type
from py2pddl import predicate, action
from py2pddl import goal, init

class LightsOutDomain(Domain):
    Object = create_type("Object")
    Light = create_type("Light", Object)

    @predicate(Light)
    def lightOn(self, l):
        """Representa que la luz l está encendida"""

    @predicate(Light)
    def lightOff(self, l):
        """Representa que la luz l está apagada"""
        
    @predicate(Light, Light)
    def adjacent(self, l1, l2):
        """Indica que la luz l1 es adyacente a la luz l2"""

    @action(Light)
    def pushLight(self, l):
        """
        Acción de pulsar una luz, lo que cambia su estado:
        - Si está encendida, se apaga
        - Si está apagada, se enciende
        """
        # La acción puede aplicarse independientemente del estado inicial
        precond = []
        # Efectos condicionales no son soportados directamente en PDDL básico,
        # así que necesitamos acciones separadas
        effect = []
        return precond, effect

    @action(Light)
    def pushLightOn(self, l):
        """Pulsar una luz que está encendida para apagarla"""
        precond = [self.lightOn(l)]
        effect = [~self.lightOn(l), self.lightOff(l)]
        return precond, effect

    @action(Light)
    def pushLightOff(self, l):
        """Pulsar una luz que está apagada para encenderla"""
        precond = [self.lightOff(l)]
        effect = [~self.lightOff(l), self.lightOn(l)]
        return precond, effect

    @action(Light, Light)
    def toggleAdjacent(self, l, a):
        """
        Cuando se pulsa l, cambia el estado de sus luces adyacentes a
        Esta acción debe ser aplicada junto con pushLightOn o pushLightOff
        """
        precond = [self.adjacent(l, a)]
        # Los efectos dependen del estado actual de la luz adyacente,
        # así que necesitamos más acciones específicas
        effect = []
        return precond, effect

    @action(Light, Light)
    def toggleAdjacentOn(self, l, a):
        """Cambia una luz adyacente encendida a apagada cuando se pulsa l"""
        precond = [self.adjacent(l, a), self.lightOn(a)]
        effect = [~self.lightOn(a), self.lightOff(a)]
        return precond, effect

    @action(Light, Light)
    def toggleAdjacentOff(self, l, a):
        """Cambia una luz adyacente apagada a encendida cuando se pulsa l"""
        precond = [self.adjacent(l, a), self.lightOff(a)]
        effect = [~self.lightOff(a), self.lightOn(a)]
        return precond, effect


def create_instance(n, m, initial_lights_on=None):
    """
    Crea una instancia del problema LightsOut con una matriz de n x m
    
    Args:
        n (int): Número de filas
        m (int): Número de columnas
        initial_lights_on (list): Lista de coordenadas (i,j) de luces que están encendidas inicialmente.
                                 Si es None, todas las luces están encendidas inicialmente.
    
    Returns:
        LightsOutProblem: Instancia del problema creada
    """
    if n <= 0 or m <= 0:
        raise ValueError("Las dimensiones del tablero deben ser mayores que 0")
    
    if initial_lights_on is None:
        # Por defecto, todas las luces están encendidas
        initial_lights_on = [(i, j) for i in range(n) for j in range(m)]
    
    class LightsOutProblem(LightsOutDomain):
        
        def __init__(self):
            super().__init__()

            # Lista para guardar los nombres de las luces
            lights = []
            for i in range(n):
                for j in range(m):
                    lights.append(f"light-{i}-{j}")

            print(f"Creando {len(lights)} luces...")
            
            # Crear objetos Light
            self.lights = LightsOutDomain.Light.create_objs(lights)

        @init
        def init(self):
            initial_state = []
            
            for i in range(n):
                for j in range(m):
                    light_name = f"light-{i}-{j}"
                    
                    # Determinar si la luz está encendida o apagada inicialmente
                    if (i, j) in initial_lights_on:
                        initial_state.append(self.lightOn(self.lights[light_name]))
                    else:
                        initial_state.append(self.lightOff(self.lights[light_name]))
                    
                    # Establecer relaciones de adyacencia (arriba, abajo, izquierda, derecha)
                    if i > 0: 
                        initial_state.append(self.adjacent(
                            self.lights[light_name], 
                            self.lights[f"light-{i-1}-{j}"]
                        ))
                    if i < n-1:  
                        initial_state.append(self.adjacent(
                            self.lights[light_name], 
                            self.lights[f"light-{i+1}-{j}"]
                        ))
                    if j > 0:  
                        initial_state.append(self.adjacent(
                            self.lights[light_name], 
                            self.lights[f"light-{i}-{j-1}"]
                        ))
                    if j < m-1:  
                        initial_state.append(self.adjacent(
                            self.lights[light_name], 
                            self.lights[f"light-{i}-{j+1}"]
                        ))
            
            return initial_state
        
        @goal
        def goal(self):
            # El objetivo es tener todas las luces apagadas
            goal_state = []
            
            for i in range(n):
                for j in range(m):
                    light_name = f"light-{i}-{j}"
                    goal_state.append(self.lightOff(self.lights[light_name]))
            
            return goal_state

    problem = LightsOutProblem()
    problem.generate_domain_pddl(filename=f"domain_lightsout_{n}x{m}")
    problem.generate_problem_pddl(filename=f"problem_lightsout_{n}x{m}")
    
    return problem

