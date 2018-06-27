import os
import datetime
import tkinter
import json
from tkinter import filedialog


def load_config_file_manager(filename):
    infile = open('config_file_manager.json')
    config_file_manager = json.load(infile)
    infile.close()
    return config_file_manager

config_file_manager = load_config_file_manager('config_file_manager.json')

MAINDIRPATH = None
DATADIRPATH = None
PRGDIRPATH = None
CONFIGDIRPATH = None
EMPTYDATADIRPATH = None
MILLINGDATADIRPATH = None



def create_folder_structure(config_file_manager):
    global MAINDIRPATH, DATADIRPATH, PRGDIRPATH, CONFIGDIRPATH
    DATE = datetime.date.today()
    DATE_STRING = DATE.strftime("%Y%m%d%H")
    ESPACE_NOM = "_"
    MAINDIRNAME = (
                DATE_STRING + ESPACE_NOM + config_file_manager["MATERIAL"] + ESPACE_NOM + config_file_manager["TOOL"] + ESPACE_NOM +
                config_file_manager["COATING"] + ESPACE_NOM + config_file_manager["MODE"] + ESPACE_NOM + config_file_manager["COMMENT"])
    DATADIRNAME = "00_DATA"
    PRGDIRNAME = "01_PRG"
    CONFIGDIRNAME = "02_CONFIG"
    EMPTYDATADIRNAME = "00_EMPTY"
    MILLINGDATADIRNAME = "01_MILLING"

    root = tkinter.Tk()
    BASENAME = filedialog.askdirectory(parent=root, initialdir="/", title='Please select a directory')
    # TODO: Why not quit tkinter?
    root.quit()

    MAINDIRPATH = os.path.join(BASENAME, MAINDIRNAME)
    DATADIRPATH = os.path.join(BASENAME, MAINDIRNAME, DATADIRNAME)
    EMPTYDATADIRPATH = os.path.join(BASENAME, MAINDIRNAME, DATADIRNAME, EMPTYDATADIRNAME)
    MILLINGDATADIRPATH = os.path.join(BASENAME, MAINDIRNAME, DATADIRNAME, MILLINGDATADIRNAME)
    PRGDIRPATH = os.path.join(BASENAME, MAINDIRNAME, PRGDIRNAME)
    CONFIGDIRPATH = os.path.join(BASENAME, MAINDIRNAME, CONFIGDIRNAME)

    os.mkdir(MAINDIRPATH)
    os.mkdir(DATADIRPATH)
    os.mkdir(EMPTYDATADIRPATH)
    os.mkdir(MILLINGDATADIRPATH)
    os.mkdir(PRGDIRPATH)
    os.mkdir(CONFIGDIRPATH)


