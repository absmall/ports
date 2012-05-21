#!/usr/bin/env python
import os
import sys
import argparse
import shutil
import commands
import subprocess
from lxml import etree

statically_package = 0
platforms = ["x86", "armv7"]

def version(platform):
    return subprocess.check_output(['nto'+platform+'-gcc', '-dumpmachine']).strip()

def mkworkdir(clean):
    global platform
    if clean:
        commands.rmpath("build")
    try:
        commands.mkdir("build")
    except OSError as e:
        pass

    try:
        commands.mkdir("build/"+platform)
    except OSError as e:
        pass

def downloadpackage(tree):
    # Check if the source is already available
    download = tree.getroot().find("download")

    commands.chdir("build")
    if os.path.exists(download.find("result").text):
        print "Source for '%s' already downloaded" % package
    else:
        for i in download:
            if i.tag == "command":
                commands.command(i.text)
        commands.git_create_repo()
        for i in download:
            if i.tag == "patch":
                commands.git_apply_patch("../%s" % i.text)
    commands.chdir("..")

def compilepackage(tree):
    buildNode = tree.getroot().find("build")

    commands.chdir("build")
    # Build the package
    for i in buildNode:
        if i.tag == "command":
            commands.command(i.text)
    commands.chdir("..")


def packagepackage(tree, package, devMode):
    # Build a string for the command to execute
    command = "blackberry-nativepackager"

    # Package name
    command += " %s.bar ../../blackberry-tablet.xml" % package

    packageNode = tree.getroot().find("package")
    commands.chdir("build/"+platform)
    if( devMode ):
        command += " -devMode"
    for i in packageNode:
        if i.tag == "file":
            remote = i.get("remote")
            if remote:
                target = remote
            else:
                target = i.text

            command += " -e \"%s\" %s" % (os.path.expandvars(i.text), target)
        elif i.tag == "argument":
            command += " -arg \"%s\"" % i.text
    commands.command(command)
    commands.chdir("../..")

def link(source, dest):
    global basedir

    # Go to ports directory
    commands.chdir("%s/%s" % (basedir, source))

    # Read in the descriptor
    tree = etree.parse("package.xml")

    # We need to follow the link paths to make sure
    # all necessary libraries are available
    for i in tree.getroot():
        if i.tag == "depends":
            commands.link(i.text, dest)

    exportNode = tree.getroot().find("export")

    commands.chdir("build/"+platform)
    # Make sure directories exist
    for i in exportNode:
        if i.tag == "file":
            remote = i.get("remote")
            if remote:
                target = remote
            else:
                target = i.text
            commands.mkdir("../../../%s/build/%s/%s" % (dest, platform, os.path.dirname(target)))
    # Setup symlinks
    for i in exportNode:
        if i.tag == "file":
            remote = i.get("remote")
            if remote:
                target = remote
            else:
                target = i.text
        commands.link(os.path.relpath(i.text, "../../../%s/build/%s/%s" % (dest, platform, os.path.dirname(target))), "../../../%s/build/%s/%s" % (dest, platform, target))
    commands.chdir("../..")

def build_patch(package):
    global basedir
    commands.chdir("%s/%s/build" % (basedir, package))

    # Generate the patches
    patches = commands.git_create_patch()
    for i in patches:
        commands.mv(i, "..")

    commands.chdir("..")

    # Read package.xml and update it with the patches
    tree = etree.parse("package.xml")
    download = tree.getroot().find("download")
    # Remove existing patches
    for i in download:
        if i.tag == "patch":
            download.remove(i)
    # Add in new ones
    for i in patches:
        patch = etree.Element("patch")
        patch.text = i
        download.append( patch )

    # Write package.xml back out with the changes
    package = open("package.xml", "w")
    package.write(etree.tostring(tree))
    package.close()

def build(package, deps, clean, devMode):
    global basedir
    global built
    global platform

    # See if this is already built
    if package in built:
        return

    # Go to ports directory
    commands.chdir("%s/%s" % (basedir, package))

    # Read in the descriptor
    tree = etree.parse("package.xml")

    # Build all dependencies
    if deps:
        for i in tree.getroot():
            if i.tag == "depends":
                build(i.text, deps, clean, devMode)

    # Go back to ports directory in case we left to build dependencies
    commands.chdir("%s/%s" % (basedir, package))

    # Give a target in which to install built files
    os.putenv("QNX_INSTALL", basedir+"/"+package+"/build/"+platform)

    # Set up the workspace
    mkworkdir(clean)

    # Link all dependencies
    for i in tree.getroot():
        if i.tag == "depends":
            print "Linking"
            link(i.text, package)

    # Back to ports directory in case we left to link dependencies
    commands.chdir("%s/%s" % (basedir, package))

    downloadpackage(tree)
    compilepackage(tree)
    packagepackage(tree, package, devMode)
    built += package

built = []

# Parse arguments
parser = argparse.ArgumentParser(description='Build packages for playbook')
parser.add_argument('-s', '--static', action='store_const', const=1, help='Include all shared libraries in the package (this is like statically linking the libraries')
parser.add_argument('-c', '--commands_only', action='store_const', const=1, help='Only print out the commands that would be executed, do not run them')
parser.add_argument('-v', '--verbose', action='store_const', const=1, help='Lots of output')
parser.add_argument('--clean', action='store_const', const=1, help='Remove all built code before beginning')
parser.add_argument('--dev', action='store_const', const=1, help='Build in development mode (can be loaded using a debug token, can be debugged, cannot be signed)')
parser.add_argument('--nodeps', action='store_const', const=1, help='Don\'t build dependencies, they have already been built.')
parser.add_argument('--prepare-patch', action='store_const', const=1, help='Create patch files for the package')
parser.add_argument('--platform', action='store', nargs='?', default="armv7", help='Platform to build for')
parser.add_argument('package', metavar='package', nargs='+', help='Package to build')
args = vars(parser.parse_args())

commands.print_commands = args['commands_only'] or args['verbose']
commands.run_commands = not args['commands_only']
statically_package = args['static']

# Go to ports directory
commands.chdir(os.path.dirname(sys.argv[0]))
commands.chdir("../ports")

basedir = os.getcwd()

# Set environment variables for the build to use
os.putenv("QNX_VERSION", version(args['platform']))
platform = args['platform']

# See what is there
if( len(args['package']) >= 1 ):
    packages = args['package']
else:
    packages = filter(lambda x: x[0]!='.', os.listdir("../ports"))

for package in packages:
    if args['prepare_patch']:
        build_patch(package)
    else:
        build(package, args['nodeps'] is None, args['clean'], args['dev'])
