import libsumo
from consts import *
import threading


class Simulation:

    def __init__(self, begin, end, step_duration, n_steps):
        self.n_steps = n_steps
        self.semaphore = threading.Semaphore(1)  # Creiamo un semaforo con un contatore iniziale di 1
        libsumo.start(["sumo", "-c", "test_simulation.sumocfg", "-b", str(begin), "-e", str(end), "--step-length",
                       str(step_duration)])
        self.do_steps(n_steps)

    def simulation_step(self, n_steps):
        if self.is_busy():
            return
        self.n_steps = n_steps
        self.do_steps(n_steps)

    def stop_simulation(self):
        libsumo.close()

    def is_busy(self):
        return True if self.semaphore._value==0 else False

    def do_steps(self, n_steps):

        self.semaphore.acquire()  # Acquisisce il semaforo prima di eseguire i passi della simulazione

        if n_steps == -1:
            # execute all steps of the simulation
            return
        try:
            thread = threading.Thread(target=self.execute_steps, args=(self.n_steps,))
            thread.start()
        except RuntimeError:
            return

    def execute_steps(self, n_steps):
        for step in range(n_steps):
            libsumo.simulationStep()
        self.semaphore.release()  # Rilascia il semaforo dopo aver completato i passi
