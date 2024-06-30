import libsumo
import threading
from consts import *

class Simulation:

    # Constructor
    def __init__(self):
        self.semaphore = threading.Semaphore(
            1)  # Semaphore Initialized with a count of 1 => This ensures that only one thread can acquire the semaphore at a time, preventing concurrent execution of simulation steps.

    def configure(self, begin, end, step_duration, n_steps):
        self.n_steps = n_steps
        libsumo.start(
            ["sumo", "-c", CFG_PATH + SUMOCFG, "-b", str(begin), "-e", str(end), "--step-length", str(step_duration)])
        self.do_steps(n_steps)
        self.kill_thread=False

    # Method which will be called to stop the simualtion
    def stop_simulation(self):
        try:
            if self.semaphore.value==1:
                libsumo.close()
                self.kill_thread=True
        except:
            return False
        return True


    def is_busy(self):
        return self.semaphore.value == 0  # If Semaphore counts 0 indicates busy


    def do_steps(self, n_steps):
        if self.is_busy():
            return
        try:
            if n_steps == -1:
                threading.Thread(target=self.execute_all_steps).start()
            else:
                threading.Thread(target=self.execute_steps, args=(n_steps,)).start()
        except RuntimeError:
            self.semaphore.release()  # Release the semaphore if thread creation fails


    def execute_steps(self, n_steps):
        self.semaphore.acquire()
        try:
            for step in range(n_steps):
                if not self.kill_thread:
                    libsumo.simulationStep()
                else:
                    break
        # This ensures that when all cars are done, or if something goes wrong, the track (semaphore) is free for someone else to use
        finally:
            self.semaphore.release()
            self.kill_thread=False # Ensure semaphore is released even if an exception occurs

    def execute_all_steps(self):
        self.semaphore.acquire()
        try:
            while libsumo.simulation.getMinExpectedNumber() > 0 and not self.kill_thread:  # libsumo.simulation.getMinExpectedNumber() returns the number of cars expected to be on the track.
                libsumo.simulationStep()                        # This function moves the simulation forward by one step, making the cars move.
        finally:
            self.semaphore.release()
            self.kill_thread=False
            # Ensure semaphore is released even if an exception occurs
