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

    if os.path.exists(download.find("result").text):
        print "Source for '%s' already downloaded" % package
    else:
        for i in download:
            if i.tag == "command":
                os.system(i.text)

def compilepackage(tree):
    build = tree.getroot().find("build")

    for i in build:
        os.system(i.text)

def packagepackage(tree, package):
    # Build a string for the command to execute
    command = "blackberry-nativepackager"

    # Package name
    command += " %s.bar ../blackberry-tablet.xml" % package

    packageNode = tree.getroot().find("package")
    for i in packageNode:
        if i.tag == "file":
            remote = i.get("remote")
            if remote:
                command += " -e \"%s\" %s" % (i.text, remote)
            else:
                command += " -e \"%s\" %s" % (i.text, i.text)
    os.system(command)

def build(package):

    os.chdir(package)

    # Read in the descriptor
    tree = etree.parse("package.xml")

    mkworkdir()
    os.chdir("src")
    downloadpackage(tree)
    compilepackage(tree)
    os.chdir("..")
    os.chdir("obj")
    packagepackage(tree, package)
    os.chdir("..")
    os.chdir("..")

# Go to ports directory
os.chdir(os.path.dirname(sys.argv[0]))
os.chdir("../ports")

# See what is there
if( len(sys.argv) > 1 ):
    packages = [ sys.argv[1] ]
else:
    packages = filter(lambda x: x[0]!='.', os.listdir("../ports"))

for package in packages:
    build(package)
