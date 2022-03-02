#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2021
# File   : app.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 25.08.2021

import asyncio
import datetime
import logging
import os
from signal import SIGINT, SIGTERM
import textwrap
import yaml

from quart import Quart, redirect, url_for, render_template, g, flash, current_app
from quart_motor import Motor
from rich.logging import RichHandler

from .database import update_devices
from .devices import (discover_devices,
                      realtime_energy_use_loop,
                      daily_energy_use_loop)


def build_app(args):

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)10s '\
               '[%(filename)s:%(lineno)s - %(funcName)20s()] %(message)s',
        datefmt="[%x %X]",
        handlers=[RichHandler()]
    )
    logger = logging.getLogger()
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    app = Quart(__name__)
    app.secret_key = args.secret_key
    app.config["MONGO_URI"] = "mongodb://localhost:27017/dashboardDB"

    mongo = Motor(app, tz_aware=True)
    app.mongo = mongo

    @app.before_serving
    async def startup():
        loop = asyncio.get_event_loop()
        
        app.devices = await discover_devices()
        await update_devices(datetime.datetime.now(), app.devices)
        logger.info(f'Discovered devices:\n{textwrap.indent(app.devices.summarize(), "    * ")}')
        realtime_task = loop.create_task(realtime_energy_use_loop(app.devices))
        #daily_task = loop.create_task(daily_energy_use_loop(plugs))

    return app


def run_app(args):

    app = build_app(args)
    app.run('0.0.0.0', 7171, use_reloader=True, debug=True)
