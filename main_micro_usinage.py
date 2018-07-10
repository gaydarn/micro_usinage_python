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

    config = file_manager.load_config('config.json')
    config_file_manager = file_manager.load_config('config_file_manager.json')

    file_manager.create_folder_structure(config_file_manager)

    fichier_config = os.path.join(file_manager.CONFIGDIRPATH, "config.json")
    fichier_config_file_manager = os.path.join(file_manager.CONFIGDIRPATH, 'config_file_manager.json')

    file_manager.store_config(config, fichier_config)
    file_manager.store_config(config_file_manager, fichier_config_file_manager)

    # Calcul des paramètres d'usinage
    parameters = compute_parameters(config)
    fichier_parameters = os.path.join(file_manager.CONFIGDIRPATH, "parameters.json")
    file_manager.store_config(parameters, fichier_parameters)

    # Création du programme de surfaçage
    progname_surface_milling = os.path.join(file_manager.PRGDIRPATH, "sub_spirale_surface_milling.nc")
    create_prog_surface_milling(config, parameters, progname_surface_milling)

    # Création du programme de mesure
    progname_spirale_measurement = os.path.join(file_manager.PRGDIRPATH, "sub_spirale_measurements.nc")
    create_prog_spirale_measurements(config, parameters, progname_spirale_measurement)

    programe_COM = os.path.join(file_manager.PRGDIRPATH, "programe_COM.nc")
    create_contact_outil_matière(programe_COM)

    # Création du fichier config usinage
    fichier_config_usinage = os.path.join(file_manager.CONFIGDIRPATH, "config.json")
    file_manager.store_config(config, fichier_config_usinage)

    # Création du fichier config manager
    fichier_config_manager = os.path.join(file_manager.CONFIGDIRPATH, "config_file_manager.json")
    file_manager.store_config(config_file_manager, fichier_config_manager)

    progname_main = os.path.join(file_manager.PRGDIRPATH, "main.nc")
    create_prog_main(config, progname_main, progname_surface_milling, progname_spirale_measurement, programe_COM)





def create_prog_main(config, progname_main, progname_surface_milling, progname_spirale_measurement, programe_COM):
    # Création du fichier et écriture des entètes
    file = open(progname_main, "w")
    file.writelines(";**********************\n")
    file.writelines(";PROGRAMME PRINCIPAL\n")
    file.writelines(";**********************\n\n")
    # Début du programme (statique)
    # file.writelines("T1 \n") si la machine n'a pas de changeur d'outil
    file.writelines("T1 M6\n")
    file.writelines("G53 G01 B0 C0 F1000\n")
    file.writelines("G54\n")
    file.writelines("G01 Z20\n")
    file.writelines("L {}\n".format(path_leaf(programe_COM)))
    file.writelines("M1\n")
    file.writelines("#TRAFO ON\n")
    file.writelines("L {}\n".format(path_leaf(progname_surface_milling)))
    file.writelines("G102 Z1\n")
    file.writelines("M9\n")
    file.writelines("T2 M6\n")
    file.writelines("L {}\n".format(path_leaf(programe_COM)))
    file.writelines("M1\n")
    file.writelines("#TRAFO ON\n")
    file.writelines("L {}\n".format(path_leaf(progname_spirale_measurement)))
    file.writelines("M05\n")
    # file.writelines("T0\n") si la machine n'a pas de changeur d'outil
    file.writelines("T0 M6\n")
    file.writelines("M9\n")
    file.writelines("M30\n")

# création d'une fonction contact outil matière
def create_contact_outil_matière (program_COM):
    # Création du fichier et écriture des entètes
    file = open(program_COM, "w")
    file.writelines(";**********************\n")
    file.writelines(";Contact outil-matière\n")
    file.writelines(";**********************\n\n")
    file.writelines("M3 S60000\n")
    file.writelines("#TRAFO ON\n")
    file.writelines("G01 X3 Y0 F1000\n")
    file.writelines("G01 Z2.5\n")
    file.writelines("M1\n")
    file.writelines("M100=24\n")
    file.writelines("G100 Z-0.01\n")
    file.writelines("M101=[V.A.MOFFS.Z*10000]\n")
    file.writelines("G101 Z1\n")
    file.writelines("G01 Z5 F1000\n")
    file.writelines("G00 Z10\n")
    file.writelines("M17\n")
    file.writelines(";fin du contact outil matière\n")

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
    file.writelines(config["LUBRIFICATION"]+"\n")
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
    # file.writelines("T1 \n") si la machine n'a pas de changeur d'outil
    file.writelines("G90\n")
    file.writelines("# HSC[OPMODE 2 CONTERROR 0.02]\n")
    file.writelines("# HSC ON\n")
    file.writelines("M03 S{}\n".format(n))
    file.writelines(config["LUBRIFICATION"] + "\n")
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

    ae = config["AE"][0]
    fz = config["FZ"][0]
    ap = config["AP"]

    for vc in config["VC"]:

        n = math.floor(1000 * vc / (config["DIAM_FRAISE"] * math.pi))
        vf = math.floor(config["NB_DENTS"] * fz * n)
        dist = math.floor(vf / 60 * config["TEMPS_MESURE"])

        parameters.append({"mode": "VC",
                           "val": vc,
                           "n": n,
                           "Vf": vf,
                           "ae": ae,
                           "ap": ap,
                           "fz": fz,
                           "dist": dist})
    return parameters


    # Paramètre de AE
def compute_parameters_AE(config):
    parameters = []

    n = config["N"]
    dF = config["DIAM_FRAISE"]
    ap = config["AP"]

    for ae in config["AE"]:

        fz = config["H"] / (2 * math.sqrt(-(ae * (ae - dF) / math.pow(dF, 2))))
        vf = math.floor(config["NB_DENTS"] * fz * n)
        dist = math.floor(vf / 60 * config["TEMPS_MESURE"])

        parameters.append({     "mode": "AE",
                                "val": ae,
                                "n": n,
                                "Vf": vf,
                                "ae": ae,
                                "ap": ap,
                                "fz" : fz,
                                "dist": dist})
    return parameters


    # Paramètre de FZ
def compute_parameters_FZ(config):
    parameters = []

    n = config["N"]
    ap = config["AP"]
    ae = config["AE"][0]

    for fz in config["FZ"]:

        vf = math.floor(config["NB_DENTS"] * fz * n)
        dist = math.floor(vf / 60 * config["TEMPS_MESURE"])

        parameters.append({     "mode": "FZ",
                                "val": fz,
                                "n": n,
                                "Vf": vf,
                                "ae": ae,
                                "ap": ap,
                                "fz": fz,
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


    #Vc liste : 565, 550, 525, 500, 475, 450, 425, 400, 375, 350, 325, 300, 275, 250, 225, 200, 175, 150, 125, 100, 75, 50
    #Fz liste : 0.1, 0.095, 0.09, 0.085, 0.08, 0.075, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01
    #Ae liste : 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3