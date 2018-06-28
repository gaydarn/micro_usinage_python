#!/usr/bin/env python3

import matplotlib.pyplot as plt
import json
import ntpath
import file_manager
import math
import os

colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

def main():

    # Chargement du fichier de configuration
    config = load_config('config.json')

    print(file_manager.DATADIRPATH)
    file_manager.create_folder_structure(file_manager.config_file_manager)
    print(file_manager.DATADIRPATH)

    # Calcul des paramètres d'usinage
    parameters = compute_parameters(config)

    # Création du programme de surfaçage
    progname_surface_milling = os.path.join(file_manager.PRGDIRPATH, "sub_spirale_surface_milling.nc")
    create_prog_surface_milling(config, parameters, progname_surface_milling)

    # Création du programme de mesure
    progname_spirale_measurement = os.path.join(file_manager.PRGDIRPATH, "sub_spirale_measurements.nc")
    create_prog_spirale_measurements(config, parameters, progname_spirale_measurement)

    # Création du fichier config usinage
    fichier_config_usinage = os.path.join(file_manager.CONFIGDIRPATH, "config.json")

    # Création du fichier config manager
    fichier_config_manager = os.path.join(file_manager.CONFIGDIRPATH, "config_file_manager.json")


    progname_main = os.path.join(file_manager.PRGDIRPATH, "main.nc")
    create_prog_main(config, progname_main, progname_surface_milling, progname_spirale_measurement)

def create_prog_main(config, progname_main, progname_surface_milling, progname_spirale_measurement):
    # Création du fichier et écriture des entètes
    file = open(progname_main, "w")
    file.writelines(";**********************\n")
    file.writelines(";PROGRAMME PRINCIPAL\n")
    file.writelines(";**********************\n\n")
    # Début du programme (statique)
    file.writelines("T1 \n")
    #file.writelines("T1 M6\n") pour changement de broche
    file.writelines("G53 G01 B0 C0 F100\n")
    file.writelines("G55\n")
    file.writelines("L {}\n".format(path_leaf(progname_surface_milling)))
    file.writelines("L {}\n".format(path_leaf(progname_spirale_measurement)))
    file.writelines("M05\n")
    file.writelines("T0\n")
    # file.writelines("T0 M6\n")  pour changement de broche
    file.writelines("M30\n")

