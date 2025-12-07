import logging
from gpiozero import LED
import adafruit_dht
import board


# Configure logging to simulate system output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [HARDWARE] - %(message)s")
logger = logging.getLogger(__name__)

# System state simulation (In-memory storage)
_system_state = {"light_status": "off"}

# GPIO Setup
ledGrn = LED(26)  # Using GPIO 26 for the light control

# DHT Sensor Setup (Assuming DHT22 on GPIO 16)
dhtDevice = adafruit_dht.DHT22(board.D16)


def control_light(status: str) -> str:
    """
    Simulates the control of a physical light via GPIO.

    Args:
        status (str): The desired state of the light ('on' or 'off').

    Returns:
        str: A message confirming the action execution.
    """
    status = status.lower()

    if status == "on":
        _system_state["light_status"] = "on"
        # Real implementation: gpio_led.on()
        ledGrn.on()

        # test to see if the led is really on
        if ledGrn.is_lit:
            logger.info("LIGHT TURNED ON (GPIO LOW)")
            return "The light has been turned on successfully."

        logger.error("Failed to turn on the light.")
        return "Error: Failed to turn on the light."

    elif status == "off":
        _system_state["light_status"] = "off"
        # Real implementation: gpio_led.off()
        ledGrn.off()

        if not ledGrn.is_lit:
            logger.info("🌑 LIGHT TURNED OFF (GPIO HIGH)")
            return "The light has been turned off successfully."

        logger.error("Failed to turn off the light.")
        return "Error: Failed to turn off the light."

    else:
        error_msg = f"Error: Invalid status '{status}'. Use 'on' or 'off'."
        logger.error(error_msg)
        return error_msg


def get_environment_metrics(location: str = "indoor") -> str:
    """
    Simulates reading data from a sensor.
    To implement real hardware later, initialize the DHT sensor globally above
    and read from it here.
    """
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        temp = temperature_c

        logger.info(f"SENSOR READ at {location}: {temp}°C, {humidity}%")
        return f"Temperature is {temp}°C and Humidity is {humidity}%."
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read,
        # just keep going
        logger.error(f"Runtime error reading sensor: {error.args[0]}")
        return "Error: Failed to read from the sensor."
