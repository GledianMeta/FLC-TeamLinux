import libsumo
import threading
from consts import *

class Simulation:

    # Constructor
    def __init__(self, begin, end, step_duration, n_steps):
        self.n_steps = n_steps
        self.semaphore = threading.Semaphore(1)  # Semaphore Initialized with a count of 1 => This ensures that only one thread can acquire the semaphore at a time, preventing concurrent execution of simulation steps.
        libsumo.start(["sumo", "-c", CFG_PATH + SUMOCFG, "-b", str(begin), "-e", str(end), "--step-length", str(step_duration)])
        self.do_steps(n_steps)




    # Method which will be called to stop the simualtion
    def stop_simulation(self):
        libsumo.close()
        return "Simulation stopped"


    def is_busy(self):
        return self.semaphore.value == 0  # If Semaphore counts 0 indicates busy


    def do_steps(self, n_steps):
        if self.is_busy():
            return
        #otherwise
        self.semaphore.acquire()  # Acquire the semaphore before starting the steps
        try:
            if n_steps == -1:
                threading.Thread(target=self.execute_all_steps).start()
            else:
                threading.Thread(target=self.execute_steps, args=(n_steps,)).start()
        except RuntimeError:
            self.semaphore.release()  # Release the semaphore if thread creation fails



    def simulation_step(self, n_steps):
        if self.is_busy():
            return "Simulation is busy"
        self.n_steps = n_steps
        self.do_steps(n_steps)
        return "Simulation step executed"


    def execute_steps(self, n_steps):
        try:
            for step in range(n_steps):
                libsumo.simulationStep()
        # This ensures that when all cars are done, or if something goes wrong, the track (semaphore) is free for someone else to use
        finally:
            self.semaphore.release()  # Ensure semaphore is released even if an exception occurs


    def execute_all_steps(self):
        try:
            while libsumo.simulation.getMinExpectedNumber() > 0:  # libsumo.simulation.getMinExpectedNumber() returns the number of cars expected to be on the track.
                libsumo.simulationStep()                        # This function moves the simulation forward by one step, making the cars move.
        finally:                                             # finally guarantees the release of the semaphore.
            self.semaphore.release()                       # Ensure semaphore is released even if an exception occurs
