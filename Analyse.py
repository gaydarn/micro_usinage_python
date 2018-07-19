import pandas
import matplotlib.pyplot as plt
import numpy as np
import glob
from numpy import array
import math
import file_manager
import main_micro_usinage
import os
from tkinter import filedialog


# Pour enregister les plots
# plt.savefig('Subject1Phyla.eps', format='eps', dpi=1000)





colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
          'tab:olive', 'tab:cyan', ]



def get_files_data(path, file_selection=None):

    # path = r'.\Mesure\VC Vide'  # use your path
    all_files = glob.glob(path + "/*.csv")
    # frame = pandas.DataFrame()
    # file_selection = ['N1', 'N5', 'N17']
    _list = []
    if file_selection is None or not file_selection:
        for file_ in all_files:
            df = pandas.read_csv(file_, sep=';')
            _list.append(df)
    else:
        for file_ in all_files:
            mask = file_.split("_")[-1].split(".")[0]
            for sel in file_selection:
                if sel == mask:
                    df = pandas.read_csv(file_, sep=';')
                    _list.append(df)
                    break
    return _list


def compute_mean_value(file_data, plot=False, verbose=False, title="default"):
    # N1    lecture fichier csv avec 3 colonnes : dates et heure          Time            Value
    sig = file_data  # pandas.read_csv("N3.csv", sep=';')
    # dérivée
    x = sig["Time"]
    y = sig["Value"]
    # x = list_1[1]["Time"]
    # y = Courant_usinage
    dy = np.zeros(y.shape, np.float)
    dy[0: -1] = np.fabs(np.diff(y) / np.diff(x))
    # détection des deux maximum de la dérivée
    ix1 = 0
    ix2 = 0
    ixf = 0
    with_window = 100
    threshold_front = 7
    threshold_stab = 8
    threshold_instab = 8
    state = "SEARCH_STAB"
    for _ix, pt in enumerate(dy):
        if state == "SEARCH_FIRST_FRONT":
            if pt > threshold_front:
                if verbose:
                    print("First front found in x={}".format(_ix))
                ixf = _ix
                state = "SEARCH_STAB"

        if state == "SEARCH_STAB" and with_window < _ix < len(dy) - with_window:
            if np.mean(dy[_ix - with_window:_ix + with_window]) <= threshold_stab:
                if verbose:
                    print("stab found in x1={}".format(x[_ix]))
                ix1 = _ix
                state = "SEARCH_INSTAB"

        if state == "SEARCH_INSTAB" and with_window < _ix < len(dy) - with_window:
            if np.mean(dy[_ix - with_window:_ix + with_window]) > threshold_instab:
                if verbose:
                    print("instab found in x2={}".format(x[_ix]))
                ix2 = _ix
                state = "FOUND"
                break
            else:
                ix2 = _ix-80
    mean = 0
    if state == "FOUND" or state == "SEARCH_INSTAB":
        mean = np.mean(y[ix1:ix2])
        if verbose:
            print("measurement done, mean value is {}".format(mean))
    else:
        print("ERROR: Unable to found the mean value!")

    if plot:
        plt.plot(x, y, label='Courant mesuré')
        plt.ylabel('Courant [mA]')
        plt.xlabel('Temps [ms]')
        plt.plot(x, dy, label='Dérivée')
        plt.scatter(x[ixf], y[ixf], s=100, c="y")
        plt.scatter(x[ix1], y[ix1], s=100, c="g")
        plt.scatter(x[ix2], y[ix2], s=100, c="r")
        mean_x = [x[ix1], x[ix2]]
        mean_y = [mean, mean]
        plt.plot(mean_x, mean_y, label='Courant moyen', c="k")
        plt.title(title)
        plt.legend(loc="best")
        plt.show()

    return mean


def plot_files_data(_files_data_empty, _files_data_milling):
    legends = []
    for _ix, file in enumerate(files_data_vide):
        plt.plot(files_data_usinage[_ix]["Time"], files_data_usinage[_ix]["Value"], c=colors[_ix % len(colors)])
        legends.append("{}={}".format(parameters[_ix]["mode"], parameters[_ix]["val"]))
        plt.ylabel('Courant [mA]')
        plt.xlabel('Temps [ms]')
        plt.title(os.path.basename(file_manager.MAINDIRPATH))
    plt.legend(legends, loc='best')
    for _ix, file in enumerate(files_data_vide):
        plt.plot(files_data_vide[_ix]["Time"], files_data_vide[_ix]["Value"], c=colors[_ix % len(colors)])
    plt.show()

def plot_files_data_without_derivative(_files_data_empty, _files_data_milling):
    for _ix, file in enumerate(files_data_vide):
        plt.plot(files_data_vide[_ix]["Time"], files_data_vide[_ix]["Value"])
        plt.legend(loc="best")
        plt.plot(files_data_usinage[_ix]["Time"], files_data_usinage[_ix]["Value"])
        plt.ylabel('Courant [mA]')
        plt.xlabel('Temps [ms]')
        plt.title(os.path.basename(file_manager.MAINDIRPATH))
    plt.show()


