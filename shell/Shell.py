#! /usr/bin/env python3
import os
import sys
import re


def change_directory(cmd):  # Change directory
    current_path = os.getcwd()  #Get the current path
    if os.path.isdir(current_path + "/" + cmd[1]):  #Check if the given input is an actual directory
        os.chdir(current_path + "/" + cmd[1])


def execute_command(cmd):
    for directory in re.split(':', os.environ['PATH']):
        program = "%s/%s" % (directory, cmd[0])
        try:
            os.execve(program, cmd, os.environ)
        except FileNotFoundError:
            pass
        except ValueError:
            pass


def execute_path(cmd):
    try:
        os.execve(cmd[0], cmd, os.environ)
    except FileNotFoundError:
        pass


def execute(cmd):
    if '&' in cmd:
        cmd.remove('&')
    rc = os.fork()
    if rc < 0:
        # os.write(2, "fork failed".encode())
        sys.exit()
    elif rc == 0:
        if '/' in cmd[0]:
            execute_path(cmd[0])
        else:
            execute_command(cmd)
        # os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)
    else:
        if not '&' in cmd:
            child_pid_code = os.wait()


def output_redirection(cmd):
    if '&' in cmd:
        cmd.remove('&')
    rc = os.fork()
    if rc < 0:
        sys.exit(0)
    elif rc == 0:
        os.close(1)  # redirect child's stdout
        os.open(cmd[-1], os.O_CREAT | os.O_WRONLY);
        os.set_inheritable(1, True)
        cmd = cmd[0:cmd.index(">")]
        execute_command(cmd)
        sys.exit(1)
    else:
        if not '&' in cmd:
            child_pid_code = os.wait()


def input_redirection(cmd):
    if '&' in cmd:
        cmd.remove('&')
    rc = os.fork()
    if rc < 0:
        sys.exit(1)
    elif rc == 0:
        os.close(0)  # redirect child's stdin
        os.open(cmd[-1], os.O_RDONLY);
        os.set_inheritable(0, True)
        cmd = cmd[0:cmd.index("<")]
        execute_command(cmd)
        sys.exit(1)
    else:
        if not '&' in cmd:
            child_pid_code = os.wait()


def pipe_command(cmd):
    r, w = os.pipe()
    for f in (r, w):
        os.set_inheritable(f, True)
    commands = ' '.join([str(elem) for elem in cmd])
    commands = commands.split("|")
    command1 = commands[0].split()
    command2 = commands[1].split()
    commands = (command1, command2)
    main_process = True
    subprocesses = []
    even = 0
    for cmd in commands:
        even += 1
        if '&' in cmd:
            cmd.remove('&')
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
            execute_command(cmd)
            break
    if main_process:
        for i in (r, w):
            os.close(i)

        for subprocess in subprocesses:
            if not '&' in cmd:
                child_pid_code = os.wait()


def process_command(cmd):  # Select the command to execute
    if "exit()" in cmd:
        sys.exit(0)
    if not cmd:
        pass
    elif '/' in cmd[0]:
        execute_path(cmd)
    elif cmd == "\n":
        return
    elif "cd" in cmd:
        change_directory(cmd)
    elif "|" in cmd:
        pipe_command(cmd)
    elif ">" in cmd:
        output_redirection(cmd)
    elif "<" in cmd:
        input_redirection(cmd)
    else:
        execute(cmd)


if __name__ == '__main__':
    try:
        while True:

            pid = os.getpid()

            if 'PS1' in os.environ:
                os.write(1, (os.environ['PS1']).encode())
                try:
                    command = [str(n) for n in input().split()]
                except EOFError:
                    sys.exit(1)
            else:
                os.write(1, ('$ ').encode())
                try:
                    command = [str(n) for n in input().split()]
                except EOFError:
                    sys.exit(1)
            process_command(command)
    except KeyboardInterrupt:
        os.write(1, "\nProcess finished with exit code 0".encode())
