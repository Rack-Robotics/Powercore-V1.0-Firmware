# Rack Robotics, Inc. 
# Rackrobo.io
# Powercore EDM Power Supply Unit Firmware [23.07.14]

"""
“This software is released by Rack Robotics, inc. under the [Creative Commons CC-BY-SA 2.0 license.] (https://creativecommons.org/licenses/by-sa/2.0/legalcode "Creative Commons Legal Code")
"""

"""
Scope of Powercore EDM Power Supply Unit Firmware [23.07.14]:
1) Provide control over power MOSFET for high-voltage + high-current switching
2) Monitor thermister & power MOSFET temperature
3) Deactivate PSU in the event of overheating to prevent damage to unit
"""

"""
    Electrical discharge machining (EDM) utilizes a thermoelectric process called 'spark erosion'. Sparks erosion removes material 
    by vaporizing/boiling away metal using many very small electric sparks. Sparks happen very quickly, lasting only for a
    fraction of a millisecond.

    The Rack Robotics's Powercore is a transistor EDM power supply unit. The Powercore creates, maintains, and monitors electrical 
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
"""

# Imported Modules 
# ----------------
from machine import Pin , ADC, PWM
import math
from utime import sleep

"""
The minimum period of the EDM system is the sum of the periods. The maximum frequency of the EDM system is the inverse of the minimum period.
"""

# Target period that capacitor energy is dumped, and a spark forms (microseconds)
electrical_discharge_spark_period = 40      # microseconds

# Target period that capacitors are charged up, and the dielectric fluid recovers (microseconds)
electrical_discharge_recovery_period = 400     # microseconds

# Tell system to invert logic for the power MOSFET. Setting the asigned GPIO pin high will set the MOSFET gate low, and vise versa
invert_MOSFET_logic = True

"""
The Powercore V1 EDM power supply contains a power resistor. The temperature of the power resistor can be monitored as an added safety feature. In the event 
that power resistor temperature rises to unsafe levels, then action can be taken by the microcontroller. If the temperature is extremely low, this indicates 
an electrical failure, such as the thermister not being connected securely. The same is done for the power MOSFET. 
"""

# Maximum allowable temperature of power resistor board)
maximum_allowable_temperature_of_power_resistor = 368.15 # Kelvin

# Minimum allowable temperature of power resistor board
minimum_allowable_temperature_of_power_resistor = 273.15 # Kelvin

# Maximum allowable temperature of power resistor board
maximum_allowable_temperature_of_power_MOSFET = 353.2 # Kelvin

# Minimum allowable temperature of power resistor board
minimum_allowable_temperature_of_power_MOSFET = 273.15 # Kelvin

"""
A thermister is a variable resistor. Microcontrollers can not read resistance, only voltages, with an analog to voltage converter. This is done with a voltage 
divider, containing the thermister and a 10K pullup resistor. Converting the observed voltage to a temperature requires a beta coefficient, a specification for thermisters.
"""

# The beta coefficient of the NTC 3950 thermister, which is a specification of the thermister used to calculate temperature
NTC_3950_thermister_beta_coefficient = 3950

# Nominal resistance of the NTC 3950 thermister
NTC_3950_thermister_normal_resistance = 100000 # ohms

# The pullup resistor for the thermisters on the Powercore motherboard
thermister_pullup_resistor_value = 10000 # ohms

# The default value of temperature. This is made default negative as a safety feature
temperature = -100 # Kelvin

# Periodic checks are conducted using the 'time' module, which requires a variable which is continuously updated
last_check_time_for_thermal_runaway_protection_check_one = 0
last_check_time_for_thermal_runaway_protection_check_two = 0

# Set up the output pin for initiating spark. This MOSFET is situated between the cathode electrode and ground. 
# Current may only flow through the electrodes when this MOSFET pin is high. 
high_voltage_MOSFET_pin = Pin(17, Pin.OUT)

# Set up the analog input pin for the current sensor
ACS712_analog_current_sensor = ADC(Pin(26))

# Two JST connects, or pads for JST connectors, are present on the motherboard. Thermisters can be plugged into 
# these connectors to monitor the temperature of critical components. A 10K resistor pulls these pins up to 3.3 volts.
thermister_1_analog_input = ADC(Pin(27))
thermister_2_analog_input = ADC(Pin(28))

# This MOSFET is used to control the state of the short alert pin. When this pin is low, the short alert pin is pulled high. 
# When this pin is high, the short alert pin is pulled low. 
short_alert_MOSFET_pin = Pin(20, Pin.OUT)

# Three LEDs are present on the motherboard PCB. These are driven by three pins
spark_status_LED = Pin(16, Pin.OUT)
high_voltage_MOSFET_status_LED = Pin(18, Pin.OUT)
short_alert_LED = Pin(19, Pin.OUT)
user_LED = Pin(25, Pin.OUT) # Comes placed on the pico module from factory

# Function Definition
# -------------------

def set_default_pin_states(): 
    """
    Function to set the default/safe state of GPIO pins for initialization of Powercore EDM power supply
    """
    
    # Logic for the high voltage MOSFET is inverted. Switching this GPIO pin on turns the high-voltage MOSFET off
    if invert_MOSFET_logic == True: 
        high_voltage_MOSFET_pin.on()
    if invert_MOSFET_logic == False: 
        high_voltage_MOSFET_pin.off()
    
    # GPIO pins to turn on
    user_LED.on()

    # GPIO pins to turn off
    spark_status_LED.off()
    high_voltage_MOSFET_status_LED.off()
    short_alert_LED.off()
    short_alert_MOSFET_pin.off()

