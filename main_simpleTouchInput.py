"""Micropython module for stepper motor driven by Easy Driver."""
from machine import Pin
from time import sleep_us
import esp32


class Stepper:
    """Class for stepper motor driven by Easy Driver."""

    def __init__(self, step_pin, dir_pin, sleep_pin):
        """Initialise stepper."""
        self.stp = step_pin
        self.dir = dir_pin
        self.slp = sleep_pin

        self.stp.init(Pin.OUT)
        self.dir.init(Pin.OUT)
        self.slp.init(Pin.OUT)

        self.step_time = 20  # us
        self.steps_per_rev = 1600
        self.current_position = 0

    def get_current_position(self):
        return self.current_position

    def power_on(self):
        """Power on stepper."""
        self.slp.value(0)

    def power_off(self):
        """Power off stepper."""
        self.slp.value(1)

    def steps(self, step_count):
        """Rotate stepper for given steps."""
        self.dir.value(1 if step_count > 0 else 0)
        for i in range(abs(step_count)):
            self.stp.value(1)
            sleep_us(self.step_time)
            self.stp.value(0)
            sleep_us(self.step_time)
        self.current_position += step_count

    def rel_angle(self, angle):
        """Rotate stepper for given relative angle."""
        steps = int(angle / 360 * self.steps_per_rev)
        self.steps(steps)

    def abs_angle(self, angle):
        """Rotate stepper for given absolute angle since last power on."""
        steps = int(angle / 360 * self.steps_per_rev)
        steps -= self.current_position % self.steps_per_rev
        self.steps(steps)

    def revolution(self, rev_count):
        """Perform given number of full revolutions."""
        self.steps(rev_count * self.steps_per_rev)

    def set_step_time(self, us):
        """Set time in microseconds between each step."""
        if us < 20:  # 20 us is the shortest possible for esp8266
            self.step_time = 20
        else:
            self.step_time = us

# Just let it roll

if False:
    stepPin = Pin(2, Pin.OUT)
    dirPin = Pin(4, Pin.OUT)
    sleepPin = Pin(5, Pin.OUT)


    stepper = Stepper(stepPin, dirPin, sleepPin)
    stepper.set_step_time(500)
    stepper.power_on()

    print("stepper created")
    print("stepping stepps")
    stepper.steps(50000)
    stepper.power_off()

    print("done")

# Setting up Information
# Revs needed to go up / down completely

totalRevs = 5500
curerntState = 0 # 0 will mean all the way up and this is where we will start

# Function to wake up and trigger a up or down (Touch wake up not working in the moment, so I will not do that)

touchInput = False

# Build the interrupt
def handle_interrupt(pin):
  global touchInput
  touchInput = True
  global interrupt_pin
  interrupt_pin = pin 
pir = Pin(27, Pin.IN)
pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)
print("Interrupt created")

# Initializing the Stepper
stepPin = Pin(2, Pin.OUT)
dirPin = Pin(4, Pin.OUT)
sleepPin = Pin(5, Pin.OUT)
stepper = Stepper(stepPin, dirPin, sleepPin)
stepper.set_step_time(500)
print("Stepper Instance created")



from machine import TouchPad, Pin
tIn2 = TouchPad(Pin(15))
tIn2.config(1000)

while True:
    tIn2Touch = tIn2.read()
    if (tIn2Touch < 400):
        print("Touch Input recognized")
        stepper.power_on()
        if stepper.get_current_position() < 10:
            # Go Down
            stepper.steps(totalRevs)
            print("We went down")
        elif stepper.get_current_position() > (totalRevs - 10):
            # go Up
            stepper.steps(-totalRevs)
            print("We went up")
        stepper.power_off()
        touchInput = False
