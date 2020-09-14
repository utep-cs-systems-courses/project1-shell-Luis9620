import os, sys, re


def change_directory(command):
    currentPath = os.getcwd()
    command, selectedDirectory = re.split(" ", command)
    if os.path.isdir(currentPath + "/" + selectedDirectory):
        os.chdir(currentPath + "/" + selectedDirectory)

def show_directories():
    currentPath = os.getcwd()
    directories = os.listdir()
    for directory in directories:
        if os.path.isdir(currentPath + "/" + directory):
            print('\033[94m' + directory, end=" ")
        else:
            print("\033[30m" + directory, end=" ")
    print("\n")


def execute(command):
    for directory in re.split(':', os.environ['PATH']):
        program = "%s/%s" % (directory, command[0])
        try:
            os.execve(program, command, os.environ)
        except FileNotFoundError:
            pass


def output_to_file(command):
    command, filePath = [i.strip() for i in re.split('>', command)]
    filePath = os.getcwd() + '/' + filePath
    command = [i.strip() for i in re.split(' ', command)]
    rc = os.fork()
    if rc < 0:
        os.write(2, ("Fork failed").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        sys.stdout = open(filePath, 'w+')
        fd = sys.stdout.fileno()
        os.set_inheritable(fd, True)
        os.dup(fd)
        execute(command)


def process_command(command):
    if "exit()" in command:
        sys.exit(0)
    elif "cd" in command:
        change_directory(command)
    elif "ls" in command:
        show_directories()
    elif ">" in command:
        output_to_file(command)


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
        process_command(userInput)

except KeyboardInterrupt:
    os.write(1, ("\nProcess Finished with exit code 0").encode())
