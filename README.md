# Containerizing SUMO's simulation APIs
We are the FLC TeamLinux and here we present the final version of our APIs for SUMO-Simulation containerization. 
 
These APIs allow the user to interact with the SUMO simulation environment, by uploading configuration files, starting a simulation, and retrieving the output files.

In the context of the SUMO simulation, some default files are already present and can be overwritten by the user by means of the APIs, in order to customize the simulation environment. Those files are described in the GET /init_simulation. Otherwise, the user can upload it's own custom network, the routes, the charging stations, and set the battery and output options before starting the simulation.

A typical flow of the simulation would be:
1. initialize a new environment;
2. update your custom configuration files and battery and output options;
3. start simulation choosing between a direct execution straight from <i>begin</i> to <i>end</i>, or step by step (with a certain step size);
4. stop the simulation when you think you are done and check the results with the output.

The simulation can be started and stopped at any time, <b> but the output files can be retrieved only once it has beed stopped.</b>

## Dockerization and startup

In order to make them available anywhere with a really simple deployment procedure. the simulation tools have been encapsulated in a Docker container defined in the <a href="https://github.com/GledianMeta/FLC-TeamLinux/blob/main/Dockerfile">Dockerfile</a>. In this way, any user with a Docker engine running on it's computer will be able to reach and use these tools over it's local IP address, at port 8080.
Steps for configuration:
1. Clone this repository in your working directory ```git clone https://github.com/GledianMeta/FLC-TeamLinux```;
2. With a running docker engine, execute ```docker build -t <TAG_NAME_YOU_PREFER> .``` to build the container (it will take a while);
3. To start the container, use ```docker run -p 8080:8080 [-d/-it] <TAG_NAME_YOU_PREFER>``` (-it is for interactive output, while -d means "detach output from stdout").


## Configuration of the simulation

### GET /init_simulation
- initializes the environment for the simulation, overwriting the actual configuration files with the default ones which are:
  - sumo.net.xml
  - sumo.rou.xml
  - sumo.add.xml (additional, empty file for charging stations)
  - sumo.sumocfg (an xml-like file with inside of it the net-file, route-file and the time configuration).
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
- sets the output options in the simulation: by default, the following outputs are already inserted:
  - raw dump: info about vehicles positions;
  - emission output: info about electrical/fuel vehicles emissions; 
  - statistic output: general statistics of the simulation like the number of vehicles inserted/waiting, average speeds, traffic and public transport statistics;
  - charging station output: info about charging stations like power, efficiency, number of recharged vehicles and delivered energy.
- body: a JSON object with all the output parameters (and their value) that the user wants to set. Here is an example of the body:
    ```json
    {
        "battery_output": true,
        "collision_output": true,
    }
    ```
- returns:
    - 200 OK: if the output options are set successfully
    - 400 Bad Request: if the body empty, not a JSON object, the JSON object or the output parameters are not correct, or if the simulation has already been started (the user cannot set the output options during the started simulation) 


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
    - 500 Internal Server Error: if the simulation fails to start

### GET /next_step
- performs the next N steps of the simulation or all the remaining steps (if N=-1)
- query parameters:
    - n: the number of steps to compute
- returns:
    - 200 OK: if the next steps are computed successfully
    - 400 Bad Request: if the simulation has not been started or if there is an error in the execution of the next steps

### GET /status
- returns the actual status of the simulation, so if it has been started or not and if it is running or not
- returns:
    - 200 OK: a JSON object with the start status and the running status. Here is an example of the body:
    ```json
    {
        "started": true,
        "running": true
    }
    ```

### GET /stop_simulation
- stops the simulation run
- returns:
    - 200 OK: if the simulation is stopped successfully
    - 400 Bad Request: if the simulation has not been started yet

## Output Management

### GET /outputs
- returns the predefined outputs and the output requested by the user (using POST /output_options) at the end of the simulation
- returns:
    - 200 OK: if the outputs are returned successfully
    - 400 Bad Request: if the simulation has been started and not stopped yet
