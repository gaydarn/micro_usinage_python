#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import math
import json
import ntpath

colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

def main():

    # Chargement du fichier de configuration
    config = load_config('config.json')

    # Calcul des paramètres d'usinage
    parameters = compute_parameters(config)

    # Création du programme de surfaçage
    progname_surface_milling = "micro_usinage/sub_spirale_surface_milling.nc"
    create_prog_surface_milling(config, parameters, progname_surface_milling)

    # Création du programme de mesure
    progname_spirale_measurement = "micro_usinage/sub_spirale_measurements.nc"
    create_prog_spirale_measurements(config, parameters, progname_spirale_measurement)

    progname_main = "micro_usinage/main.nc"
    create_prog_main(config, progname_main, progname_surface_milling, progname_spirale_measurement)

def create_prog_main(config, progname_main, progname_surface_milling, progname_spirale_measurement):
    # Création du fichier et écriture des entètes
    file = open(progname_main, "w")
    file.writelines(";**********************\n")
    file.writelines(";PROGRAMME PRINCIPAL\n")
    file.writelines(";              **********************\n\n")
    # Début du programme (statique)
    file.writelines("T1 M6\n")
    file.writelines("G53 G01 Z+24 F1000\n")
    file.writelines("G55 G90\n")

    file.writelines("L {}\n".format(path_leaf(progname_surface_milling)))
    file.writelines("L {}\n".format(path_leaf(progname_spirale_measurement)))
    file.writelines("M05\n")
    file.writelines("T0 M6\n")
    file.writelines("M30\n")

