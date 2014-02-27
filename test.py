#!/usr/bin/python2

import os.path
import sys
import cm_sync
from urllib import urlretrieve
from subprocess import call, check_output
from xml.dom import minidom
import mmap
import git

print('STEP 0: Welcome to the CM Crowdin sync script\n')

print('STEP 1: Create cm_caf.xml')

if not os.path.isfile('caf.xml'):
    sys.exit('You have no caf.xml. Terminating')
xml = minidom.parse('caf.xml')
items = xml.getElementsByTagName('item')

cm_caf = []

for item in items:
    call(['mkdir', '-p', 'tmp/' + item.attributes["path"].value])
    item_aosp = item.getElementsByTagName('aosp')
    for aosp_item in item_aosp:
        url = aosp_item.firstChild.nodeValue
        path_to_base = 'tmp/' + item.attributes["path"].value + '/' + aosp_item.attributes["file"].value
        path_to_cm = item.attributes["path"].value + '/' + aosp_item.attributes["file"].value
        path = item.attributes["path"].value
        urlretrieve(url, path_to_base)
        cm_sync.create_cm_caf_xml(path_to_base, path_to_cm, path)
        cm_caf.append(path + '/cm_caf.xml')
        print('Created ' + path + '/cm_caf.xml')

#print('\nSTEP 2: Upload Crowdin source translations')
#print(check_output(["java", "-jar", "crowdin-cli.jar", "upload", "sources"]))

#print('STEP 3: Download Crowdin translations')
#print(check_output(["java", "-jar", "crowdin-cli.jar", "download"]))

print('STEP 4A: Clean up of empty translations')
# Search for all XML files
result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(os.getcwd()) for f in filenames if os.path.splitext(f)[1] == '.xml']
for xml_file in result:
    if '<resources/>' in open(xml_file).read():
        print ('Removing ' + xml_file)
        os.remove(xml_file)
    if '<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2"/>' in open(xml_file).read():
        print ('Removing ' + xml_file)
        os.remove(xml_file)    

print('\nSTEP 4B: Clean up of source cm_caf.xmls')
for cm_caf_file in cm_caf:
    print ('Removing ' + cm_caf_file)
    os.remove(cm_caf_file)

print('\nSTEP 5: Push translations to Git')
path_repo = os.getcwd() + '/packages/apps/Settings'
repo = git.Repo(path_repo)
print repo.git.add(path_repo)
print repo.git.commit(m='Automatic translations import')
print repo.git.push('ssh://cobjeM@review.cyanogenmod.org:29418/CyanogenMod/android_packages_apps_Settings', 'HEAD:refs/for/cm-11.0')

print('\nSTEP 6: Done!')