def connect(config):
  import network
  import esp
  from time import sleep
  esp.osdebug(None)
  
  station = network.WLAN(network.STA_IF)
  station.active(True)
  for credential in config.credentials:
    if station.isconnected() == False:
        print("Trying to connect to " + credential['ssid'])
        station.connect(credential["ssid"], credential["password"])
        for i in range(50):
            sleep(0.1)
            if station.isconnected() == True:
                break
  if station.isconnected() == False:
    print("Could not establish a connection, please try again.")
  else:
    print(station.ifconfig())