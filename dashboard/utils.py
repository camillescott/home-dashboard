#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2021
# File   : utils.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 13.09.2021

import asyncio
import collections
import datetime
import functools


def is_iterable(obj):
    return (
        isinstance(obj, collections.Iterable)
        and not isinstance(obj, str)
    )


def once_per_second(func):
    async def wrapper(*args, **kwargs):
        while True:
            found = False
            while datetime.datetime.now().microsecond < 50000:
                if not found:
                    await func(*args, **kwargs)
                    found = True
                await asyncio.sleep(.01)
            await asyncio.sleep(.01)
    return wrapper


def once_per_minute(second=0):
    if not (0 <= second < 60):
        raise ValueError(f'`second` must be between 0 and 60 (got {second})')
    def deco(func):
        async def wrapper(*args, **kwargs):
            while True:
                found = False
                while datetime.datetime.now().second == second:
                    if not found:
                        await func(*args, **kwargs)
                        found = True
                    await asyncio.sleep(.1)
                await asyncio.sleep(.1)
        return wrapper
    return deco


def once_per_hour(minute=0):
    def deco(func):
        async def wrapper(*args, **kwargs):
            while True:
                found = False
                while datetime.datetime.now().minute == minute:
                    if not found:
                        await func(*args, **kwargs)
                        found = True
                    await asyncio.sleep(5)
                await asyncio.sleep(5)
        return wrapper
    return deco


def once_per_day(hour=0):
    def deco(func):
        async def wrapper(*args, **kwargs):
            while True:
                found = False
                
                while datetime.datetime.now().hour == hour:
                    if not found:
                        await func(*args, **kwargs)
                        found = True
                    await asyncio.sleep(60)
                await asyncio.sleep(60)
        return wrapper
    return deco
