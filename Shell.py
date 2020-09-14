import os, sys, re
def changeDirectory(command):
    currentPath = os.getcwd()
    command, selectedDirectory = re.split(" ", command)
    if os.path.isdir(currentPath + "/" + selectedDirectory):
        os.chdir(currentPath + "/" + selectedDirectory)

def showDirectories():
    currentPath = os.getcwd()
    directories = os.listdir()
    for directory in directories:
        if os.path.isdir(currentPath + "/" + directory):
            print('\033[94m' + directory, end=" ")
        else:
            print("\033[30m" + directory, end=" ")
    print("\n")

def executeCommand(command):
    if "exit()" in command:
        sys.exit(0)
    elif "cd" in command:
        changeDirectory(command)
    elif "ls" in command:
        showDirectories()

try:
    sys.ps1 = os.environ['PS1']
except KeyError:
    sys.ps1 = '$ '
if sys.ps1 is None:
    sys.ps1 = '$ '
try:
    while True:
        os.write(1, sys.ps1.encode())
        userInput = input()
        executeCommand(userInput)

except KeyboardInterrupt:
    os.write(1,("\nProcess Finished with exit code 0").encode())