def derivative_and_plot(x, y, ylabel1, xlabel, ylabel2, Title="default"):
    dy = np.zeros(y.shape, np.float)
    dy[0: -1] = (np.diff(y) / np.diff(x))
    dy[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])

    fig, ax1 = plt.subplots()
    ax1.plot(x, y, '-', label='Courant util', c=colors[0])
    ax1.set_ylabel(ylabel1)
    ax1.set_xlabel(xlabel)
    ax2 = ax1.twinx()
    ax2.plot(x, dy,'k--', label='Dérivée', c=colors[1])
    ax2.scatter(x, dy, c=colors[1])
    ax2.set_ylabel(ylabel2)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title(Title)
    ax1.legend(bbox_to_anchor=(1.01, -0.05), loc=3, ncol=2, mode="expand", borderaxespad=0)
    ax2.legend(bbox_to_anchor=(1.01, -0.10), loc=3, ncol=2, mode="expand", borderaxespad=0)
    plt.show()

    # Chargement du fichier de configuration
    config = file_manager.load_config('config.json')


if __name__ == "__main__":

    file_manager.get_folder_structure()
    files_selection = []
    files_data_vide = get_files_data(file_manager.EMPTYDATADIRPATH, files_selection)
    files_data_usinage = get_files_data(file_manager.MILLINGDATADIRPATH, files_selection)
    config = file_manager.load_config(os.path.join(file_manager.CONFIGDIRPATH, "config.json"))



    #TODO load parameters
    parameters = main_micro_usinage.compute_parameters(config)

    # plot pour comparaison des plusireur points de mesurre, pas utile pour les analyse
    #plot_files_data_without_derivative(files_data_vide, files_data_usinage)


    #graphique de les tous les courant
    plot_files_data(files_data_vide, files_data_usinage)



    #   Graphique de chaque courbe : si oui : TRUE  si non : FALSE
    ################################################
    plot_display = False
    ################################################



    print("")
    print("Moyenne usinage")
    mean_usinage = []
    # files selection = None, il y a une erreur pour la mesure de la moyenne
    for ix, data in enumerate(files_data_usinage):
        mean_usinage.append(compute_mean_value(data, plot=plot_display, verbose=True, title="Milling at  - {}={}".format(parameters[ix]["mode"], parameters[ix]["val"])))
    print("")
    print("Moyenne vide")
    mean_vide = []
    for ix, data in  enumerate(files_data_vide):
        mean_vide.append(compute_mean_value(data, plot=plot_display, verbose=True, title="Empty at - {}={}".format(parameters[ix]["mode"], parameters[ix]["val"])))


    if "VC" in config["MODE"]:
        #   mode VC
        Vc_list = config["VC"]
        Ae = config["AE"][0]
        Fz = config["FZ"][0]
        R = 0.9
        ap = np.abs(config["AP"])
        d = config["DIAM_FRAISE"]
        z = config["NB_DENTS"]

        # calcul pour la création des graphiques
        f = z * Fz
        courant_util = []
        ec = []


        Titre = os.path.basename(file_manager.MAINDIRPATH)
        for ix, Vc in enumerate(Vc_list):
                courant_util.append((mean_usinage[ix] - mean_vide[ix]))
                ec.append((60 * R * math.pow((courant_util[ix]/1000), 2))/(Vc_list[ix] * 1000 * ap * f))

        derivative_and_plot(array(Vc_list), array(courant_util),'Courant [mA]', 'Vc [m/min]', 'Dérivée', Titre)

        derivative_and_plot(array(Vc_list), array(ec),'énergie de coupe [J/mm^3]', 'Vc [m/min]', 'Dérivée', Titre)

    elif "FZ" in config["MODE"]:
        #   mode FZ
        Vc = 0
        Ae = config["AE"][0]
        Fz_list = config["FZ"]
        R = 0.9
        ap = np.abs(config["AP"])
        d = config["DIAM_FRAISE"]
        z = config["NB_DENTS"]
        n = config['N']

        # calcul pour la création des graphiques
        Vc = (n * np.pi * d) / 1000
        f = []
        h = []
        courant_util = []
        ec = []

        Titre = os.path.basename(file_manager.MAINDIRPATH)
        for ix, Fz in enumerate(Fz_list):
            f.append(Fz * z)
            h.append(2 * Fz * math.sqrt((Ae / d) * (1 - (Ae / d))))
            courant_util.append((mean_usinage[ix] - mean_vide[ix]))
            ec.append((60 * R * math.pow((courant_util[ix] / 1000), 2)) / (Vc * 1000 * ap * f[ix]))

        derivative_and_plot(array(h), array(courant_util), 'Courant [mA]', 'h [mm]', 'Dérivée', Titre)

        derivative_and_plot(array(h), array(ec), 'énergie de coupe [J/mm^3]', 'h [mm]', 'Dérivée', Titre)

    elif "AE" in config["MODE"]:
        #   mode AE
        Vc = 0
        Ae_list = config["AE"]
        Fz = 0
        R = 0.9
        ap = np.abs(config["AP"])
        d = config["DIAM_FRAISE"]
        z = config["NB_DENTS"]
        n = config['N']

        # calcul pour la création des graphiques
        Vc = (n * np.pi * d) / 1000
        tab_Fz = [data['fz'] for data in parameters]
        f = []

        Titre = os.path.basename(file_manager.MAINDIRPATH)
        for ix, Fz in enumerate(tab_Fz):
            f.append(Fz * z)
        courant_util = []
        ec = []
        for ix, Ae in enumerate(Ae_list):
            courant_util.append((mean_usinage[ix] - mean_vide[ix]))
            ec.append((60 * R * math.pow((courant_util[ix] / 1000), 2)) / (Vc * 1000 * ap * f[ix]))

        derivative_and_plot(array(Ae_list), array(courant_util), 'Courant [mA]', 'ae [mm]', 'Dérivée', Titre)

        derivative_and_plot(array(Ae_list), array(ec), 'énergie de coupe [J/mm^3]', 'ae [mm]', 'Dérivée', Titre)








