# Rack Robotics Powercore EDM Power Supply Unit Firmware [23.07.14]

This repository contains the firmware for Rack Robotics's Powercore, an affordable, hackable transistor EDM power supply unit. It is released under the [Creative Commons CC-BY-SA 2.0 license.](https://creativecommons.org/licenses/by-sa/2.0/legalcode)

## Overview

The Powercore creates, maintains, and monitors electrical sparks in an Electrical Discharge Machining (EDM) machine by using a process called 'spark erosion'. It consists of several important features including control over a high-voltage power MOSFET, thermal and current monitoring, and adjustable frequency and duty cycle. The Powercore uses a Raspberry Pi Pico for its on-board microcontroller, which comes pre-flashed with Micropython.

## Installation

Clone the repository using the following command:

git clone https://github.com/rack-robotics/powercore-firmware.git

## Setup

Before running the firmware, make sure that your Powercore EDM PSU is correctly installed and connected to your Raspberry Pi Pico. 

Please ensure that you do not attempt to program the microcontroller while machining or while the unit is powered on.

## Firmware Configuration

The firmware comes with a range of predefined settings, including temperature limits for different components, periods for capacitor charge and discharge, and the logic of the power MOSFET. These settings are located in the top portion of the main.py file and can be adjusted based on your needs.

Usage
Ensure that micropython is already uploaded to the pico. Flash this firmware to the pico using the pico-go-w extension in VS Code.

Contributing
We welcome contributions to this project. If you've found a bug or have a feature request, please open an issue. If you would like to improve the firmware, please fork the repository and create a pull request.

License
This software is released by Rack Robotics, Inc. under the Creative Commons CC-BY-SA 2.0 license.
