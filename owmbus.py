#!/usr/bin/env python3
import asyncio
import logging
import server_async

from os import getenv
import json
import requests

import time

from pymodbus.constants import Endian
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)

_logger = logging.getLogger(__name__)


async def updating_task(context):
    #   Update values in server.
    #
    #   It should be noted that getValues and setValues are not safe
    #   against concurrent use.
    base_url = "http://api.openweathermap.org/data/2.5/forecast?units=metric"
    appid=getenv("WEATHER_TOKEN")
    lat = getenv("LAT")
    lon = getenv("LON")
    
    Final_url = base_url + "&appid=" + appid + "&lat=" + lat + "&lon=" + lon
    
    fc_as_hex = 3
    slave_id = 0x00
    address = 0x00
        # update loop
    while True:
        now = time.time()
        values, dt = await read_data(Final_url, int(now))
        context[slave_id].setValues(fc_as_hex, address, values)
        txt = f"updating {len(values)!s} values"
        print(txt)
        _logger.debug(txt)
        if dt > now:
            wait = int((dt - now + 1))
        else:
            wait = 10
        await asyncio.sleep(wait)

async def read_data(Final_url, now):
    ms, ls = divmod(now, 1<<16)
    retval = [ms,ls]
    weather_data = requests.get(Final_url).json()
    list = weather_data.get('list')
    for item in list:
        dt = int(item.get('dt'))
        temp = int(100 * float(item.get('main').get('temp')))
        if (temp < 0):
            temp += 0x10000
        retval.append(int((dt-now)/60))
        retval.append(temp)
    return retval, int(list[0].get('dt'))
        


def setup_payload_server(cmdline=None):
    """Define payload for server and do setup."""

    block = ModbusSequentialDataBlock(1, [0] * 82)
    store = ModbusSlaveContext(hr=block, ir=block)
    context = ModbusServerContext(slaves=store, single=True)
    return server_async.setup_server(
        description="Run payload server.", cmdline=cmdline, context=context
    )

async def run_updating_server(args):
    """Start updating_task concurrently with the current task."""
    task = asyncio.create_task(updating_task(args.context))
    task.set_name("example updating task")
    await server_async.run_async_server(args)  # start the server
    task.cancel()


async def main(cmdline=None):
    """Combine setup and run."""
    run_args = setup_payload_server(cmdline=cmdline)
    await run_updating_server(run_args)

if __name__ == "__main__":
    asyncio.run(main(), debug=False)  # pragma: no cover
