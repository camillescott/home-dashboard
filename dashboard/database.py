#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2021
# File   : database.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 13.09.2021

import enum
import functools
import importlib
import inspect
import logging
import types

from quart import current_app
from bson.objectid import ObjectId

from .utils import is_iterable, once_per_hour


class Tables(enum.Enum):
    DEVICES = 'devices'
    REALTIME = 'realtime'
    DAILY = 'daily'
    ARCHIVE = 'archive'


def use_mongo(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log = logging.getLogger() 
        db = kwargs.get('db', current_app.mongo.db)
        func_instance = func(db, *args, **kwargs)

        if isinstance(func_instance, types.AsyncGeneratorType):
            async def inner():
                async for result in func_instance:
                    yield result
        else:
            async def inner():
                return await func_instance
        return inner()

    return wrapper


@use_mongo
async def update_devices(db, update_time, devices):
    table = db[Tables.DEVICES.value]

    for did, device in devices:
        data = {'alias': device.alias,
                'host': device.host,
                'device_id': device.device_id,
                'device_type': device.device_type.name,
                'location': device.location,
                'model': device.model,
                'class': str(type(device)),
                'last_updated': update_time}

        await table.replace_one({'device_id': device.device_id},
                                data,
                                upsert = True)


@use_mongo
async def query_device(db, device_id, as_device = False):
    table = db[Tables.DEVICES.value]
    query = {'device_id': device_id}
    device_data = table.find_one(query)

    if as_device:
        module_name, _, klass_name = device_data['class'].rpartition('.')
        klass = getattr(importlib.import_module(module_name), klass_name)
        device = klass(data['host'])
        await device.update()
        return device, device_data
    else:
        return device_data


@use_mongo
async def add_realtime_power_entry(db, device_id, read_time, data):
    table = db[Tables.REALTIME.value]
    data = dict(device_id=device_id, read_time=read_time, **data)

    result = await table.insert_one(data)

    return result


@use_mongo
async def add_daily_power_entry(db, device_id, read_time, data):
    table = db[Tables.REALTIME.value]
    data = dict(device_id=device_id, read_time=read_time, **data)

    result = await table.insert_one(data)

    return result


@once_per_hour
@use_mongo
async def smooth_and_archive_buffer(db):
    now = datetime.datetime.now()
    hour = datetime.timedelta(hours=1)
    table = db[Tables.ARCHIVE.value]


