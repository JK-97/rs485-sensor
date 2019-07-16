#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Basic run script"""
from usbutils.rs485driver import Rs485Driver

def main():
    Rs485Driver(serial_port='/dev/ttyUSB0').run()


if __name__ == "__main__":
    main()
