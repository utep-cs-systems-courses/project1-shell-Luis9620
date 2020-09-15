#! /usr/bin/env python3
import os
import sys
import re


def change_directory(command):
    current_path = os.getcwd()
    command, selected_directory = re.split(" ", command)
    if os.path.isdir(current_path + "/" + selected_directory):
        os.chdir(current_path + "/" + selected_directory)


def execute_command(command):
    for directory in re.split(':', os.environ['PATH']):
        program = "%s/%s" % (directory, command[0])
        try:
            os.execve(program, command, os.environ)
        except FileNotFoundError:
            pass
        except ValueError:
            pass


def execute_path(command):
    try:
        os.execve(command[0], command, os.environ)
    except FileNotFoundError:
        pass


def execute(command):
    rc = os.fork()
    if rc < 0:
        os.write(2, "fork failed".encode())
        sys.exit()
    elif rc == 0:
        command = [i.strip() for i in re.split(' ', command)]
        if '/' in command[0]:
            execute_path(command)
        else:
            execute_command(command)
        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)
    else:
        child_pid_code = os.wait()


def output_redirection(command):
    command, file_path = [i.strip() for i in re.split('>', command)]
    file_path = os.getcwd() + '/' + file_path
    command = [i.strip() for i in re.split(' ', command)]
    rc = os.fork()
    if rc < 0:
        os.write(2, "Fork failed".encode())
        sys.exit(0)
    elif rc == 0:
        os.close(1)
        sys.stdout = open(file_path, 'w+')
        fd = sys.stdout.fileno()
        os.set_inheritable(fd, True)
        os.dup(fd)
        execute_command(command)
        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)
    else:
        child_pid_code = os.wait()


def input_redirection(command):
    command, file_path = [i.strip() for i in re.split('<', command)]
    file_path = os.getcwd() + '/' + file_path
    command = [i.strip() for i in re.split(' ', command)]
    rc = os.fork()
    if rc < 0:
        os.write(2, "Fork failed".encode())
        sys.exit(1)
    elif rc == 0:
        os.close(0)
        sys.stdin = open(file_path, 'r')
        fd = sys.stdin.fileno()
        os.set_inheritable(fd, True)
        os.dup(fd)
        execute_command(command)
        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)
    else:
        child_pid_code = os.wait()


def pipe_command(command):
    r, w = os.pipe()
    for f in (r, w):
        os.set_inheritable(f, True)

    commands = [i.strip() for i in re.split('[\x7C]', command)]
    main_process = True
    subprocesses = []
    even = 0
    for command in commands:
        even += 1
        rc = os.fork()
        if rc:
            subprocesses.append(rc)
        else:
            main_process = False
            if even % 2 != 0:
                os.close(1)
                write = os.dup(w)
                for i in (r, w):
                    os.close(i)

                sys.stdout = os.fdopen(write, "w")
                fd = sys.stdout.fileno()
                os.set_inheritable(fd, True)
            else:
                os.close(0)
                read = os.dup(r)
                for i in (r, w):
                    os.close(i)

                sys.stdin = os.fdopen(read, "r")
                fd = sys.stdin.fileno()
                os.set_inheritable(fd, True)

            command = [i.strip() for i in re.split(' ', command)]
            execute_command(command)
            break
    if main_process:
        for i in (r, w):
            os.close(i)

        for subprocess in subprocesses:
            os.waitpid(subprocess, 0)


def process_command(command):
    if "exit()" in command:
        sys.exit(0)
    elif command == "\n":
        return
    elif "cd" in command:
        change_directory(command)
    elif "|" in command:
        pipe_command(command)
    elif ">" in command:
        output_redirection(command)
    elif "<" in command:
        input_redirection(command)
    else:
        execute(command)


try:
    sys.ps1 = os.environ['PS1']
except KeyError:
    sys.ps1 = '$ '

if sys.ps1 is None:
    sys.ps1 = '$ '

if __name__ == '__main__':
    try:
        while True:
            os.write(1, sys.ps1.encode())
            userInput = os.read(0, 1024).decode()[:-1]
            process_command(userInput)

    except KeyboardInterrupt:
        os.write(1, "\nProcess finished with exit code 0".encode())
