# Active Agent
 This is an automated Bot for the Interactify website
# Installation
### First go to the Microsot Store and install Python 3.12
### Open up Windows CMD and run the following command to install the necessary packages
```
pip install Pillow requests pyinstaller
```
### Now that the necessary packages are installed go to the link, click on the green 'Code' button the click 'Download ZIP'.
```
https://github.com/Ewsmyth/active-agent.git
```
### Once the zip file is downloads right click on it and select 'Extract All'. Before selecting 'Extract' select the browse button and navigate to the C Drive. This will extract the application files to the C drive so that it can be run for all users.
### In Windows CMD navigate to the active-agent folder.
```
cd C:\active-agent-main
```
### Once you are in the C:\active-agent-main folder you can build the .exe file
```
python3 -m PyInstaller --onefile --noconsole "Active Agent.py"
```
### If you want to make a shortcut on your desktop (which you should), right-click on your desktop and select 'new' and then 'shortcut', When the create shortcut wizard pops-up select 'Browse...' the file path to the .exe file is "C:\active-agent-main\dist\bot.exe" Then you can select 'Next'.