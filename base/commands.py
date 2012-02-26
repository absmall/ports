import os
import subprocess

print_commands_only = 0

def mv(src, dst):
    if print_commands_only:
        print "mv %s %s" % (src,dst)
    else:
        os.system("mv %s %s" % (src,dst))

def chdir(dir):
    if print_commands_only:
        print "cd %s" % dir
    os.chdir(dir)

def mkdir(dir):
    if print_commands_only:
        print "mkdir -p %s" % dir
    else:
        try:
            os.makedirs(dir)
        except OSError:
            # If directory exists, that's okay
            pass

def link(target, name):
    if print_commands_only:
        print "ln -s %s %s" % (target, name)
    else:
        print "ln -s %s %s" % (target, name)
        os.system("ln -s %s %s" % (target, name))

def command(cmd):
    if print_commands_only:
        for i in cmd.split('\n'):
            i = i.strip()
            if i != "":
                print i
    else:
        os.system(cmd)

def rmpath(dir):
    if print_commands_only:
        print "rm -rf %s" % dir
    else:
        try:
            shutil.rmtree(dir)
        except OSError:
            # If directory doesn't exist, that's okay
            pass

def git_create_repo():
    if print_commands_only:
        print "git init"
        print "git add *"
        print "git commit -m 'Initial commit'"
        print "git tag initial HEAD"
    else:
        os.system("git init")
        os.system("git add *")
        os.system("git commit -m 'Initial commit'")
        os.system("git tag initial HEAD")

def git_create_patch():
    if print_commands_only:
        print "git format-patch initial"
    else:
        return subprocess.check_output(["git","format-patch","initial"], ).split()

def git_apply_patch(patch):
    if print_commands_only:
        print "git am %s" % patch
    else:
        os.system("git am %s" % patch)
