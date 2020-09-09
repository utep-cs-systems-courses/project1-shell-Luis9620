import os, sys

sys.ps1 = "$"
while(True):
    currentPath = os.getcwd()   #Get the current Path
    sys.ps1 = "\033[30m" + currentPath + "$: "
    userInput = input(sys.ps1)
    if(userInput == "exit()"):
        sys.exit()
    userInput = userInput.split(" ")
    lenOfInput = len(userInput)
    if userInput[0] == "cd":
        try:
            os.chdir(currentPath + "/" + userInput[1])  # implement a try-catch
        except:
            continue
    if userInput[0] == "ls":
        directories = os.listdir()  #Get directories and files inside directory
        for directory in directories:
            if "." in directory:    #color the items without an extension(directories) blue
                print("\033[30m" + directory, end=" ")
            else:
                print('\033[94m' + directory, end=" ")
        print("\n")
