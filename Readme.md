# Setup

Run this command to setup venv and install python modules

>Powershell.exe -executionpolicy remotesigned -File  .\init.ps1



## Findings

Placing computer vision functions in threads improves fps drasticly (as much as 50x), 
however this increases the delay to a point where the PID control is rendered useless.

When flying over uneven ground drone will keep it highest altitude, e.g going higher to clear obstacle but not come down after.