#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2021
# File   : __main__.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 13.09.2021

import argparse

from .app import run_app


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--secret-key',
        default='pk7DuFlJzsquN-8PmEM_bg'
    )

    args = parser.parse_args()
    run_app(args)