def create_prog_surface_milling(config, parameters, filename):

    # Condition initiales
    r = config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"] / 2 + config["SURPLUS_PREM_PASSE"]
    theta = 0
    vf = config["SURFACE_VF"]
    x_list = []
    y_list = []
    # Création du fichier et écriture des entètes
    file = open(filename, "w")
    write_headers(config, file, parameters, "SURFACAGE")
    # Début du programme (statique)
    file.writelines("G90\n")
    file.writelines("# HSC[OPMODE 2 CONTERROR 0.02]\n")
    file.writelines("# HSC ON\n")
    file.writelines("M03 S{}\n".format(config["SURFACE_N"]))
    file.writelines("G0 Z10\n")
    file.writelines("G0 X{} Y0\n".format(config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"]))  # 1/2 largeur de fraise de marge
    file.writelines("G1 Z{} F1000\n".format(config["SURFACE_PROF_PASSE"]))

    while r > (config["DIAM_FRAISE"] / 2) - 0.05:

        # Calcul de coordonées cartésiennes
        x, y = pol2cart(r, theta, config["NB_DECIMALES"])
        x_list.append(x)
        y_list.append(y)
        # Calcul des prochaines coordonées polaires
        theta += config["ANGLE_CHANGE_DIAM"]
        r -= config["SURFACE_LARG_PASSE"] / (360 / math.fabs(config["ANGLE_CHANGE_DIAM"]))

        # Log pour la génération du programme
        file.writelines("G1 X{} Y{} Z{} F{}\n".format(x, y, config["SURFACE_PROF_PASSE"], vf))

    file.writelines("G1 Z20\n")
    file.writelines("G0 X0 Y15\n")
    file.writelines("# HSC OFF\n")
    file.writelines("M17\n")
    file.close()
    ax = plt.subplot(111)
    plt.title("Surface milling")
    ax.plot(x_list, y_list, 'g-')
    max_dist = (config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"] / 2) * 1.2
    plt.xlim(-max_dist, max_dist)
    plt.ylim(-max_dist, max_dist)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
# Fin du programme de surfaçage


# Début du programme mesure
def create_prog_spirale_measurements(config, parameters, filename):

    # Condition initiales
    r = config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"] / 2 + config["SURPLUS_PREM_PASSE"]
    r_old = r
    theta = 0
    theta_old = theta
    dist_tot = 0
    #index_param = 0
    index_param = -1
    x_list = []
    x_list_tmp = []
    y_list = []
    y_list_tmp = []
    flag_measurement_complete = False
    vf, ae, ap, n, dist = maj_param_usinage(parameters[index_param+1])
    vf = config["SURFACE_VF"]
    n = config["SURFACE_N"]
    ae = config["SURFACE_LARG_PASSE"]

    #première distance pour ajouter les tours de réserve
    target_dist = config["NB_TOURS_RESERVE"] * math.pi * config["DIAM_PIECE"]
    # Création du fichier et écriture des entètes
    file = open(filename, "w")
    write_headers(config, file, parameters, "SPIRALE DE MESURE")
    # Début du programme (statique)
    file.writelines("T1 \n")
    #file.writelines("T1 M6\n") pour changement de broche
    file.writelines("G90\n")
    file.writelines("# HSC[OPMODE 2 CONTERROR 0.02]\n")
    file.writelines("# HSC ON\n")
    file.writelines("M03 S{}\n".format(n))
    file.writelines("G0 Z10\n")
    file.writelines("G0 X{} Y0\n".format(config["DIAM_PIECE"] / 2 + config["DIAM_FRAISE"]))  # 1/2 largeur de fraise de marge
    file.writelines("G1 Z{} F1000\n".format(ap))
    file.writelines("\n;OP: {}:\n".format(str(parameters[index_param])))

    while r > (config["DIAM_FRAISE"] / 2) - 0.05:

        # Calcul de coordonées cartésiennes
        x, y = pol2cart(r, theta, config["NB_DECIMALES"])

        # Calcul de la distance parcourue
        dist_tot += r_old * math.radians(math.fabs(theta - theta_old))
        # Sauvegarde des valeurs pour les calculs à la boucle suivante
        r_old = r
        theta_old = theta
        # Calcul des prochaines coordonées polaires
        theta += config["ANGLE_CHANGE_DIAM"]
        r -= ae / (360 / math.fabs(config["ANGLE_CHANGE_DIAM"]))

        # Log pour la génération du programme et l'affichage
        file.writelines("G1 X{} Y{} Z{} F{}\n".format(x, y, ap, vf))

        if not flag_measurement_complete:
            # Log pour l'affichage
            x_list_tmp.append(x)
            y_list_tmp.append(y)

            # Passage à la vitesse suivante si la distance cible est atteinte
            if dist_tot >= target_dist and not index_param >= len(parameters):
                x_list.append(x_list_tmp.copy())
                x_list_tmp.clear()
                y_list.append(y_list_tmp.copy())
                y_list_tmp.clear()
                index_param += 1
                # Contrôle si la mesure est terminée
                if index_param >= len(parameters):
                    file.writelines("N{}:\n".format(index_param * 2))
                    file.writelines(";End of measurement, now we do a surface milling to prepare for the next measure!\n\n")
                    vf = config["SURFACE_VF"]
                    file.writelines("M03 S{}\n".format(config["SURFACE_N"]))
                    flag_measurement_complete = True
                else:
                    vf, ae, ap, n, dist = maj_param_usinage(parameters[index_param])
                    #vf = parameters[index_param]["Vf"]
                    #ae = parameters[index_param]["ae"]
                    target_dist += dist
                    file.writelines("N{}:\n".format((index_param)*2))
                    file.writelines("M03 S{}\n".format(n))
                    file.writelines("\nN{}:\n".format(((index_param) * 2) + 1))
                    file.writelines(";OP: {}:\n".format(str(parameters[index_param])))


    msg = "Error!"
    dist_tot = round(dist_tot, 2)
    if flag_measurement_complete:
        msg = "Measurement have been programmed without issue, with a total milling distance of {}".format(dist_tot)
    else:
        msg = "The maximum milling distance of {} is not enough to make all the measurement!".format(dist_tot)
    file.writelines("\n;{}\n\n".format(str(msg)))
    print(msg)
    
    file.writelines("G1 Z20\n")
    file.writelines("G0 X0 Y15\n")
    file.writelines("# HSC OFF\n")
    file.writelines("M17\n")
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

def maj_param_usinage(parameter):
    vf = parameter["Vf"]
    ae = parameter["ae"]
    ap = parameter["ap"]
    n = parameter["n"]
    dist = math.ceil(parameter["dist"])

    return vf, ae, ap, n, dist


def load_config(filename):
    infile = open('config.json')
    config = json.load(infile)
    infile.close()
    return config

    # Choix d'un des trois paramètres
def compute_parameters(config):
   if "VC" in config["MODE"]:
       return compute_parameters_VC(config)
   elif "AE" in config["MODE"]:
       return compute_parameters_AE(config)
   elif "FZ" in config["MODE"]:
       return compute_parameters_FZ(config)


    # Paramètre de Vc
def compute_parameters_VC(config):
    parameters = []

    for vc in config["VC"]:
        ae = config["AE"][0]
        fz = config["FZ"][0]
        n = math.floor(1000 * vc / (config["DIAM_FRAISE"] * math.pi))
        vf = math.floor(config["NB_DENTS"] * fz * n)
        dist = math.floor(vf / 60 * config["TEMPS_MESURE"])
        ap = config["AP"]

        parameters.append({"mode": "VC",
                           "val": vc,
                           "n": n,
                           "Vf": vf,
                           "ae": ae,
                           "ap": ap,
                           "dist": dist})
    return parameters


    # Paramètre de AE
def compute_parameters_AE(config):
    parameters = []

    for ae in config["AE"]:
        n = config["N"]
        dF = config["DIAM_FRAISE"]
        fz = config["H"] / (2 * math.sqrt(-(ae * (ae - dF) / math.pow(dF, 2))))
        vf = math.floor(config["NB_DENTS"] * fz * n)
        dist = math.floor(vf / 60 * config["TEMPS_MESURE"])
        ap = config["AP"]

        parameters.append({     "mode": "AE",
                                "val": ae,
                                "n": n,
                                "Vf": vf,
                                "ae": ae,
                                "ap": ap,
                                "dist": dist})
    return parameters


    # Paramètre de FZ
def compute_parameters_FZ(config):
    parameters = []

    for fz in config["FZ"]:
        n = config["N"]
        vf = math.floor(config["NB_DENTS"] * fz * n)
        dist = math.floor(vf / 60 * config["TEMPS_MESURE"])
        ap = config["AP"]
        ae = config["AE"][0]

        parameters.append({     "mode": "AE",
                                "val": ae,
                                "n": n,
                                "Vf": vf,
                                "ae": ae,
                                "ap": ap,
                                "dist": dist})
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
