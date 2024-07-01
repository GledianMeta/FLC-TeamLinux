import libsumo
import threading
from consts import *


class Simulation:

    # Constructor
    def __init__(self):
        self.simulation_started = False
        self.kill_thread = False
        self.exec_semaphore = threading.Semaphore(
            1)  # This ensures that only one thread can acquire the semaphore at a time, preventing concurrent execution of simulation steps.

    # Configures and starts the simulation
    def configure(self, begin=0, end=None, step_duration=1, n_steps=-1, cfgpath=None):
        # Checks if the simulation is already running
        if self.is_busy() or self.is_started():
            return False
        self.n_steps = n_steps
        self.kill_thread = False
        cmd = ["sumo", "-c"]
        if cfgpath==None:
            cmd.append(CFG_PATH + SUMOCFG)
        else:
            cmd.append(cfgpath)
        if begin != 0:
            cmd.append("-b")
            cmd.append(f"{begin}")
        if end is not None:
            cmd.append("-e")
            cmd.append(f"{end}")
        if step_duration != 1:
            cmd.append("--step-length")
            cmd.append(f"{step_duration}")
        libsumo.start(cmd)
        self.simulation_started = True
        self.do_steps(n_steps)
        return True

    # Method which will be called to stop the simulation
    def stop_simulation(self):
        """
        Closes the libsumo simulation in both cases: when the simulations steps have been done and you  want to restart the simulation, or
        :return:
        """
        if not self.is_started():
            return False
        try:
            # if the simulation is running, acquire the second semaphore, so that the running sim's Thread will not read the wrong
            # "self.kill_thread" value and will wait to read a True value, so it will break and release also the first semaphore
            # TODO: is it better to avoid false read or allowing unwanted simulation Steps?
            if self.is_busy():
                self.kill_thread = True
            libsumo.close()
            self.simulation_started = False
            return True
        except:
            return False

    def do_steps(self, n_steps):  # is not a cumulative function, but a sequential one
        if self.is_busy() or not self.is_started():
            return False
        if n_steps == -1:
            threading.Thread(target=self.execute_all_steps).start()
        else:
            threading.Thread(target=self.execute_steps, args=(n_steps,)).start()
        return True

    def execute_steps(self, n_steps):
        try:
            if self.is_busy():
                return  # in case is_busy() check in do_steps() fails, re-check it in here and return.
            self.exec_semaphore.acquire()
            for step in range(n_steps):
                if not self.kill_thread:
                    libsumo.simulationStep()
                else:  # if kill_thread==True, kill the thread by breaking from the loop, and set the kill_thread back to False
                    self.kill_thread = False
                    break
        # This ensures that when all cars are done, or if something goes wrong, the track (semaphore) is free for someone else to use
        finally:
            self.exec_semaphore.release()
            # Ensure semaphore is released even if an exception occurs


    def execute_all_steps(self):
        if self.is_busy():
            return  # ideally this must never be called when is_busy()=True thanks to the check in do_steps()
        try:
            self.exec_semaphore.acquire()
            while libsumo.simulation.getMinExpectedNumber() > 0:  # libsumo.simulation.getMinExpectedNumber() returns the number of cars expected to be on the track.
                if not self.kill_thread:
                    libsumo.simulationStep()  # This function moves the simulation forward by one step, making the cars move.
                else:  # if kill_thread==True, kill the thread by breaking from the loop, and set the kill_thread back to False
                    self.kill_thread = False
                    break
        finally:
            self.exec_semaphore.release()

    def is_busy(self):
        return self.exec_semaphore._value == 0  # If Semaphore counts 0 indicates some computation is done
        # return threading.thread_count.....

    def is_started(self):
        return self.simulation_started
