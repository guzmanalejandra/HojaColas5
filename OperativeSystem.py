
import simpy
import random
import math


# Lucia Alejandra Guzman 20262
# Data
CapacidadRAM = 100
NumeroDeCPU = 2
random.seed(24)  # Seed
NumProcesos = 200  # Number of proccess
Interval = 1  # prcess creation interval
InstruccionesPorCiclo = 3  # How many insructions the CPU performs per unit of time
TiempoOperacionInOut = 5  # Time of operation I/O
TiemposDeProcesos = []  # list to store data


class SistemaOperativo:
    """Es el ambiente del sistema operativo, crea la RAM y los CPU"""

    def __init__(self, env):
        self.RAM = simpy.Container(env, init=CapacidadRAM, capacity=CapacidadRAM)
        self.CPU = simpy.Resource(env, capacity=NumeroDeCPU)


class Proceso:
    """La clase Proceso modela el funcionamiento de un proceso en la computadora"""

    def __init__(self, id, no, env, sistema_operativo):
        # Attributes
        self.id = id
        self.no = no
        self.instrucciones = random.randint(1, 10)
        self.memoriaRequerida = random.randint(1, 10)
        self.env = env
        self.terminated = False
        self.sistema_operativo = sistema_operativo
        self.createdTime = 0
        self.finishedTime = 0
        self.totalTime = 0
        self.proceso = env.process(self.procesar(env, sistema_operativo))

    # Methods
    def procesar(self, env, sistema_operativo):
        inicio = env.now
        self.createdTime = inicio
        print('%s: Creado en %d' % (self.id, inicio))  # The process is created at that moment 
        with sistema_operativo.RAM.get(self.memoriaRequerida) as getRam:  # Get RAM depending on the required
            yield getRam

            # Start Ram Usage
            print('%s: Obtiene RAM en %d (Estado: Wait)' % (self.id, env.now))
            siguiente = 0  # Variable to know what to do after "running"
            while not self.terminated:
                with sistema_operativo.CPU.request() as req:  # Request cpu until finished
                    print('%s: Espera al CPU en %d (Estado: Wait)' % (self.id, env.now))
                    yield req

                    # Inicio uso de CPU
                    print('%s: Obtiene CPU en %d (Estado: Running)' % (self.id, env.now))
                    for i in range(InstruccionesPorCiclo):  # Perform operations per cycle
                        if self.instrucciones > 0:
                            self.instrucciones -= 1  # If there are still instructions: operate
                            siguiente = random.randint(1, 2)  # To define your next step
                    yield env.timeout(1)  # It takes unit of time to perform instruction per cycle

                    # Start process I/O
                    if siguiente == 1:
                        print('%s: Espera operacion I/O en %d (Estado: I/O)' % (self.id, env.now))
                        yield env.timeout(TiempoOperacionInOut)

                    # Ends of RAM usage
                    if self.instrucciones == 0:
                        self.terminated = True  #If theres no mores instructions: end

            print('%s: Terminado en %d (Estado: Terminated)' % (self.id, env.now))
            sistema_operativo.RAM.put(self.memoriaRequerida)  # Release Ram
        fin = env.now
        self.finishedTime = fin  # Marcar fin
        self.totalTime = int(self.finishedTime - self.createdTime)  # Get computer time
        TiemposDeProcesos.insert(self.no, self.totalTime)


# Process generator
def proceso_generator(env, sistema_operativo):
    for i in range(NumProcesos):
        tiempo_creacion = random.expovariate(1.0/Interval)
        Proceso('Proceso %d' % i, i, env, sistema_operativo)
        yield env.timeout(tiempo_creacion)  # How long it will take for each one to appear


# Main
class Main:
    """Esta clase se encarga de crear los objetos para la simulacion"""
    def __init__(self):
        env = simpy.Environment()  #Create atmosphere
        sistema_operativo = SistemaOperativo(env)  # Create operating system
        env.process(proceso_generator(env, sistema_operativo))  # Create processes
        env.run()

        # Calculate time statistics
        def promedio(s): return sum(s) * 1.0 / len(s)

        tiempo_promedio_total = promedio(TiemposDeProcesos)  # Get average
        varianza_tiempo_total = map(lambda x: (x - tiempo_promedio_total) ** 2, TiemposDeProcesos)  # Get variance
        desvest_tiempo_total = math.sqrt(promedio(varianza_tiempo_total))  # Calculate Standard derivation

        print "El promedio de tiempo es de: ", tiempo_promedio_total, ", y su desviacion estandar es de: ", \
            desvest_tiempo_total


Main()  # run
