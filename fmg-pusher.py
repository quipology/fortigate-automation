__author__ = 'Bobby Williams'

import pyautogui as pa
import time
from getpass import getpass
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

username = 'XXXX'
binary = FirefoxBinary(r'C:\XXX\Mozilla Firefox\firefox.exe')

success_log = []

def get_creds():
    #### Get login creds. ####
    global pw
    pw = getpass('Enter password for \'{}\': '.format(username))

def find_configs():
    #### Get a list of config files ####
    
    # Directory where the configs reside:
    config_dir = r'C:\XXX\XXX-fw-cfg-gen\generated'

    print('Checking for configs in: {} ...'.format(config_dir))
    os.chdir(config_dir)
    files = os.listdir('.')
    for i in files:
        if 'XXXS_MFGXXX' in i:
            print('Config files found!')
            return files
    print('No config files found, exiting..')
    sys.exit()
        
def get_driver():
    return webdriver.Firefox(firefox_binary=binary, executable_path=r'C:\Portable-Python27\App\selenium\webdriver\firefox\amd64\geckodriver.exe')

def login_to_fmg(driver, username=None, password=None):
    #### Open and login to FMG via Firefox ####
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    driver.get('https://10.160.129.140/login.htm')
    driver.find_element_by_id('username').send_keys(username)
    time.sleep(1)
    driver.find_element_by_id('secretkey').send_keys(password)
    time.sleep(1)
    driver.find_element_by_id('login_button').click()

def navigate_menus(data):
    # Go to scripts section:
    time.sleep(2)
    scripts = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\scripts.png')
    while not scripts:
        pa.click(29, 1829)
        time.sleep(1)
        scripts = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\scripts.png')

    # Lock ADOM:
    locked_adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\locked_adom.png')
    while not locked_adom:
        pa.click(351, 147)
        time.sleep(4)
        locked_adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\locked_adom.png')

    # Create new sript:
    create_script = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\create_script.png')
    while not create_script:
        pa.click(296, 186)
        time.sleep(1)
        create_script = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\create_script.png')

    # Set new script name:
    script_name = str(datetime.now())+'_auto'          
    pa.click(463, 207)
    time.sleep(1)
    pa.typewrite(script_name)
    time.sleep(1)

    # Select 'Policy Package, ADOM Database':
    pa.press(['tab', 'tab', 'tab'])
    time.sleep(1)
    pa.press('down')
    time.sleep(1)
    pa.press('enter')
    time.sleep(1)

    # Set config data:
    pa.press('tab')
    time.sleep(1)
    pa.typewrite(data)
    time.sleep(3)
    pa.press(['tab', 'tab'])
    time.sleep(1)
    pa.press('enter')
    time.sleep(3)

    # Select Run script on package:
    pa.click(1002, 210)
    time.sleep(1)
    pa.click(1002, 210)
    time.sleep(1)
    pa.rightClick(260, 232)
    time.sleep(.5)
    pa.press('down')
    time.sleep(.5)
    pa.press('up')
    time.sleep(.5)
    pa.press('enter')
    time.sleep(1)

    pkg_check = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\run-script-on-pkg.png')
    while pkg_check:
        pa.press('tab')
        time.sleep(.5)
        pa.press('tab')
        time.sleep(.5)
        pa.press('tab')
        time.sleep(1)
        pa.press('enter')
        time.sleep(2)
        pkg_check = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\run-script-on-pkg.png')

    # Save changes before pushing:
    save_changes = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\save-changes.png')
    while not save_changes:
        time.sleep(5)
        save_changes = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\save-changes.png')

    pa.click(466, 149) # Click the Save button
    time.sleep(2)
    pa.click(505, 107) # Click 'Policy & Objects' tab
    time.sleep(3)
    pa.moveTo(589, 146)
    time.sleep(1)
    pa.click(575, 195)

    # Install package step 1:
    time.sleep(5)
    pa.click(816, 1235)

    # Install package step 2:
    time.sleep(5)
    pa.click(816, 1235)

    # Install package step 3 (Validation):
    validation_check = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\validation.png')
    while not validation_check:
        time.sleep(3)
        validation_check = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\validation.png')
    pa.click(897, 1235)

