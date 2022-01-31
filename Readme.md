# Setup

Run this command on a windows machine to setup venv and install python modules

>Powershell.exe -executionpolicy remotesigned -File  .\init.ps1

Run these commands on Ubuntu
>sudo chmod +x init

>sudo ./init

<br>

# Use Guide

Once you've run the install scripts, start the server on the ubuntu VM first.
Then you can start the drone and connect your windows to the drones WiFi.

>![wifi image](https://raw.githubusercontent.com/Tuur123/ResearchProject/main/docs/wifi.png)

Then you can start the python script on the windows machine. The drone will take off after 2 seconds if you enable flying at line 10

>![flying enable](https://raw.githubusercontent.com/Tuur123/ResearchProject/main/docs/flying_enable.png)

You will see a livestream from the drones camera with some information on it such as a fps counter, battery percentage and what the drone is doing.
If a person is being tracked it will also draw some indicator lines on the persons face and the target of the drone.

>![stream](https://raw.githubusercontent.com/Tuur123/ResearchProject/main/docs/stream.png)

When the drone scans a QR Code you will see a secondary screen pop-up wich contains the face of the person and text wich tells you if the person scanned is SAFE or UNSAFE.

>![scanned person](https://raw.githubusercontent.com/Tuur123/ResearchProject/main/docs/scanned.png)

## Findings

Placing computer vision functions in threads improves fps drasticly (as much as 50x), 
however this increases the delay to a point where the PID control is rendered useless.

When flying over uneven ground drone will keep it highest altitude, e.g going higher to clear obstacle but not come down after.

When connecting to tello on device with more than 2 network adapters, windows will route those packets to the ethernet connection rather than wifi wich is connected to the tello.
This is fixed by modifying the djitellopy library. This is not possible on linux, where the kernel has absolute control over the routing and routing cant be changed.

>![bind socket image](https://raw.githubusercontent.com/Tuur123/ResearchProject/main/docs/bind_socket.png)

Posetracking with movenet doesnt give as much accuracy as with mediapipe.

PID's are hard to implement because of the latency, the drone always overshoot its target and they are really hard to finetune.

Scanning the CovidSafe QR Code give an encoded string wich cant be read, also the camera resolution of the drone used in this demo is not great, so scanning the complex offical codes is not feasible. That's why in this demo I supplied dummy codes (see QR folder).

If someone uses phone of someone else, this can be detected because there will be 2 faces with the same qr code.

Because the python face_recognition softawere uses dlib, I use a ubuntu VM to run all recognition code in. Installing dlib on windows should be possible but I never made it work.
If you're having issues with the server connection when using a VM, perhaps [my short tutorial](https://youtu.be/kc-t2D7QaUM) will help you.

<br>

## If you want to replicate this kind of project, have a look at these comminities for usefull tips and information
>https://www.reddit.com/r/pythontips/

>https://forum.opencv.org/

>https://groups.google.com/g/mediapipe


<br>
<br>

## SOURCES

Covidsafe. “Bewijs dat je Covid Safe bent.” Accessed January 21, 2022. https://covidsafe.be/nl/.
Chaiyadecha, Sasiwut. “How to Install Dlib Library for Python in Windows 10.” Analytics Vidhya (blog), July 25, 2020. https://medium.com/analytics-vidhya/how-to-install-dlib-library-for-python-in-windows-10-57348ba1117f.
“Dlib C++ Library.” Accessed January 31, 2022. http://dlib.net/.
Geitgey, Adam. “Machine Learning Is Fun! Part 4: Modern Face Recognition with Deep Learning.” Medium (blog), September 24, 2020. https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78.
“How to Detect QRCode and BarCode using OpenCV in Python + Project - YouTube.” Accessed January 25, 2022. https://www.youtube.com/.
“MediaPipe.” Accessed January 25, 2022. https://mediapipe.dev/.
Engineering Education (EngEd) Program | Section. “Multi-Person Pose Estimation with Python.” Accessed January 20, 2022. https://www.section.io/engineering-education/multi-person-pose-estimator-with-python/.
Palo, Norman Di. “How to Add Person Tracking to a Drone Using Deep Learning and NanoNets.” NanoNets (blog), July 13, 2018. https://medium.com/nanonets/how-i-built-a-self-flying-drone-to-track-people-in-under-50-lines-of-code-7485de7f828e.
Sandler, Mark, Andrew Howard, Menglong Zhu, Andrey Zhmoginov, and Liang-Chieh Chen. “MobileNetV2: Inverted Residuals and Linear Bottlenecks.” ArXiv:1801.04381 [Cs], March 21, 2019. http://arxiv.org/abs/1801.04381.

I particularly used https://mediapipe.dev/ very much, as the drone being able to accurately track persons is the largests cornerstone of this project.