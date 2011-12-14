#!/usr/bin/env python
import os
import sys
import libxml2

def mkworkdir():
    try:
        os.mkdir("src")
    except OSError as e:
        pass

    try:
        os.mkdir("obj")
    except OSError as e:
        pass

def downloadpackage(package):
    doc = libxml2.parseFile("../package.xml")
    ctxt = doc.xpathNewContext()

    # Check if the source is already available
    res = ctxt.xpathEval("/port/download/result/node()")
    if os.path.exists(str(res[0])):
        print "Source for '%s' already downloaded" % package
    else:
        res = ctxt.xpathEval("/port/download/command/node()")
        for i in res:
            os.system(str(i))
    doc.freeDoc()
    ctxt.xpathFreeContext()

def buildpackage(package):
    doc = libxml2.parseFile("../package.xml")
    ctxt = doc.xpathNewContext()

    # Check if the source is already available
    print os.getcwd()
    res = ctxt.xpathEval("/port/build/result/node()")
    res = ctxt.xpathEval("/port/build/command/node()")
    for i in res:
        os.system(str(i))
    doc.freeDoc()
    ctxt.xpathFreeContext()

def build(package):
    os.chdir(package)
    mkworkdir()
    os.chdir("src")
    downloadpackage(package)
    buildpackage(package)
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
