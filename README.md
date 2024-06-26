# FLC-TeamLinux
 Hello there, we are the FLC TeamLinux and here we present the first alpha proposal for the Application Programming Interfaces of our SUMO-Simulation containerization.
 
 Initialize the Simulation
 GET /init_simulation -> initialize the environment for the (single) simulation, recreating (and eventually overwriting) the sim.'s files folder (/simulation). So in creates the layout for the:
    simulation.edg.xml (a default test file)
    simulation.nod.xml (a default test file)
    simulation.net.xml (a default test file)
    simulation.rou.xml (a default test file)
    simulation.sumocfg (an xml-like file with inside of it the net-file, route-file and the time configuration).
 PUT /network (upload .net.xml)
 PUT /routes (overwrite existing .rou.xml file)
 PUT /charging_stations?reset (upload .xml file)
 POST /battery_options (will be updated in the .sumocfg file)
 POST /output_options (will be updated in the .sumocfg file)
 GET /create_config (check available files in the /simulation folder and generates the .sumocfg file)
 PS. if no output is explicitly indicated from the user, a list of predefined outputs will be considered in the configuration
 
 Start Simulation
 These APIs will start the simulation:
 
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
