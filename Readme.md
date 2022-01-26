# Setup

Run this command to setup venv and install python modules

>Powershell.exe -executionpolicy remotesigned -File  .\init.ps1



## Findings

Placing computer vision functions in threads improves fps drasticly (as much as 50x), 
however this increases the delay to a point where the PID control is rendered useless.

When flying over uneven ground drone will keep it highest altitude, e.g going higher to clear obstacle but not come down after.

When connecting to tello on device with more than 2 network adapters, windows will route those packets to the ethernet connection rather than wifi wich is connected to the tello.
This is fixed by modifying the djitellopy library.

>![bind socket image](https://raw.githubusercontent.com/Tuur123/ResearchProject/main/docs/bind_socket.png)

posetracking with movenet doesnt give as much accuracy as with mediapipe.

PID's are hard to implement because of the latency, the drone always overshoot its target

Scanning the CovidSafe QR Code give an encoded string

drone resolution is not that great, scanning complex qr codes is not feasible

if someone uses phone of someone else, we can detect this because we will have 2 faces with the same qr code

not possible to run face identification on windows, running it on ubuntu vm

## SOURCES

http://ncfrn.mcgill.ca/members/pubs/person_following_robot_icvs2017.pdf

https://medium.com/nanonets/how-i-built-a-self-flying-drone-to-track-people-in-under-50-lines-of-code-7485de7f828e

https://www.section.io/engineering-education/multi-person-pose-estimator-with-python/