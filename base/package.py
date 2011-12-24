#!/usr/bin/env python
import os
import sys
from lxml import etree

def mkworkdir():
    try:
        os.mkdir("src")
    except OSError as e:
        pass

    try:
        os.mkdir("obj")
    except OSError as e:
        pass

def downloadpackage(tree):

    # Check if the source is already available
    download = tree.getroot().find("download")

    os.chdir("src")
    if os.path.exists(download.find("result").text):
        print "Source for '%s' already downloaded" % package
    else:
        for i in download:
            if i.tag == "command":
                os.system(i.text)
    os.chdir("..")

def compilepackage(tree):
    buildNode = tree.getroot().find("build")

    os.chdir("src")
    # Build the package
    for i in buildNode:
        if i.tag == "command":
            os.system(i.text)
    os.chdir("..")


def packagepackage(tree, package):
    # Build a string for the command to execute
    command = "blackberry-nativepackager"

    # Package name
    command += " %s.bar ../blackberry-tablet.xml" % package

    packageNode = tree.getroot().find("package")
    os.chdir("obj")
    for i in packageNode:
        if i.tag == "file":
            remote = i.get("remote")
            if remote:
                command += " -e \"%s\" %s" % (i.text, remote)
            else:
                command += " -e \"%s\" %s" % (i.text, i.text)
    os.system(command)
    os.chdir("..")

def build(package):
    global basedir
    global built

    # See if this is already built
    if package in built:
        return

    # Go to ports directory
    os.chdir("%s/%s" % (basedir, package))

    # Read in the descriptor
    tree = etree.parse("package.xml")

    # Build all dependencies
    for i in tree.getroot():
        if i.tag == "depends":
            build(i.text)

    # Go back to ports directory in case we left to build dependencies
    os.chdir("%s/%s" % (basedir, package))

    mkworkdir()
    downloadpackage(tree)
    compilepackage(tree)
    packagepackage(tree, package)
    built += package

built = []

# Go to ports directory
os.chdir(os.path.dirname(sys.argv[0]))
os.chdir("../ports")

basedir = os.getcwd()

# See what is there
if( len(sys.argv) > 1 ):
    packages = [ sys.argv[1] ]
else:
    packages = filter(lambda x: x[0]!='.', os.listdir("../ports"))

for package in packages:
    build(package)
