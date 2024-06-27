import os
import subprocess
import randomTrips

SUMO_PATH = os.environ['SUMO_HOME']
#RANDOM_TRIPS_PATH = SUMO_PATH + "\\tools\\randomTrips.py"
RANDOM_TRIPS_PATH = r"C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"
# this method returns a CompletedProcess instance, whose returncode attribute is 0 if there is no error
# an alternative is to insert the attribute check=True; if an error occurs, an exception will be thrown (try-catch)
result = subprocess.run("netgenerate "
                        "--rand "
                        "--seed 43 "
                        "--output-file test_network.net.xml")
# if result.returncode =! 0 print("error")

# generate random trips, then convert them into routes
result = subprocess.run("python randomTrips.py " +
                        "--net-file test_network.net.xml "
                        "--route-file test_routes.rou.xml")

result = subprocess.run("sumo "
                        "--net-file test_network.net.xml "
                        "--route-files test_routes.rou.xml "
                        "--save-configuration test_simulation.sumocfg")