def create_prog_surface_milling(config, parameters, filename):

    # Condition initiales
    r = config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"] / 2 + config["SURPLUS_PREM_PASSE"]
    theta = 0
    vf = parameters[0]["Vf"]
    x_list = []
    y_list = []
    # Création du fichier et écriture des entètes
    file = open(filename, "w")
    write_headers(config, file, parameters, "SURFACAGE")
    # Début du programme (statique)
    #file.writelines("T1 M6\n")
    #file.writelines("G55 G90\n")
    file.writelines("# HSC[OPMODE 2 CONTERROR 0.02]\n")
    file.writelines("# HSC ON\n")
    file.writelines("M03 S{}\n".format(parameters[0]["n"]))
    file.writelines("G0 X{} Y0 Z10\n".format(config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"]))  # 1/2 largeur de fraise de marge
    file.writelines("G1 Z{} F1000\n".format(config["PROF_PASSE"]))

    while r > (config["DIAM_FRAISE"] / 2) - 0.05:

        # Calcul de coordonées cartésiennes
        x, y = pol2cart(r, theta, config["NB_DECIMALES"])
        x_list.append(x)
        y_list.append(y)
        # Calcul des prochaines coordonées polaires
        theta += config["ANGLE_CHANGE_DIAM"]
        r += config["LARG_PASSE"] / (360 / math.fabs(config["ANGLE_CHANGE_DIAM"]))

        # Log pour la génération du programme
        file.writelines("G1 X{} Y{} Z{} F{}\n".format(x, y, config["PROF_PASSE"], vf))

    file.writelines("G1 Z10\n")
    file.writelines("# HSC OFF\n")
    #file.writelines("M05\n")
    file.writelines("M17\n")
    # file.writelines("M6 T0\n")
    #file.writelines("M30\n")
    file.close()
    ax = plt.subplot(111)
    plt.title("Surface milling")
    ax.plot(x_list, y_list, 'g-')
    max_dist = (config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"] / 2) * 1.2
    plt.xlim(-max_dist, max_dist)
    plt.ylim(-max_dist, max_dist)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def create_prog_spirale_measurements(config, parameters, filename):

    # Condition initiales
    r = config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"] / 2 + config["SURPLUS_PREM_PASSE"]
    r_old = r
    theta = 0
    theta_old = theta
    dist = 0
    index_param = 0
    target_dist = parameters[index_param]["dist"] + config["NB_TOURS_RESERVE"] * math.pi * config["DIAM_PIECE"]
    x_list = []
    x_list_tmp = []
    y_list = []
    y_list_tmp = []
    flag_measurement_complete = False
    vf = parameters[index_param]["Vf"]
    # Création du fichier et écriture des entètes
    file = open(filename, "w")
    write_headers(config, file, parameters, "SPIRALE DE MESURE")
    # Début du programme (statique)
    file.writelines("T1 M6\n")
    file.writelines("G55 G90\n")
    file.writelines("# HSC[OPMODE 2 CONTERROR 0.02]\n")
    file.writelines("# HSC ON\n")
    file.writelines("M03 S{}\n".format(parameters[index_param]["n"]))
    file.writelines("G0 X{} Y0 Z10\n".format(config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"]))  # 1/2 largeur de fraise de marge
    file.writelines("G1 Z{} F1000\n".format(config["PROF_PASSE"]))
    file.writelines("N{}:\n".format(index_param + 1))
    while r > (config["DIAM_FRAISE"] / 2) - 0.05:

        # Calcul de coordonées cartésiennes
        x, y = pol2cart(r, theta, config["NB_DECIMALES"])

        # Calcul de la distance parcourue
        dist += r_old * math.radians(math.fabs(theta - theta_old))
        # Sauvegarde des valeurs pour les calculs à la boucle suivante
        r_old = r
        theta_old = theta
        # Calcul des prochaines coordonées polaires
        theta += config["ANGLE_CHANGE_DIAM"]
        r += config["LARG_PASSE"] / (360 / math.fabs(config["ANGLE_CHANGE_DIAM"]))

        # Log pour la génération du programme et l'affichage
        file.writelines("G1 X{} Y{} Z{} F{}\n".format(x, y, config["PROF_PASSE"], vf))

        if not flag_measurement_complete:
            # Log pour l'affichage
            x_list_tmp.append(x)
            y_list_tmp.append(y)

            # Passage à la vitesse suivante si la distance cible est atteinte
            if dist >= target_dist and not index_param >= len(parameters):
                x_list.append(x_list_tmp.copy())
                x_list_tmp.clear()
                y_list.append(y_list_tmp.copy())
                y_list_tmp.clear()
                index_param += 1
                # Contrôle si la mesure est terminée
                if index_param >= len(parameters):
                    # TODO configure vitesse de base
                    flag_measurement_complete = True
                else:
                    vf = parameters[index_param]["Vf"]
                    target_dist += math.ceil(parameters[index_param]["dist"])
                    file.writelines("N{}:\n".format(index_param + 1))
                    file.writelines("M03 S{}\n".format(math.floor(parameters[index_param]["n"])))
    msg = "Error!"
    dist = round(dist, 2)
    if flag_measurement_complete:
        msg = "Measurement have been programmed without issue, with a total milling distance of {}".format(dist)
    else:
        msg = "The maximum milling distance of {} is not enough to make all the measurement!".format(dist)
    file.writelines(";" + str(msg))
    print(msg)
    file.writelines("G1 Z10\n")
    file.writelines("# HSC OFF\n")
    #file.writelines("M05\n")
    file.writelines("M17\n")
    #file.writelines("M30\n")
    file.close()
    ax = plt.subplot(111)
    plt.title(msg)
    for ix, item in enumerate(x_list):
        ax.plot(x_list[ix], y_list[ix], colors[ix % len(colors)])
    max_dist = (config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"] / 2) * 1.2
    plt.xlim(-max_dist, max_dist)
    plt.ylim(-max_dist, max_dist)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def load_config(filename):
    infile = open('config.json')
    config = json.load(infile)
    infile.close()
    return config

def compute_parameters(config):
    parameters = []

    # for vc in np.arange(config["VC_MOY"], config["VC_MAX"] + 1, config["VC_STEP"]):
    #     n = math.floor(1000 * vc / (config["DIAM_FRAISE"] * math.pi))
    #     vf = math.floor(config["NB_DENTS"] * config["FZ"] * n)
    #     dist = math.floor(vf / 60 * config["TEMPS_MESURE"])
    #     parameters.append({"Vc": vc, "n": n, "Vf": vf, "dist": dist})

    tab_range = np.arange(config["VC_MIN"], config["VC_MAX"], config["VC_STEP"])
    for vc in reversed(tab_range):
        n = math.floor(1000 * vc / (config["DIAM_FRAISE"] * math.pi))
        vf = math.floor(config["NB_DENTS"] * config["FZ"] * n)
        dist = math.floor(vf / 60 * config["TEMPS_MESURE"])
        parameters.append({"Vc": vc, "n": n, "Vf": vf, "dist": dist})
    return parameters

def write_headers(config, file, parameters, operation):
    file.writelines(";*******************\n")
    file.writelines(";  OPERATION : {}\n".format(operation))
    file.writelines("\n;   CONFIG: \n")
    for item in config:
        file.writelines(";      {} = {}\n".format(item, config[item]))
    file.writelines("\n;    PARAMETERS: \n")
    for meas in parameters:
        file.writelines(";      {}\n".format(meas))
    file.writelines(";*******************\n\n")


def pol2cart(r, theta, nb_dec=10):
    x = round(r * math.cos(math.radians(theta)), nb_dec)
    y = round(r * math.sin(math.radians(theta)), nb_dec)
    return x, y

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

if __name__ == "__main__":
    main()