#!/usr/bin/env python
import os
import sys
import argparse
import shutil
from lxml import etree

print_commands_only = 0

def logged_chdir(dir):
    global print_commands_only

    if print_commands_only:
        print "cd %s" % dir
    os.chdir(dir)

def logged_mkdir(dir):
    global print_commands_only

    if print_commands_only:
        print "mkdir %s" % dir
    else:
        os.mkdir(dir)

def logged_command(cmd):
    global print_commands_only

    if print_commands_only:
        for i in cmd.split('\n'):
            i = i.strip()
            if i != "":
                print i
    else:
        os.system(cmd)

def logged_rmpath(dir):
    global print_commands_only

    if print_commands_only:
        print "rm -rf %s" % dir
    else:
        shutil.rmtree(dir)

def mkworkdir(clean):
    if clean:
        logged_rmpath("src")
        logged_rmpath("obj")
    try:
        logged_mkdir("src")
    except OSError as e:
        pass

    try:
        logged_mkdir("obj")
    except OSError as e:
        pass

def downloadpackage(tree):
    global print_commands_only

    # Check if the source is already available
    download = tree.getroot().find("download")

    logged_chdir("src")
    if os.path.exists(download.find("result").text):
        if not print_commands_only:
            print "Source for '%s' already downloaded" % package
    else:
        for i in download:
            if i.tag == "command":
                os.system(i.text)
    logged_chdir("..")

def compilepackage(tree):
    buildNode = tree.getroot().find("build")

    logged_chdir("src")
    # Build the package
    for i in buildNode:
        if i.tag == "command":
            logged_command(i.text)
    logged_chdir("..")


def packagepackage(tree, package):
    # Build a string for the command to execute
    command = "blackberry-nativepackager"

    # Package name
    command += " %s.bar ../blackberry-tablet.xml" % package

    packageNode = tree.getroot().find("package")
    logged_chdir("obj")
    for i in packageNode:
        if i.tag == "file":
            remote = i.get("remote")
            if remote:
                command += " -e \"%s\" %s" % (i.text, remote)
            else:
                command += " -e \"%s\" %s" % (i.text, i.text)
    logged_command(command)
    logged_chdir("..")

def build(package, clean):
    global basedir
    global built

    # See if this is already built
    if package in built:
        return

    # Go to ports directory
    logged_chdir("%s/%s" % (basedir, package))

    # Read in the descriptor
    tree = etree.parse("package.xml")

    # Build all dependencies
    for i in tree.getroot():
        if i.tag == "depends":
            build(i.text, clean)

    # Go back to ports directory in case we left to build dependencies
    logged_chdir("%s/%s" % (basedir, package))

    mkworkdir(clean)
    downloadpackage(tree)
    compilepackage(tree)
    packagepackage(tree, package)
    built += package

built = []

# Parse arguments
parser = argparse.ArgumentParser(description='Build packages for playbook')
parser.add_argument('-c', '--commands_only', action='store_const', const=1, help='Only print out the commands that would be executed, do not run them')
parser.add_argument('--clean', action='store_const', const=1, help='Remove all built code before beginning')
parser.add_argument('package', metavar='package', nargs='+', help='Package to build')
args = vars(parser.parse_args())

print_commands_only = args['commands_only']

# Go to ports directory
logged_chdir(os.path.dirname(sys.argv[0]))
logged_chdir("../ports")

basedir = os.getcwd()

# See what is there
if( len(args['package']) >= 1 ):
    packages = args['package']
else:
    packages = filter(lambda x: x[0]!='.', os.listdir("../ports"))

for package in packages:
    build(package, args['clean'])