def implement_configs(files):
    for i in files:
        ######################
        #### Trusted VDOM ####
        ######################
        if '01' in i and 'Trusted' in i:
            with open(i, 'r') as fi:
                data = fi.read()

            # Select the ADOM in the GUI:
            adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\01-Trusted.png')
            while not adom:
                time.sleep(1)
                pa.click(116, 150)
                pa.hotkey('ctrl', 'a')
                pa.press('backspace')
                pa.typewrite('XXXS_MFGXXXS01F_Trusted')
                time.sleep(1)
                pa.press('down')
                time.sleep(1)
                pa.press('enter')
                time.sleep(2)
                adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\01-Trusted.png')

            navigate_menus(data)

            print('Configuration file {} was implemented successfully!'.format(i))
            with open(r'C:\XXX\fmg-pusher\log', 'a') as fo:
                fo.write(str(datetime.now())+' - Configuration file {} was implemented successfully!\n'.format(i))

            sys.exit()
            
            
        '''    
        elif '02' in i and 'Trusted' in i:
            with open(i, 'r') as fi:
                data = fi.read()
            # Select the ADOM in the GUI:
            adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\02-Trusted.png')
            while not adom:
                time.sleep(1)
                pa.click(168, 146)
                pa.hotkey('ctrl', 'a')
                pa.press('backspace')
                pa.typewrite('XXXS_MFGXXXS02F_Trusted')
                time.sleep(1)
                pa.press('down')
                time.sleep(1)
                pa.press('enter')
                time.sleep(3)
                adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\02-Trusted.png')

            navigate_menus(data)

            print('Configuration file {} was implemented successfully!'.format(i))
            with open(r'C:\XXX\fmg-pusher\log', 'a') as fo:
                fo.write(str(datetime.now())+' - Configuration file {} was implemented successfully!\n'.format(i))

        elif '03' in i and 'Trusted' in i:
            with open(i, 'r') as fi:
                data = fi.read()
            # Select the ADOM in the GUI:
            adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\03-Trusted.png')
            while not adom:
                time.sleep(1)
                pa.click(168, 146)
                pa.hotkey('ctrl', 'a')
                pa.press('backspace')
                pa.typewrite('XXXS_MFGXXXS03F_Trusted')
                time.sleep(1)
                pa.press('down')
                time.sleep(1)
                pa.press('enter')
                time.sleep(3)
                adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\03-Trusted.png')
            
            navigate_menus(data)

            print('Configuration file {} was implemented successfully!'.format(i))
            with open(r'C:\XXX\fmg-pusher\log', 'a') as fo:
                fo.write(str(datetime.now())+' - Configuration file {} was implemented successfully!\n'.format(i))

        elif '04' in i and 'Trusted' in i:
            with open(i, 'r') as fi:
                data = fi.read()
            # Select the ADOM in the GUI:
            adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\04-Trusted.png')
            while not adom:
                time.sleep(1)
                pa.click(168, 146)
                pa.hotkey('ctrl', 'a')
                pa.press('backspace')
                pa.typewrite('XXXS_MFGXXXS04F_Trusted')
                time.sleep(1)
                pa.press('down')
                time.sleep(1)
                pa.press('enter')
                time.sleep(3)
                adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\04-Trusted.png')
            
            navigate_menus(data)

            print('Configuration file {} was implemented successfully!'.format(i))
            with open(r'C:\XXX\fmg-pusher\log', 'a') as fo:
                fo.write(str(datetime.now())+' - Configuration file {} was implemented successfully!\n'.format(i))

        elif '05' in i and 'Trusted' in i:
            with open(i, 'r') as fi:
                data = fi.read()
            # Select the ADOM in the GUI:
            adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\05-Trusted.png')
            while not adom:
                time.sleep(1)
                pa.click(168, 146)
                pa.hotkey('ctrl', 'a')
                pa.press('backspace')
                pa.typewrite('XXXS_MFGXXXS05F_Trusted')
                time.sleep(1)
                pa.press('down')
                time.sleep(1)
                pa.press('enter')
                time.sleep(3)
                adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\05-Trusted.png')

            navigate_menus(data)

            print('Configuration file {} was implemented successfully!'.format(i))
            with open(r'C:\XXX\fmg-pusher\log', 'a') as fo:
                fo.write(str(datetime.now())+' - Configuration file {} was implemented successfully!\n'.format(i))

        elif '06' in i and 'Trusted' in i:
            with open(i, 'r') as fi:
                data = fi.read()
            # Select the ADOM in the GUI:
            adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\06-Trusted.png')
            while not adom:
                time.sleep(1)
                pa.click(168, 146)
                pa.hotkey('ctrl', 'a')
                #time.sleep(2)
                pa.press('backspace')
                pa.typewrite('XXXS_MFGXXXS06F_Trusted')
                time.sleep(1)
                pa.press('down')
                time.sleep(1)
                pa.press('enter')
                time.sleep(3)
                adom = pa.locateOnScreen(r'C:\XXX\fmg-pusher\images\06-Trusted.png')
            
            navigate_menus(data)

            print('Configuration file {} was implemented successfully!'.format(i))
            with open(r'C:\XXX\fmg-pusher\log', 'a') as fo:
                fo.write(str(datetime.now())+' - Configuration file {} was implemented successfully!\n'.format(i))

        #### Datacenter (DC1) VDOM ####
            

        #### DC2 VDOM ####


        #### Untrusted VDOM ####


        #### 3rd Party VDOM ####
        '''
get_creds()
driver = get_driver()
login_to_fmg(driver, username=username, password=pw)
files = find_configs()
implement_configs(files)

