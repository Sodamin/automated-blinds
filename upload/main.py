try:
  import usocket as socket
except:
  import socket

import time

import gc
gc.collect()

# Script Routing
connectNetwork = True
initializeLights = True
ledTest = True
displayTest = False

# Settings
import config # Relevant Configs outsourced in config.py file

  

def commandFromRequest(request):
  try:
    mode = request[request.find('?mode=')+6:request.find('&')]
  except:
    mode = 'none'
  try:
    dir = request[request.find('&dir=')+5:request.find('&dir=')+7]
  except:
    dir = 'Error cannot understand command'
  command = {'mode': mode, 'dir': dir}
  return(command)

if connectNetwork:
  import web
  web.connect(config)


def web_page():
  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p><a href="/?mode=full&dir=do"><button class="button">Full Down</button></a></p> 
  <p><a href="/?mode=full&dir=up"><button class="button">Full Up</button></a></p> 
  </body></html>"""
  return html


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

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
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = str(conn.recv(1024))
    #print('Content = %s' % request)
    command = commandFromRequest(request)
    if command['mode'] == 'full':
        stepper.power_on()
        if command['dir'] == 'up':
            print("Going up")
            stepper.steps(-totalRevs)
            print("We went up")   
        elif command['dir'] == 'do':
            print("Going down")
            stepper.steps(totalRevs)
            print("We went down")
        else:
          print("Did not understand commmand: " + command['dir'])
        stepper.power_off()
    else:
        print('Command not recognized. Please try commands like http://host/?mode=full&dir=do')
    response = web_page()
    conn.send(b'HTTP/1.1 200 OK\n')
    conn.send(b'Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    
    conn.close()