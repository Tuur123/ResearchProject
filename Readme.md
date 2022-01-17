# Setup

Run this command to setup venv and install python modules

>Powershell.exe -executionpolicy remotesigned -File  .\init.ps1



## Findings

Placing computer vision functions in threads improves fps drasticly (as much as 50x), 
however this increases the delay to a point where the PID control is rendered useless.

When flying over uneven ground drone will keep it highest altitude, e.g going higher to clear obstacle but not come down after.

When connecting to tello on device with more than 2 network adapters, windows will route those packets to the ethernet connection rather than wifi wich is connected to the tello.
This is fixed by modifying the djitellopy library.


## SOURCES

http://ncfrn.mcgill.ca/members/pubs/person_following_robot_icvs2017.pdf

https://medium.com/nanonets/how-i-built-a-self-flying-drone-to-track-people-in-under-50-lines-of-code-7485de7f828e