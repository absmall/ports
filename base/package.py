#!/usr/bin/env python
import os
import sys
import libxml2

def gotodir(package):
	os.chdir(package)

def leavedir(package):
	os.chdir("../..")

def mkworkdir():
	#os.mkdir("obj")
	os.chdir("obj")

def downloadpackage(package):
	doc = libxml2.parseFile("../package.xml")
	ctxt = doc.xpathNewContext()
	res = ctxt.xpathEval("/port/download/command/node()")
	for i in res:
		os.system(str(i))
	doc.freeDoc()
	ctxt.xpathFreeContext()

def build(package):
	gotodir(package)
	mkworkdir()
	downloadpackage(package)
	leavedir(package)

if( len(sys.argv) > 1 ):
	packages = [ sys.argv[1] ]
else:
	packages = os.listdir("../ports")

for package in packages:
	os.chdir("../ports")
	build(package)
