#!/usr/bin/env python
import os
import sys
import argparse
import shutil
import subprocess
from lxml import etree

statically_package = 0
print_commands_only = 0

def logged_mv(src, dst):
    global print_commands_only

    if print_commands_only:
        print "mv %s %s" % (src,dst)
    else:
        os.system("mv %s %s" % (src,dst))

def logged_chdir(dir):
    global print_commands_only

    if print_commands_only:
        print "cd %s" % dir
    os.chdir(dir)

def logged_mkdir(dir):
    global print_commands_only

    if print_commands_only:
        print "mkdir -p %s" % dir
    else:
        try:
            os.makedirs(dir)
        except OSError:
            # If directory exists, that's okay
            pass

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
        try:
            shutil.rmtree(dir)
        except OSError:
            # If directory doesn't exist, that's okay
            pass

def logged_git_create_repo():
    global print_commands_only

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

def logged_git_create_patch():
    global print_commands_only

    if print_commands_only:
        print "git format-patch initial"
    else:
        return subprocess.check_output(["git","format-patch","initial"], ).split()

def logged_git_apply_patch(patch):
    global print_commands_only

    if print_commands_only:
        print "git am %s" % patch
    else:
        os.system("git am %s" % patch)

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

def logged_link(target, name):
    global print_commands_only

    if print_commands_only:
        print "ln -s %s %s" % (target, name)
    else:
        print "ln -s %s %s" % (target, name)
        os.system("ln -s %s %s" % (target, name))

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
                logged_command(i.text)
        logged_git_create_repo()
        for i in download:
            if i.tag == "patch":
                logged_git_apply_patch("../%s" % i.text)
    logged_chdir("..")

def compilepackage(tree):
    buildNode = tree.getroot().find("build")

    logged_chdir("src")
    # Build the package
    for i in buildNode:
        if i.tag == "command":
            logged_command(i.text)
    logged_chdir("..")


def packagepackage(tree, package, devMode):
    # Build a string for the command to execute
    command = "blackberry-nativepackager"

    # Package name
    command += " %s.bar ../blackberry-tablet.xml" % package

    packageNode = tree.getroot().find("package")
    logged_chdir("obj")
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
    logged_command(command)
    logged_chdir("..")

def link(source, dest):
    global basedir

    # Go to ports directory
    logged_chdir("%s/%s" % (basedir, source))

    # Read in the descriptor
    tree = etree.parse("package.xml")

    # We need to follow the link paths to make sure
    # all necessary libraries are available
    for i in tree.getroot():
        if i.tag == "depends":
            link(i.text, dest)

    exportNode = tree.getroot().find("export")

    logged_chdir("obj")
    # Make sure directories exist
    for i in exportNode:
        if i.tag == "file":
            logged_mkdir("../../%s/obj/%s" % (dest, os.path.dirname(i.text)))
    # Setup symlinks
    for i in exportNode:
        if i.tag == "file":
            logged_link(os.path.relpath(i.text, "../../%s/obj/%s" % (dest, os.path.dirname(i.text))), "../../%s/obj/%s" % (dest, i.text))
    logged_chdir("..")

def build_patch(package):
    global basedir
    logged_chdir("%s/%s/src" % (basedir, package))

    # Generate the patches
    patches = logged_git_create_patch()
    for i in patches:
        logged_mv(i, "..")

    logged_chdir("..")

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

    # See if this is already built
    if package in built:
        return

    # Go to ports directory
    logged_chdir("%s/%s" % (basedir, package))

    # Read in the descriptor
    tree = etree.parse("package.xml")

    # Build all dependencies
    if deps:
        for i in tree.getroot():
            if i.tag == "depends":
                build(i.text, deps, clean, devMode)

    # Go back to ports directory in case we left to build dependencies
    logged_chdir("%s/%s" % (basedir, package))

    # Set up the workspace
    mkworkdir(clean)

    # Link all dependencies
    for i in tree.getroot():
        if i.tag == "depends":
            link(i.text, package)

    # Back to ports directory in case we left to link dependencies
    logged_chdir("%s/%s" % (basedir, package))

    downloadpackage(tree)
    compilepackage(tree)
    packagepackage(tree, package, devMode)
    built += package

built = []

# Parse arguments
parser = argparse.ArgumentParser(description='Build packages for playbook')
parser.add_argument('-s', '--static', action='store_const', const=1, help='Include all shared libraries in the package (this is like statically linking the libraries')
parser.add_argument('-c', '--commands_only', action='store_const', const=1, help='Only print out the commands that would be executed, do not run them')
parser.add_argument('--clean', action='store_const', const=1, help='Remove all built code before beginning')
parser.add_argument('--dev', action='store_const', const=1, help='Build in development mode (can be loaded using a debug token, can be debugged, cannot be signed)')
parser.add_argument('--nodeps', action='store_const', const=1, help='Don\'t build dependencies, they have already been built.')
parser.add_argument('--prepare-patch', action='store_const', const=1, help='Create patch files for the package')
parser.add_argument('package', metavar='package', nargs='+', help='Package to build')
args = vars(parser.parse_args())

print_commands_only = args['commands_only']
statically_package = args['static']

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
    if args['prepare_patch']:
        build_patch(package)
    else:
        build(package, args['nodeps'] is None, args['clean'], args['dev'])
