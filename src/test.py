from main import LightsOutDomain, create_instance
import os
import sys

# Creamos un patrón inicial específico como en la imagen
# El patrón muestra un plus (+) con luces encendidas


# Crear una instancia 3x3 con el patrón específico
print("Creando instancia 3x3 con patrón específico...")
create_instance(n=5, m=5)

# Ejecutar pyperplan con esa instancia
print("Ejecutando pyperplan con la instancia 3x3...")
comando = "pyperplan -H hmax -s astar domain_lightsout_5x5.pddl problem_lightsout_5x5.pddl"
exit_code = os.system(comando)

if exit_code != 0:
    print("\nError ejecutando pyperplan con la instancia 3x3.")
    sys.exit(1)
else:
    print("\nÉxito con la instancia 3x3.")
