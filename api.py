import os
import pickle

from flask import Flask

from libs.pyboinc.pyboinc import init_rpc_client
from libs.pyboinc.pyboinc.rpc_client import Mode

BOINC_IP = os.environ['BOINC_IP']
BOINC_PASSWORD = os.environ['BOINC_PASSWORD']

app = Flask(__name__)


# Return a new client every time it is called
async def get_client():
    rpc_client = await init_rpc_client(BOINC_IP, BOINC_PASSWORD)
    await rpc_client.authorize()
    return rpc_client


async def resume_all_task(rpc_client):
    results = await rpc_client.get_results()
    for result in results:
        project_url = result["project_url"]
        name = result["name"]
        await rpc_client.resume_result(project_url, name)


@app.route("/start")
async def start():
    pickle.dump(False, open("soft_stop_state.p", "wb"))

    rpc_client = await get_client()
    await rpc_client.set_run_mode(Mode.AUTO, 0)
    await resume_all_task(rpc_client)
    return "Success"


@app.route("/stop")
async def stop():
    rpc_client = await get_client()
    await rpc_client.set_run_mode(Mode.NEVER, 0)
    return "Success"


@app.route("/soft_stop")
async def soft_stop():
    pickle.dump(True, open("soft_stop_state.p", "wb"))
    return "Success"


if __name__ == '__main__':
    app.run()