def get_temperature(thermister_pin, number_of_samples, pullup_resistor_value, normal_thermister_resistance, beta_coefficient):
    """
    Function to get the temperature from a thermister. This function assumes that the thermister is part of a voltage
    divider with a pullup resistor.
    :param thermister_pin: Analog pin to which thermister is connected
    :param number_of_samples: Numbers of samples taken during averaging operation
    :param pullup_resistor_value: Value of pullup resistor in thermister voltage divider circuit (ohms)
    :param normal_thermister_resistance: Normal value of the thermister (ohms)
    :param beta_coefficient: Beta coefficient of thermister
    :return: Temperature of thermister in kelvin
    """
    voltage_sum = 0

    # Collect multiple readings and average their values
    for i in range(number_of_samples):

        # Calculate the voltage observed on the pico digital to analog converter
        voltage = thermister_pin.read_u16() * (3.3 / 65535)
        
        voltage_sum += voltage

    average_voltage = voltage_sum / number_of_samples

    # Calculate the resistance, of the NTC 3950 thermisterm which corresponds to the observed voltage
    observed_thermister_resistance = pullup_resistor_value / ((3.3 / average_voltage) -1)
    
    # Calculate the resistance in Kelvin using the Steinhart-Hart equation
    steinhart = observed_thermister_resistance / normal_thermister_resistance
    steinhart = math.log(steinhart)
    steinhart /= beta_coefficient
    steinhart += 1.0 / (25 + 273.15)
    steinhart = 1.0 / steinhart
    temperature = steinhart

    # Report the temperature over serial
    #print('Thermister Temperature: ' + str(temperature) + ' K')

    return temperature

def thermal_runaway_protection_check(thermister_pin, maximum_temperature, minimum_temperature):
    """"
    Function to check temperature observed by thermister.
    :Param thermister_pin: Analog pin to which thermister and voltage divider are connected
    :Param maximum_temperature: Upper limit for allowable observed temperature
    :Param minimum_temperature: Lower limit for allowable observed temperature
    :Param interval: How often to conduct thermal runaway checks (ms)
    :Param time_check: Time check variable 
    """

    # Observes the temperature of a thermister
    observed_temperature = get_temperature(thermister_pin, 3, thermister_pullup_resistor_value, NTC_3950_thermister_normal_resistance, NTC_3950_thermister_beta_coefficient)
    
    # Report observed_temperature
    print(str(thermister_pin) + ":" + str(observed_temperature) + " K")

    # Checks of observed temperature is higher than or equal to maximum_temperature
    if observed_temperature > maximum_temperature:

        # Reset pins to safe state, and report error
        set_default_pin_states()
        PWM_output.deinit()

        # Report problem
        print('Observed thermister temperature: ' + str(observed_temperature) + 'K, Shutting Down...')
        
        # Command CPU into low-power state to indefinitely pause program
        machine.deepsleep()

    # Checks of observed temperature is lower than or equal to minimum_temperature
    if observed_temperature < minimum_temperature:

        # Reset pins to safe state, and report error
        set_default_pin_states()
        PWM_output.deinit()

        # Report problem
        print('Observed thermister temperature: ' + str(observed_temperature) + 'K, Shutting Down...')
        
        # Command CPU into low-power state to indefinitely pause program
        machine.deepsleep()

def calculate_PWM_parameters():
    """
    Function to calculate PWM parameters of spark
    """

    global spark_period
    global spark_frequency
    global spark_duty_cycle

    # Calculate the spark period in microseconds
    spark_period = electrical_discharge_spark_period + electrical_discharge_recovery_period

    # Calculate the spark frequency in hertz
    spark_frequency = 1 / (spark_period / 1000000)

    # Calculate the spark duty cycle (0 - 1)
    spark_duty_cycle = (electrical_discharge_spark_period / (electrical_discharge_spark_period + electrical_discharge_recovery_period))

    if invert_MOSFET_logic == True: 
        spark_duty_cycle = 1 - spark_duty_cycle 

def enable_high_power_pwm():
    """
    Function to generate high-power EDM waveforms using the power MOSFET
    """

    global PWM_output

    # Assign PWM_output pin
    PWM_output = PWM(high_voltage_MOSFET_pin)

    # Set PWM frequency 
    PWM_output.freq(int(spark_frequency))

    # Initialize PWM with specific duty cycle
    PWM_output.duty_u16(round(spark_duty_cycle * 65535))

    #Turn on status LED 
    high_voltage_MOSFET_status_LED.on()

# Main code
# --------
# Initialize Powercore EDM power supply
print("Starting up...")
set_default_pin_states()
calculate_PWM_parameters()
enable_high_power_pwm()
print("initialized")

while True:
    user_LED.toggle()
    thermal_runaway_protection_check(thermister_1_analog_input, maximum_allowable_temperature_of_power_resistor, minimum_allowable_temperature_of_power_resistor)
    thermal_runaway_protection_check(thermister_2_analog_input, maximum_allowable_temperature_of_power_MOSFET, minimum_allowable_temperature_of_power_MOSFET)
    sleep(1)