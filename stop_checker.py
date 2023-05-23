import asyncio
import os
import pickle
from datetime import timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from libs.pyboinc.pyboinc import init_rpc_client
from libs.pyboinc.pyboinc.rpc_client import Mode

BOINC_IP = os.environ['BOINC_IP']
BOINC_PASSWORD = os.environ['BOINC_PASSWORD']
BOINC_CHECKPOINTING = int(os.environ["BOINC_CHECKPOINTING"])


async def check_to_stop(rpc_client):
    print("Checking if task should be stopped")

    # Read state from file
    should_stop = pickle.load(open("soft_stop_state.p", "rb"))

    if should_stop:
        one_task_running = False  # Default

        results = await rpc_client.get_results()
        for result in results:

            # check if the result is an active task
            if 'active_task' in result:
                active_task = result['active_task']
                checkpoint_cpu_time = active_task['checkpoint_cpu_time']
                current_cpu_time = active_task['current_cpu_time']
                project_url = result["project_url"]
                name = result["name"]

                # Check if last checkpoint was longer ago than the configured value
                if current_cpu_time - checkpoint_cpu_time < timedelta(seconds=BOINC_CHECKPOINTING):
                    # Suspend task
                    await rpc_client.suspend_result(project_url, name)
                    print("Suspending task:", name)
                else:
                    one_task_running = True

        # if all task are suspended set run mode to suspend
        if one_task_running is False:
            await rpc_client.set_run_mode(Mode.NEVER, 0)


async def connect():
    rpc_client = await init_rpc_client(BOINC_IP, BOINC_PASSWORD)
    await rpc_client.authorize()
    return rpc_client


if __name__ == '__main__':

    # connect to Boinc
    loop = asyncio.get_event_loop()
    rpc_client = loop.run_until_complete(connect())

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_to_stop, 'interval', args=[rpc_client], seconds=60)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
