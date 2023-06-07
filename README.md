# Boinc Home Assistant Control

:exclamation::exclamation::exclamation:
An improved home assistant control for boinc can now be found [here](https://github.com/SpuelMett/Boinc-Home-Assistant-Integration).
It works directly in home assistant and doesnt need any rest calls or endpoints anymore.
:exclamation::exclamation::exclamation:

This project lets you start and stop Boinc from home assistant. This can be used for example to run Boinc only on solar energy.

This project uses PyBoinc from Nielstron which can be found [here](https://github.com/nielstron/pyboinc/tree/dev/pyboinc).

Another similar project is https://github.com/tylercamp/boinc-client-control. It uses dotnet and also provides rest endpoints that can be used in Home assistant.

Does this project work?
At least for me :) If you have questions or need some help let me know.

Is it safe to use? 
I don't know! The web server should at least only run in your local network. 

# How it works
As mentioned this project uses the project PyBoinc to communicate with boinc. 
With Flask rest endpoint for start and stop are provided. 
In Home Assistant we can call these endpoints with simple http get requests.
Then these Requests can be used in Automations or scripts. 

### Soft stop
Furthermore, there is a soft_stop endpoint. 
This allows to wait for the next checkpoint before pausing a task.

Pausing of task after a soft stop is checked every minute through a separate script.
The Flask server communicates with this script with a simple pickle file.
(This solution is not great but at least it works)

You can specify the seconds after which a task will wait for the next checkpoint.
Example if this is set to 120 and a pause check is done:
```
A task that made a checkpoint 119 seconds ago will be paused immediately.
A task that made a checkpoint 121 seconds ago will not be paused.
```
Because the stop check is made every 60 seconds this value should be greater than 60


## Usage
In the following commands <BOINC_IP> needs to be replaced with the ip of you server/pc where boinc is running.
<BOINC_PASSWORD> needs to be replaced with the remote Password of your boinc client. I am not sure if this project will work without a password defined. But you should use one.

I intended this project to be used with docker. But with a bit tweaking it should also work without it.

### Method 1: Docker
```
git clone https://github.com/SpuelMett/Boinc-Home-Assistant-Control.git
cd Boinc-Home-Assistant-Control
git submodule update --init
docker build -t boinc_haas_control .
docker run -d --network host --name boinc_haas_control --env BOINC_IP=<RemoteIp> --env BOINC_PASSWORD=<YourBoincRemotePassword> --env BOINC_CHECKPOINTING=120 --restart unless-stopped boinc_haas_control
```

### Method 2: No docker
```
git clone https://github.com/SpuelMett/Boinc-Home-Assistant-Control.git
cd Boinc-Home-Assistant-Control
git submodule update --init
```
In the api.py and stop_checker.py you need to replace all occurrences of os.environ[''] with your values. 
Alternative the three environment values can be set on the machine. 

Now you need a python 3.8 environment. This can be done for example with conda. 

Next:
```
pip install --no-cache-dir -r requirements.txt
waitress-serve --host 0.0.0.0 api:app | python ./stop_checker.py
```

# Home Assistant integration

In the Home Assistant Configuration.yaml you need to specify the rest endpoints. 
Now you need the ip of the server/pc running this software.
```yaml
rest_command:
  boinc_start:
    url: "http://<IP_OF_FLASK_SERVER>:8080/start"
    method: get
  boinc_stop:
    url: "http://<IP_OF_FLASK_SERVER>:8080/stop"
    method: get
  boinc_soft_stop:
    url: "http://<IP_OF_FLASK_SERVER>:8080/soft_stop"
    method: get
```

Now you are ready to call the endpoint as a service for example in automations. 
Here is an example automation in the automations.yaml
```yaml
- id: '1683994894397'
  alias: Start Boinc
  description: ''
  trigger:
  - platform: numeric_state
    entity_id: sensor.energymetermqtt_sml_curr_w
    for:
      hours: 0
      minutes: 5
      seconds: 0
    below: -10
  condition: []
  action:
  - service: rest_command.boinc_start
    data: {}
  mode: single
```
