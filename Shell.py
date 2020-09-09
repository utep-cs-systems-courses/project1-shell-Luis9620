import os, sys

while(True):
    currentPath = os.getcwd()
    userInput = input("\033[30m" + currentPath + "$: ")
    if(userInput == "exit()"):
        sys.exit()
    userInput = userInput.split(" ")
    lenOfInput = len(userInput)
