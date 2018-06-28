import pandas
import matplotlib.pyplot as plt
import numpy as np
import glob
from numpy import array
import math
import json

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
          'tab:olive', 'tab:cyan']

def load_config(filename):
    infile = open(filename)
    config = json.load(infile)
    infile.close()
    return config


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


def compute_mean_value(file_data, plot=False, verbose=False):
    # N1    lecture fichier csv avec 3 colonnes : dates et heure          Time            Value
    sig = file_data  # pandas.read_csv("N3.csv", sep=';')
    # dérivée
    x = sig["Time"]
    y = sig["Value"]
    # x = list_1[1]["Time"]
    # y = Courant_usinage
    dy = np.zeros(y.shape, np.float)
    dy[0: -1] = np.fabs(np.diff(y) / np.diff(x))
    # dy[-1] = (y[-1] - y[-2])/(x[-1] - x[-2])
    # détection des deux maximum de la dérivée
    ix1 = 0
    ix2 = 0
    ixf = 0
    with_window = 100
    threshold_front = 7
    threshold_stab = 5
    threshold_instab = 5
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
                ix2 = _ix-50
    mean = 0
    if state == "FOUND" or state == "SEARCH_INSTAB":
        mean = np.mean(y[ix1:ix2])
        if verbose:
            print("measurement done, mean value is {}".format(mean))
    else:
        print("ERROR: Unable to found the mean value!")

    if plot:
        plt.plot(x, y)
        plt.ylabel('Courant [mA]')
        plt.xlabel('Temps [ms]')
        plt.plot(x, dy)
        plt.scatter(x[ixf], y[ixf], s=100, c="y")
        plt.scatter(x[ix1], y[ix1], s=100, c="g")
        plt.scatter(x[ix2], y[ix2], s=100, c="r")
        mean_x = [x[ix1], x[ix2]]
        mean_y = [mean, mean]
        plt.plot(mean_x, mean_y, c="k")
        plt.show()

    return mean


def plot_files_data(_files_data_empty, _files_data_milling):
    for _ix, file in enumerate(files_data_vide):
        plt.plot(files_data_vide[_ix]["Time"], files_data_vide[_ix]["Value"], c=colors[_ix % len(colors)])
        plt.plot(files_data_usinage[_ix]["Time"], files_data_usinage[_ix]["Value"], c=colors[_ix % len(colors)])
        plt.ylabel('Courant [mA]')
        plt.xlabel('Temps [ms]')
    plt.show()


def derivative_and_plot(x, y):
    dy = np.zeros(y.shape, np.float)
    dy[0: -1] = (np.diff(y) / np.diff(x))
    dy[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])

    fig, ax1 = plt.subplots()
    ax1.plot(x, y, c=colors[0])
    ax1.set_ylabel('Courant [mA]')
    ax1.set_xlabel('Vc [m/min]')
    ax2 = ax1.twinx()
    ax2.plot(x, dy, c=colors[1])
    ax2.scatter(x, dy, c=colors[1])
    ax1.set_ylabel('Courant derivé')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()

    # Chargement du fichier de configuration
    config = load_config('config.json')


if __name__ == "__main__":

    files_selection = []  # ['N1', 'N3', 'N5', 'N7', 'N9', 'N11', 'N13', 'N15', 'N17', 'N19', 'N21']
    files_data_vide = get_files_data(r'.\Mesure\VC Vide', files_selection)
    files_data_usinage = get_files_data(r'.\Mesure\VC Usinage', files_selection)
    plot_files_data(files_data_vide, files_data_usinage)

    #   Graphique de chaque courbe : si oui : TRUE  si non : FALSE

    plot_display = False
    print("")
    print("Moyenne usinage")
    mean_usinage = []
    # files selection = None, il y a une erreur pour la mesure de la moyenne
    for data in files_data_usinage:
        mean_usinage.append(compute_mean_value(data, plot=plot_display, verbose=True))
    print("")
    print("Moyenne vide")
    mean_vide = []
    for data in files_data_vide:
        mean_vide.append(compute_mean_value(data, plot=plot_display, verbose=True))

    # TODO: Get info from config file saved with the measurement
    Vc_list = config["VC"]
    ae = 0.05
    ap = 1.5
    R = 0.9
    d = 2.6
    fz = 0.07
    z = 3

    n = 0
    for ix, Vc in enumerate(Vc_list):
        n = (Vc * 1000) / (np.pi * d)
    Vf = fz * n * z
    f = Vf / n

    print("")
    print("test de graphique")

    courant_util = []
    courant_section = []
    ec = []

    # TODO: modifier les graphiques

    for ix, Vc in enumerate(Vc_list):
        courant_util.append((mean_usinage[ix] - mean_vide[ix]))
        courant_section.append(courant_util[ix] / (ae * ap))
        ec.append((60 * R * math.pow((courant_util[ix]), 2)) / (Vc * ap * f))

    derivative_and_plot(array(Vc_list), array(courant_util))

    derivative_and_plot(array(Vc_list), array(courant_section))

    derivative_and_plot(array(Vc_list), array(ec))


