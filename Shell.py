import os, sys

try:
    while True:
        currentPath = os.getcwd()   #Get the current Path
        sys.ps1 = str(os.getpid()) + " " + "\033[30m" + currentPath + "$: " #Adding the process ID for testing purpouses
        userInput = input(sys.ps1)

        if(userInput == "exit()"):
            sys.exit()


        userInput = userInput.split(" ")
        lenOfInput = len(userInput)

        if userInput[0] == "cd":
            rc = os.fork()
            if rc < 0:
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)
            elif rc == 0:
                print("\n")
                if os.path.isdir(currentPath + "/" + userInput[1]):
                    os.chdir(currentPath + "/" + userInput[1])  # implement a try-catch
                else:
                    os.write(1, (userInput[1] + " is not a directory.\n").encode())
            else:
                os.wait()



        if userInput[0] == "ls":
            directories = os.listdir()  #Get directories and files inside directory
            for directory in directories:
                if os.path.isdir(currentPath + "/" + directory):
                    print('\033[94m' + directory, end=" ")
                else:
                    print("\033[30m" + directory, end=" ")
            print("\n")

except KeyboardInterrupt:
    os.write(1,("\nProcess Finished with exit code 0").encode())
