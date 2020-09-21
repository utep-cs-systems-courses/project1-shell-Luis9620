#! /usr/bin/env python3
import os
import sys
import re


def execute(args):  # execute command
    for directory in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s/%s" % (directory, args[0])    # Concatenate the directory and the program to execute
        try:
            os.execve(program, args, os.environ)    # execute the path with arguments and environment
        except FileNotFoundError:   # exception for not finding the file
            pass


def execute_path(args):     # execute path
    program = args[0]
    try:
        os.execve(program, args, os.environ)  # execute path given
    except FileNotFoundError:  # exception for not founding the file
        pass


def output_redirection(args):
    os.close(1) # Redirect child's stdout
    os.open(args[-1], os.O_CREAT | os.O_WRONLY) # Get last element in the command and open it as read only or create file if it does not exist
    os.set_inheritable(1, True) # Set the value of inheritable flag of the specified file descriptor(output).
    args = args[0:args.index(">")] # Get the command before the '>'
    execute(args)   # execute the command


def input_redirect(args):
    os.close(0) # Redirect child's stdin
    os.open(args[-1], os.O_RDONLY)  # Get last element in the command and open it as read only
    os.set_inheritable(0, True) # Set the value of inheritable flag of the specified file descriptor(input).
    args = args[0:args.index("<")]   # get the command before the '>'
    execute(args)   # execute the command


def pipe(cmd):
    args = ' '.join([str(elem) for elem in cmd])    # Separate each element in the command by an space  and cast it (string)
    pipes = args.split("|") # Split each of the pipes
    pipe1 = pipes[0].split()    # Separate each of the pipes
    pipe2 = pipes[1].split()

    pr, pw = os.pipe()  # Create pipe and return file descriptor for read and writing
    for f in (pr, pw):
        os.set_inheritable(f, True)     # Set the value of inheritable flag of the specified file descriptor(input-output).

    pipe_fork = os.fork()   # Create the subprocess
    if pipe_fork < 0:   # For any error in the creation of the fork
        os.write(2, "fork failed".encode())
        sys.exit(1)

    elif pipe_fork == 0:    # Child process
        os.close(1) # Redirect child's stdout
        os.dup(pw)  # Duplicate the file descriptor(pw)-not inheritable
        os.set_inheritable(1, True)     # Set the value of inheritable flag of the specified file descriptor(output).
        for fd in (pr, pw):  # Redirect child's stdout-stdin
            os.close(fd)
        execute(pipe1)  # Execute pipe

    else:   # Parent process
        os.close(0) # Redirect child's stdin
        os.dup(pr)  # Duplicate the file descriptor(pr)-not inheritable
        os.set_inheritable(0, True)
        for fd in (pw, pr):  # Redirect child's stdout-stdin
            os.close(fd)
        execute(pipe2)  # Execute pipe


def execute_command(cmd):   #Select the interaction with the os
    rc = os.fork()
    arguments = cmd.copy()
    if '&' in arguments:
        arguments.remove('&')
    if 'exit()' in arguments:
        sys.exit(0)
    if rc < 0:
        os.write(2, "Fork failed, returning".encode())
        sys.exit(1)
    elif rc == 0:
        if '>' in arguments:
            output_redirection(arguments)
        if '<' in arguments:
            input_redirect(arguments)
        if '/' in arguments[0]:
            execute_path(arguments)
        if '|' in arguments:
            pipe(arguments)
        else:
            execute(arguments)
    else:
        if '&' not in arguments:
            child_pid_code = os.wait()

# File descriptor
# 0 is for std input
# 1 is for std output
# 2 is for std error
if __name__ == '__main__':
    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
            try:
                command = [str(n) for n in input().split()]
            except EOFError:  # catch error
                sys.exit(1)
        else:
            os.write(1, '$ '.encode())
            try:
                command = [str(n) for n in input().split()]
            except EOFError:
                sys.exit(1)

        if "cd" in command:  # If there is a cd in the command given, change directory to the 2nd argument
            try:
                os.chdir(command[1])  # Change current directory to specified
            except FileNotFoundError:  # exception for not finding the file
                pass
            continue
        if not command:
            pass
        else:
            execute_command(command)



