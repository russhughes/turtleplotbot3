"""
module button

    Button debounce and JoyStick classes



"""

# pylint: disable-msg=import-error, no-member
import time
import machine

# pylint: disable-msg=invalid-name
const = lambda x: x

UP = const(32)
DOWN = const(25)
LEFT = const(33)
RIGHT = const(26)
CENTER = const(27)
ZERO = const(0)
CHANGE = const(1)
ENTER = const(35)

# pylint: disable-msg=too-many-instance-attributes
class Button():
    """
    Button debounce class, handles button release and long presses.

    Args:
        pin (int): the pin number the button is connected to.
        debounce (int optional): the debounce time in ms, defaults to 50ms
        long: (int optional): the long press interval, defaults to 600ms, a
        value of 0 will disable reporting of long presses.
        active_high (bool optional): if True pin reads 1 when pressed. If False
        pin reads 0 when pressed. Defaults the True.

    """
    def __init__(self, pin, debounce=50,  long=600, active_low=False):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.active = 1
        self.state = 0
        self.last = 0
        self.last_ms = 0
        self.down = 0
        self.fired = 0
        self.debounce = debounce
        self.long = long
        self.active_low = active_low

    def modify(self, debounce=None, long=None):
        """
        Modify button debounce or long press timing

        Args:
            debounce (int): debounce time in ms
            long (int): long press time in ms
        """
        if debounce is not None:
            self.debounce = debounce

        if long is not None:
            self.long = long

    def read(self):
        """
        Read button with debounce and long press detection

        Returns:
            int: 0 if not pressed. 1 if pressed, -1 if long pressed
        """
        value = self.pin.value()
        if self.active_low:
            value ^= 1

        if value != self.last:
            self.last_ms = time.ticks_ms()

        if time.ticks_ms() - self.last_ms > self.debounce:
            if value != self.state:
                self.state = value
                self.fired = False

                if value == self.active:
                    self.down = time.ticks_ms()
                    return 1

            if self.long and self.state == self.active and not self.fired:
                if time.ticks_ms() - self.down > self.long:
                    self.fired = True
                    return -1

        self.last = value
        return 0

# pylint: disable-msg=too-few-public-methods
class JoyStick():
    """
    JoyStick class, handles reading a five way switch style joystick. Uses
    the Button class and supports long press notification.
    """
    def __init__(self, buttons=None):
        """
        Initialize JoyStick

        Args: buttons (list of tuples): The first tuple element should be the
            value to return when switch is pressed and released. The second
            tuple element should be a Button object for the switch.

        """
        if buttons is None:
            self.buttons = [
                (UP, Button(UP)),
                (DOWN, Button(DOWN)),
                (LEFT, Button(LEFT)),
                (RIGHT, Button(RIGHT)),
                (CENTER, Button(CENTER)),
                (CHANGE, Button(ZERO, long=0, active_low=True)),
                (ENTER, Button(ENTER, active_low=True))
            ]
        else:
            self.buttons = buttons

        self.max_ms = 0
        self.start_ms = 0

    def read(self, max_wait=0):
        """
        Read JoyStick

        Args: max_wait (optional int): maximum time to wait for button press
            in ms.

        Returns: int: the value of the button that was pressed and released.
            if the button definition did not set the parameter `long` to 0,
            and the button was pressed and held longer then the parameter
            `long` in ms the value returned will be negative. If `max_wait`
            was specified and `max_wait` ms pass without a button being
            pressed amd release a 0 will be returned.
        """
        self.max_ms = max_wait
        if max_wait:
            self.start_ms = time.ticks_ms()

        while True:
            for button in self.buttons:
                result = button[1].read()
                if result:
                    return button[0] * result

            if self.max_ms and time.ticks_ms() - self.start_ms > self.max_ms:
                return 0
