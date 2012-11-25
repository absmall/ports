import os
import subprocess
import shutil

run_commands = 1
print_commands = 0

def mv(src, dst):
    if print_commands:
        print "mv %s %s" % (src,dst)
    if run_commands:
        os.system("mv %s %s" % (src,dst))

def chdir(dir):
    if print_commands:
        print "cd %s" % dir
    os.chdir(dir)

def mkdir(dir):
    if print_commands:
        print "mkdir -p %s" % dir
    if run_commands:
        try:
            os.makedirs(dir)
        except OSError:
            # If directory exists, that's okay
            pass

def link(target, name):
    if print_commands:
        print "ln -s %s %s" % (target, name)
    if run_commands:
        print "ln -s %s %s" % (target, name)
        try:
            os.symlink(target, name)
        except OSError:
            # If link exists, that's probably okay
            pass

def command(cmd):
    if print_commands:
        for i in cmd.split('\n'):
            i = i.strip()
            if i != "":
                print i
    if run_commands:
        os.system(cmd)

def rmpath(dir):
    if print_commands:
        print "rm -rf %s" % dir
    if run_commands:
        try:
            shutil.rmtree(dir)
        except OSError:
            # If directory doesn't exist, that's okay
            pass

def git_create_repo():
    if print_commands:
        print "git init"
        print "git add *"
        print "git commit -m 'Initial commit'"
        print "git tag initial HEAD"
    if run_commands:
        os.system("git init")
        os.system("git add *")
        os.system("git commit -m 'Initial commit'")
        os.system("git tag initial HEAD")

def git_create_patch():
    if print_commands:
        print "git format-patch initial"
    if run_commands:
        return subprocess.check_output(["git","format-patch","initial"], ).split()

def git_apply_patch(patch):
    if print_commands:
        print "git am %s" % patch
    if run_commands:
        os.system("git am %s" % patch)
