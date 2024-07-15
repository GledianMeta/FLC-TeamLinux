# SUMO-Simulation APIs for Containerization
 Hello there, we are the FLC TeamLinux and here we present the final version of our APIs for SUMO-Simulation containerization. 
 
These APIs allow the user to interact with the SUMO simulation environment, by uploading configuration files, starting the simulation, and retrieving the output files.

In the context of the SUMO simulation, some default files are already present and can be overwritten by the user by means of the APIs, in order to customize the simulation environment.

The user can upload the network, the routes, the charging stations, and set the battery and output options.

The simulation can be started and stopped at any time, and the output files can be retrieved at the end of the simulation.


## Configuration of the simulation

### GET /init_simulation
- initializes the environment for the simulation, overwriting the simulation's files with the default ones which are:
  - simulation.edg.xml
  - simulation.nod.xml
  - simulation.net.xml
  - simulation.rou.xml
  - simulation.sumocfg (an xml-like file with inside of it the net-file, route-file and the time configuration).
- returns:
    - 200 OK: if the initialization is successful
    - 400 Bad Request: if a simulation has already been initialized
    - 500 Internal Server Error: if the initialization fails

### PUT /network
- uploads the network .net.xml file
- returns:
    - 200 OK: if the upload is successful
    - 400 Bad Request: if the file is not a .net.xml file, is too big, not present, doesn't match the XML schema of the SUMO network file or if the simulation has already been started (the user cannot upload the network during the started simulation)

### PUT /routes
- uploads the routes .rou.xml file
- returns:
    - 200 OK: if the upload is successful
    - 400 Bad Request: if the file is not a .rou.xml file, is too big, not present, doesn't match the XML schema of the SUMO route file or if the simulation has already been started (the user cannot upload the routes during the started simulation)

### PUT /charging_stations
- uploads the charging stations .xml file
- query parameters:
    - reset: if present, the charging stations will be reset before the upload and then the provided ones will be added
- returns:
    - 200 OK: if the upload is successful
    - 400 Bad Request: if the file is not a .xml file, is too big, not present, doesn't match the XML schema of the charging stations file or if the simulation has already been started (the user cannot upload the charging stations during the started simulation)

### POST /battery_options
- sets the battery options in the simulation
- body: a JSON object with all the battery parameters (and their value) that the user wants to set. Here is an example of the body:
    ```json
    {
        "battery_capacity": 5000,
        "battery_consumption": 0.1,
        "battery_efficiency": 0.9
    }
    ```
- returns:
    - 200 OK: if the battery options are set successfully
    - 400 Bad Request: if the body is not a JSON object, the JSON object or the battery parameters are not correct, or if the simulation has already been started (the user cannot set the battery options during the started simulation)

### POST /output_options
- sets the output options in the simulation
- body: a JSON object with all the output parameters (and their value) that the user wants to set. If no output is explicitly indicated from the user, a list of predefined outputs will be considered in the configuration. Here is an example of the body:
    ```json
    {
        "output_raw_dump": true,
        "output_emission": true,
        "output_statistics": true,
        "output_charging_station": true
    }
    ```
- returns:
    - 200 OK: if the output options are set successfully
    - 400 Bad Request: if the body is not a JSON object, the JSON object or the output parameters are not correct, or if the simulation has already been started (the user cannot set the output options during the started simulation) 


## Simulation Management

### GET /start_sim
- starts the simulation doing only the first N steps (if step_size=N), otherwise, computes 1 step (if step_size is not specified) or all the steps of the simulation (if step_size=-1)
- query parameters:
    - begin: the beginning of the simulation
    - end: the end of the simulation
    - time_step: the time step of the simulation
    - step_size: the number of steps to compute
- returns:
    - 200 OK: if the simulation is started successfully
    - 400 Bad Request: if the simulation has already been started or if the query parameters are not correct
 


GET /start_sim?begin=&end=&time_step=&step_size - start the simulation doing only the first step (if step_size=1), otherwise, computes N steps, with a value of -1 computes the simulation until the end of it (if end is specified)
 GET /next_step?n - do the n following steps of the sim.
 GET /status - returns the actual status of the simulation
 GET /stop_simulation - stops the simulation run (close)
 
 Output Management
 These APIs allow to return the output files from the Simulation, they can be requested anytime during the execution (ex. at time step=10)
 
 GET /outputs - returns a list of predifined outputs at the current step of the simulation. They include:
    raw dump, with info about vehicles positions;
    emission output, with info about electrical/fuel vehicles emissions;
    statistic output, with general statistics of the simulation like the number of vehicles inserted/waiting, average speeds, traffic and public transport statistics;
    charging station output, with info about charging stations like power, efficiency, number of recharged vehicles and delivered energy.
