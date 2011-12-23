#!/usr/bin/env python
import os
import sys
import libxml2
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

def packagepackage(package):
    # Build a string for the command to execute
    command = "blackberry-nativepackager"

    doc = libxml2.parseFile("../package.xml")
    ctxt = doc.xpathNewContext()

    # Package name
    #res = ctxt.xpathEval("/port/package/main/node()")
    command += " %s.bar ../blackberry-tablet.xml" % package

    res = ctxt.xpathEval("/port/package/file/node()")
    count = 1
    for i in res:
        try:
            res = str(ctxt.xpathEval("/port/package/file[%d]/@remote" % count)[0]).split('=')[1]
            command += " -e \"%s\" %s" % (str(i),res)
        except:
            command += " -e \"%s\" %s" % (str(i),str(i))
        count += 1
    os.system(command)

    doc.freeDoc()
    ctxt.xpathFreeContext()

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
    packagepackage(package)
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
