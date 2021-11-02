from djitellopy import tello
from threading import Thread

drone = tello.Tello()
drone.connect()

print(f"Battery level: {drone.get_battery()}%")



def showState(drone):
    pass


