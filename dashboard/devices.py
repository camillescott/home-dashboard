#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2021
# File   : devices.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 14.09.2021

import asyncio
import datetime
import enum
import logging

import kasa

from .database import add_realtime_power_entry, add_daily_power_entry
from .utils import once_per_second


class Devices:

    def __init__(self, discovered):
        self.devices = discovered

    async def update(self):
        for device in self.devices.values():
            await device.update()

    def summarize(self):
        return '\n'.join((
            f'{d.alias}: {d.device_type.name} @ {d.host} ({d.device_id})' \
            for did, d in self
        ))

    def __iter__(self):
        for did, device in self.devices.items():
            if device.children:
                for child in device.children:
                    yield child.device_id, child
            else:
                yield did, device

    def emeters(self):
        for did, device in self:
            if device.has_emeter:
                yield did, device

    def bulbs(self):
        for did, device in self:
            if device.is_bulb:
                yield did, device

    def plugs(self):
        for did, device in self:
            if device.is_plug:
                yield did, device


async def discover_devices():
    log = logging.getLogger()
    discovered = await kasa.Discover.discover()
    devices = Devices({d.device_id: d for d in discovered.values()})
    await devices.update()
    return devices


@once_per_second
async def realtime_energy_use_loop(devices, time=None):
    log = logging.getLogger()
    device_error = False
    for did, device in devices.emeters():
        try:
            emeter = await device.get_emeter_realtime()
        except kasa.exceptions.SmartDeviceException:
            log.warning(f'Error accessing device {device.alias}, skipping.')
            device_error = True
        else:
            read_time = datetime.datetime.now()
            log.info(f'{device.alias} (realtime): {emeter}')
            await add_realtime_power_entry(did, read_time, emeter)
    if device_error:
        log.info(f'Rediscovering devices...')
        devices = await discover_devices()


async def daily_energy_use_loop(devices):
    log = logging.getLogger()
    while True:
        for did, device in devices.items():
            emeter = await device.get_emeter_daily()
            read_time = datetime.datetime.now()
            log.info(f'{device.alias} (daily): {emeter}')
            await add_daily_power_entry(did, read_time, emeter)
        await asyncio.sleep(60 * 60)
