## Introduction
The Checkers Game is a digital version of the classic board game. It includes both local multiplayer and a single-player mode against an AI bot with varying difficulty levels.

## Game Features
- Fullscreen Mode: Automatically adjusts to your screen resolution.
- Local Multiplayer: Play against another person locally.

## Installation


This program works on the Visual Studio Code IDE so any references may be exclusive to it. Although, it should be compatible with any IDE that can interpret Python.

Below are the steps to install the checkers game program:
Download the zip file and unzip it.
Select the Python file in the folder.
Open the game program in your IDE.
Run the program. 

If you run into issues with running the program because of errors with the “import pygame” line of code, refer to the troubleshooting section below





## Troubleshooting

This section is biased as it will be going over the troubleshooting for a Windows 10 PC user, but it should cover most possible issues one could encounter and may need to be tweaked for Win11 or any other OS.
The main issue one may encounter is that pygame is not installed. 
The fix to this is to enter the following in the IDE terminal or in command prompt.

“pip install pygame”

If the following doesn’t work, it could be due to python not being in your system PATH.
Test this by entering the following in command prompt

“python --version”
“pip --version”
If both commands are successful, try entering the install command in the command prompt instead of the IDE terminal. If either command fails to give output of version, it's likely due to python and/or pip not being in your system PATH. To check if python is installed, go to the following in your file path. [USERNAME] should be your username on your PC

C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python313\
If the python folder exists, verify that the Scripts folder exists within it and that pip and other utilities are within the Scripts folder. 
If these folders don’t exist, install them from the official python website.
Now it's time to add the Python313 folder and Scripts folder to PATH.
First, open the file explorer and right click “This PC” and select properties. 
On the Settings menu click “advanced system settings”.
On System Properties, select Environment Variables. It should be located under Advanced.
On Environment Variables, find Path in the system variables, select Path, and click on edit.
On Edit Environment Variables, Enter the below by selecting new and copy pasting it or typing it

C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python313\
C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python313\Scripts\
Once those have been entered, press ok to save changes.
Close and reopen Command Prompt to ensure changes have taken effect.

To verify install enter the following in Command Prompt.
“python --version”
“pip --version”
If they both work for you, you should be able to enter the below in Command Prompt to install pygame.

“pip install pygame”

Once you enter the above command it should show some information about it downloading. You should be able to run the game once it downloads. If it fails to run, close and reopen the program.
If it still fails to run, I would recommend finding more in depth troubleshooting online or retracing the steps given.
