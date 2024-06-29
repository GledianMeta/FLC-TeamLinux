import libsumo
from consts import *
import threading


class Simulation:

    def __init__(self, begin, end, step_duration, n_steps):
        self.busy = False
        self.n_steps = n_steps
        self.semaphore = threading.Semaphore(1)  # Creiamo un semaforo con un contatore iniziale di 1
        libsumo.start(["sumo", "-c", f".{CFG_PATH + SUMOCFG}", "-b", begin, "-e", end, "--step-length", step_duration])
        self.doSteps(n_steps)

    def simulation_step(self, n_steps):
        self.n_steps = n_steps
        self.doSteps(n_steps)

    def isBusy(self):
        return self.busy

    def doSteps(self, n_steps):
        if n_steps == -1:
            return
        self.semaphore.acquire()  # Acquisisce il semaforo prima di eseguire i passi della simulazione
        try:
            for step in range(n_steps):
                libsumo.simulationStep()
        finally:
            self.semaphore.release()  # Rilascia il semaforo dopo aver completato i passi
