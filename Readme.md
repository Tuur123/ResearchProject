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


Covidsafe. “Bewijs dat je Covid Safe bent.” Accessed January 21, 2022. https://covidsafe.be/nl/.
Chaiyadecha, Sasiwut. “How to Install Dlib Library for Python in Windows 10.” Analytics Vidhya (blog), July 25, 2020. https://medium.com/analytics-vidhya/how-to-install-dlib-library-for-python-in-windows-10-57348ba1117f.
“Dlib C++ Library.” Accessed January 31, 2022. http://dlib.net/.
Geitgey, Adam. “Machine Learning Is Fun! Part 4: Modern Face Recognition with Deep Learning.” Medium (blog), September 24, 2020. https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78.
“How to Detect QRCode and BarCode using OpenCV in Python + Project - YouTube.” Accessed January 25, 2022. https://www.youtube.com/.
“MediaPipe.” Accessed January 25, 2022. https://mediapipe.dev/.
Engineering Education (EngEd) Program | Section. “Multi-Person Pose Estimation with Python.” Accessed January 20, 2022. https://www.section.io/engineering-education/multi-person-pose-estimator-with-python/.
Palo, Norman Di. “How to Add Person Tracking to a Drone Using Deep Learning and NanoNets.” NanoNets (blog), July 13, 2018. https://medium.com/nanonets/how-i-built-a-self-flying-drone-to-track-people-in-under-50-lines-of-code-7485de7f828e.
Sandler, Mark, Andrew Howard, Menglong Zhu, Andrey Zhmoginov, and Liang-Chieh Chen. “MobileNetV2: Inverted Residuals and Linear Bottlenecks.” ArXiv:1801.04381 [Cs], March 21, 2019. http://arxiv.org/abs/1801.04381.
