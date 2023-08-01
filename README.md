# Rack Robotics Powercore EDM Power Supply Unit Firmware [23.07.14]

This repository contains the firmware for Rack Robotics's Powercore, an affordable, hackable transistor EDM power supply unit. It is released under the [Creative Commons CC-BY-SA 2.0 license.](https://creativecommons.org/licenses/by-sa/2.0/legalcode)

## Overview

Scope of Powercore EDM Power Supply Unit Firmware [23.07.14]:
1) Provide control over power MOSFET for high-voltage + high-current switching
2) Monitor thermister & power MOSFET temperature
3) Deactivate PSU in the event of overheating to prevent damage to unit

Electrical discharge machining (EDM) utilizes a thermoelectric process called 'spark erosion'. Sparks erosion removes material 
by vaporizing/boiling away metal using many very small electric sparks. Sparks happen very quickly, lasting only for a
fraction of a millisecond.

The Rack Robotics's Powercore V1 is a transistor-capacitor hybrid EDM power supply unit. The Powercore creates, maintains, and monitors electrical 
sparks in an EDM machine. It is designed to be affordable and hackable. The Powercore has several features to achive its purpose: 

    On-Board Raspberry Pi Pico  -   A drop-in Raspberry Pi Pico module is used as an on-board microcontroller, allowing for maximum flexibility. 
                                    Micropython come pre-flashed on-board. Do not attempt to program microcontroller while machining, or while 
                                    powered on.
    
    Transistor Control          -   A high-voltage & high-current power MOSFET (IRF135S203) controls when sparks can form. The MOSFET is
                                    primarily controlled via PWM. The logic of the high-voltage MOSFET is inverted. Meaning that when the 
                                    MOSFET pin state is low, current can pass. When the MOSFET pin state is high, current can not pass. 
                                    This is because of the low-voltage AOD508 MOSFET used to drive the high-voltage MOSFET.

    Adjustable Frequency        -   The minimum frequency between sparks is controlled digitally via PWM. Recommended operating frequency is 2 KHz.
                                    Higher frequencies can generate more waste heat than lower frequencies, potentially damaging the switching MOSFET.

    Adjustable Duty cycle       -   The maximum duration of sparks is controlled digitally via PWM.

    Current Monitoring          -   Current is monitored via an analog sensor (ACS712_x20A) within a range of +-20 amps. During capacitor dscharge, this maxes out 
                                    the current sensor, causing a peak that resembles a digital peak. 

    Thermal Monitoring          -   An onboard thermister monitors the temperature of the power resistor and MOSFET, helping to preventing overheating.

    Short Circuit Alert         -   (Work in Progress!) Digital feedback is provided during the event of a short by the "short alert" port (3.3 v normal, 0 v during short).

    Analog Feedback             -   Analog feedback from the ACS712x20A current sensor is provided by the "current" port (1.667 v - 0.333 v)
                                    This system adjusts the reported voltage with a sensitivity of ~0.0667 volts / amp. The baseline voltage 
                                    of the system is the voltage reported when no current is flowing through the system. The voltage is approximately 
                                    ~1.667 v volts. When current increases, the voltage reported will decrease at a rate of 
                                    ~0.667 volts per amp. A reading of 0.333 volts indicates >= 20 amps. During capacitor dscharge, this maxes out 
                                    the current sensor, causing a peak that resembles a digital peak.

## Installation

Clone the repository using the following command:

git clone https://github.com/rack-robotics/powercore-v1-firmware.git

## Setup

Before running the firmware, make sure that your Powercore EDM PSU is correctly installed and connected to your Raspberry Pi Pico. 

Please ensure that you do not attempt to program the microcontroller while machining or while the unit is powered on.

## Firmware Configuration

The firmware comes with a range of predefined settings, including temperature limits for different components, periods for capacitor charge and discharge, and the logic of the power MOSFET. These settings are located in the top portion of the main.py file and can be adjusted based on your needs.

## Usage
Ensure that micropython is already uploaded to the pico. Flash this firmware to the pico using the pico-go-w extension in VS Code.

## Contributing
We welcome contributions to this project. If you've found a bug or have a feature request, please open an issue. If you would like to improve the firmware, please fork the repository and create a pull request.

## License
This software is released by Rack Robotics, Inc. under the Creative Commons CC-BY-SA 2.0 license.
