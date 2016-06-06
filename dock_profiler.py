#!/usr/bin/python
'''
Creates an installer package for Outset that loads a profile at login
for a specific user
'''

import argparse
import os
import shutil
import tempfile
import subprocess

p = argparse.ArgumentParser(description="Creates a package for Outset that will install a profile for a specific user on login.")
p.add_argument("-p","--profile", help='path to profile to load. Required, can use multiple times!', action='append', required=True)
p.add_argument("-n","--name", help='name of user to trigger on login. Required', required=True)
p.add_argument("-i","--identifier", help='identifier of package, defaults to "com.organization.profile"', default='com.organization.profile')
p.add_argument("-o","--output", help='path to output package, defaults to "Outset-Profile.pkg"', default='Outset-Profile.pkg')
p.add_argument('--once', help='load profile once, not every login',action='store_true')
p.add_argument("-s","--sign", help='sign package with valid identity',metavar='IDENTITY')
p.add_argument("-v","--version", help='version for package, defaults to 1.0', default='1.0')
arguments = p.parse_args()

libraryPath = 'Library/Profiles'
outsetPath = 'usr/local/outset/login-every'
if (arguments.once):
    outsetPath = 'usr/local/outset/login-once'

workingPath = tempfile.mkdtemp()
# Copy the profile into the temporary path
os.makedirs(os.path.join(workingPath, 'Outset-Dock-%s' % arguments.name, libraryPath, arguments.name))
print arguments.profile
for files in arguments.profile:
    shutil.copy(files, os.path.join(workingPath, 'Outset-Dock-%s' % arguments.name, libraryPath, arguments.name))

# Ensure Read Permissions of Profile
profilePath='{0}/{1}'.format(os.path.join(workingPath, 'Outset-Dock-%s' % arguments.name, libraryPath, arguments.name), os.listdir(os.path.join(workingPath, 'Outset-Dock-%s' % arguments.name, libraryPath, arguments.name))[0])
os.chmod('%s' % profilePath, 0755)
# Place the script into the outset folder in the temporary path
os.makedirs(os.path.join(workingPath, 'Outset-Dock-%s' % arguments.name, outsetPath))
# This is the base profile installer script
script='''#!/bin/bash
if [[ $USER == "{0}" ]]; then
    for p in /Library/Profiles/{0}/*;
    do
        /usr/bin/profiles -IvF "/Library/Profiles/{0}/$p"
    done
fi
'''.format(arguments.name)
# write script to file in temp directory
with open(os.path.join(workingPath, 'Outset-Dock-%s' % arguments.name, outsetPath, 'profile-%s.sh' % arguments.name), 'wb') as outsetScript:
    outsetScript.write(script)
os.chmod(os.path.join(workingPath, 'Outset-Dock-%s' % arguments.name, outsetPath, 'profile-%s.sh' % arguments.name), 0755)
# Call productbuild to create a package out of the temp folder
cmd = ['/usr/bin/pkgbuild', '--root', os.path.join(workingPath,'Outset-Dock-%s' % arguments.name), '--identifier', arguments.identifier, '--version', str(arguments.version), arguments.output]
if arguments.sign:
    cmd += ['--sign', arguments.sign]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(pbout, pberr) = proc.communicate()

if pberr:
    print "Error: %s" % pberr
print pbout
