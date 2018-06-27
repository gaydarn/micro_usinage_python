import os
import datetime
import tkinter
from tkinter import filedialog

config_temp = {
                "MATERIAL": "LAITON",
                "TOOL": "1520",
                "COATING": "TRIO",
                "MODE": "AE",
                "COMMENT": "10" }

MAINDIRPATH = None
DATADIRPATH = None
PRGDIRPATH = None
CONFIGDIRPATH = None

def create_folder_structure(config_xxx):
    global MAINDIRPATH, DATADIRPATH, PRGDIRPATH, CONFIGDIRPATH
    DATE = datetime.date.today()
    DATE_STRING = DATE.strftime("%Y%m%d")
    ESPACE_NOM = "_"
    MAINDIRNAME = (
                DATE_STRING + ESPACE_NOM + config_temp["MATERIAL"] + ESPACE_NOM + config_temp["TOOL"] + ESPACE_NOM +
                config_temp["COATING"] + ESPACE_NOM + config_temp["MODE"] + ESPACE_NOM + config_temp["COMMENT"])
    DATADIRNAME = "00_DATA"
    PRGDIRNAME = "01_PRG"
    CONFIGDIRNAME = "02_CONFIG"

    root = tkinter.Tk()
    BASENAME = filedialog.askdirectory(parent=root, initialdir="/", title='Please select a directory')
    # TODO: Why not quit tkinter?
    root.quit()

    MAINDIRPATH = os.path.join(BASENAME, MAINDIRNAME)
    DATADIRPATH = os.path.join(BASENAME, MAINDIRNAME, DATADIRNAME)
    PRGDIRPATH = os.path.join(BASENAME, MAINDIRNAME, PRGDIRNAME)
    CONFIGDIRPATH = os.path.join(BASENAME, MAINDIRNAME, CONFIGDIRNAME)

    os.mkdir(MAINDIRPATH)
    os.mkdir(DATADIRPATH)
    os.mkdir(PRGDIRPATH)
    os.mkdir(CONFIGDIRPATH)


