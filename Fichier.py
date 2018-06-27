import os
import datetime

DATE = datetime.date.today()
DATE_STRING = DATE.strftime("%Y-%m-%d")
MATERIAL = "LAITON"
TOOL = "1520"
COATING = "TRIO"
MODE = "AE"
COMMENT = "9"
ESPACE_NOM = "_"


NAME = (DATE_STRING+ESPACE_NOM+MATERIAL+ESPACE_NOM+TOOL+ESPACE_NOM+COATING+ESPACE_NOM+MODE+ESPACE_NOM+COMMENT)

EMPLACEMENT_1 = r"C:\Users\thibaut.nicoulin\PycharmProjects\Fichier"
print(NAME)
os.chdir(EMPLACEMENT_1)
os.mkdir(NAME)

EMPLACEMENT_2 = 'r"' + EMPLACEMENT_1 + "\\" +NAME + '"'
print(EMPLACEMENT_2)

os.chdir(EMPLACEMENT_2)
os.mkdir("00_DATA")
os.mkdir("01_PRG")
os.mkdir("02_CONFIG")

print("\\")