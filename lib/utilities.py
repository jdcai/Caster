# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
from datetime import datetime
import natlink

import os, json, sys, time

from dragonfly import Key, BringApp
from dragonfly.grammar.recobs import RecognitionHistory
from dragonfly.timer import _Timer
import win32gui, win32process, win32api, win32ui

from lib.filter import Filter
import paths


MULTI_CLIPBOARD = {}
DICTATION_CACHE = RecognitionHistory(10)
DICTATION_CACHE.register()
TIMER_MANAGER = _Timer(1)
FILTER = Filter()
# FILTER.initialize()
# also need to do filter clean up, unloading






def window_exists(classname, windowname):
    try:
        win32ui.FindWindow(classname, windowname)
    except win32ui.error:
        return False
    else:
        return True

def press_digits(n):
    number = str(n)
    for digit in number:
        Key(digit).execute()
        
def get_active_window_hwnd():
    return str(win32gui.GetForegroundWindow())

def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def get_active_window_path():
    name = win32gui.GetForegroundWindow()
    t, p = win32process.GetWindowThreadProcessId(name)
    handle = win32api.OpenProcess(0x0410, False, p)
    return win32process.GetModuleFileNameEx(handle, 0)

def get_window_by_title(title):
    hwnd = win32gui.FindWindowEx(0, 0, 0, title)
    return hwnd

def clear_pyc():
    try:
        for dirpath, dirnames, files in os.walk(paths.BASE_PATH):  # os.walk produces a list of 3-tuples
            if r"MacroSystem\.git" in dirpath or r"MacroSystem\core" in dirpath:
                continue
            for f in files:
                if f.endswith(".pyc"):
                    f = os.path.join(dirpath, f)
                    os.remove(f)
                    report("Deleted: " + f)
    except Exception:
        report(list_to_string(sys.exc_info()))
            
def get_list_of_ccr_config_files():
    results = []
    for f in os.listdir(paths.GENERIC_CONFIG_PATH):
        if f.endswith(".txt"):
            f = f.replace("+", " plus")
            results.append(f.replace("config", "").replace(".txt", ""))
    return results
    

def save_json_file(data, path):
    try:
        formatted_data = json.dumps(data, sort_keys=True, indent=4,
            ensure_ascii=False)
        if not os.path.exists(path):
            f = open(path, "w")
            f.close()
        with open(path, "w") as f:
            f.write(formatted_data)
    except Exception as e:
        report("Could not save file: %s" % str(e))

def load_json_file(path):
    result = {}
    try:
        if os.path.isfile(path):  # If the file exists.
            with open(path, "r") as f:
                result = json.loads(f.read())
                f.close()
        else:
            save_json_file(result, path)
    except Exception as e:
        report("Could not load file: %s" % str(e))
    return result

def remote_debug(who_called_it=None):
    import pydevd;  # @UnresolvedImport
    if who_called_it == None:
        who_called_it = "An unidentified process"
    try:
        pydevd.settrace()
    except Exception:
        print "ERROR: " + who_called_it + " called utilities.remote_debug() but the debug server wasn't running."
    
def report(message, speak=False, console=True, log=False):
    if console:
        print message
    if speak:
        natlink.execScript("TTSPlayString \"" + message + "\"")
    if log:
        f = open(paths.LOG_PATH, 'a') 
        f.write(str(message) + "\n")
        f.close()
    
def list_to_string(l):
    return "\n".join([str(x) for x in l])

def current_time_to_string():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def get_most_recent(path, extension):
    recent = 0
    for f in os.listdir(path):
        if f.endswith(extension):
            cur = int(f)
            if cur > recent:
                recent = cur
    if recent == 0:
        return None
    return str(recent) + extension

def clean_temporary_files():
    temp_folders = [paths.MONITOR_INFO_PATH]
    for p in temp_folders:
        if os.path.exists(p):
            for f in os.listdir(p):
                os.remove(p + f)

def scan_monitors():
    if not os.path.exists(paths.MONITOR_INFO_PATH):
        os.makedirs(paths.MONITOR_INFO_PATH)
    monitor_scan_path = paths.MONITOR_INFO_PATH + current_time_to_string() + ".txt"
    BringApp(paths.MMT_PATH, r"/stext", monitor_scan_path)._execute()
    time.sleep(1)
    return monitor_scan_path

def parse_monitor_scan(monitor_scan_path):
    monitors = {"active": [], "inactive": []}
#     content = None
    with codecs.open(monitor_scan_path, "r", encoding="utf-16") as f:
        content = f.readlines()
#     is_active = False
#     active_monitors = []
#     inactive_monitors = []
#     resolution = None
    current_monitor = None
    # Maximum Resolution: 1600 X 900
    # remote_debug()
    for line in content:
        line = line.replace(" ", "")
        if line.startswith("Resolution"):
            current_monitor = {"resolution":(1600 , 900), "maximum":None, "active":False, "name":""}
        elif line.startswith("Orientation"):
            current_monitor["orientation"] = line.split(":")[1]
        elif line.startswith("Maximum"):
            current_monitor["maximum"] = line.split(":")[1].split("X")
            current_monitor["maximum"][0] = int(current_monitor["maximum"][0])
            current_monitor["maximum"][1] = int(current_monitor["maximum"][1].replace("\r\n", ""))
        elif line.startswith("Active"):
            current_monitor["active"] = line.split(":")[1].startswith("Yes")
        elif line.startswith("Name"):
            current_monitor["name"] = line.split(":")[1].replace("\r\n", "")
            if current_monitor["active"]:
                monitors["active"].append(current_monitor)
            else:
                monitors["inactive"].append(current_monitor)
    return monitors

def subtract_matrices(matrix_a, matrix_b):
    result = []
    for i in xrange(len(matrix_a)):
        tmp = []
        for a, b in zip(matrix_a[i], matrix_b[i]):
            tmp.append(a - b)
        result.append(tmp[:])
    return result[:]



def py2exe_compile(choice):
    # the contents of this function have been replaced by instructions to do it manually
    #
    # copy generic dependencies: something_run.py, ["utilities.py", "paths.py", "settings.py"], ["compile.bat", "icon.ico", "msvcp90.dll", "msvcr90.dll"]
    # rename something_run.py to run.py
    # copy the python file
    # copy specific dependencies 
    # (dptools requires ["argparse.py", "_keyCodes.py", "_myclickLocations.py", "_mycommon.py"])
    # (element requires "tk85.dll", "tcl85.dll")
    # run the batch file compile.bat
    print "this function has been removed "