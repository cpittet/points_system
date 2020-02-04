import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import datetime

import file_manager as fm


def average(data, society_size):
    """
    Average the data
    :param data: np.array (nbr of activities x 1): the data (number of people of a category (present, excused, non present)
    at each activity) to average
    :param society_size: the current size of the society
    :return: the average (as percent)
    """
    return (1.0 / data.shape[0] * data.sum()) / society_size


def create_pdf(data, mandatory_list, last_year, names_list, society_size, path):
    """
    Creates a pdf with the evolution graphs for each activity and each category (present, excused, non present),
    add to this pdf:
        - the average (of the current year) of present people at mandatory activities
        - the average (of the current year) of excused people at mandatory activities
        - the average (of the current year) of non present people at mandatory activities
        - the average (of the current year) of present people at non mandatory activities
        - the average (of the current year) of excused people at non mandatory activities
        - the average (of the current year) of non present people overall
        - the average (of the current year) of excused people overall
        - the average (of the current year) of non present people overall
    :param data: np.array (nbr of years x 3*nbr of activities) : the full (three category) data
    :param mandatory_list: the list of the activities that are mandatory or not
    (work by the index of the activity)
    :param last_year: the last year of the data
    :param names_list: the names of the activities
    :param society_size: the current size of the society
    :param path: the location where to save the pdf (only folder path, the name of the file is automatic)
    :return:
    """
    #Number of activities
    nbr_activ = data.shape[1] // 3

    with PdfPages(str(path) + '/Jeunesse_statistiques_' + str(last_year) +'.pdf') as pdf:

        #Iterate over the categories
        categories = ["présentes", "excusées", "non excusées"]

        for cat in categories:

            #Set A4 portait (in inches...)
            fig = plt.figure(figsize=(11.93, 15.98))

            # Adjust the spacing between the plots
            fig.subplots_adjust(hspace=1.75, wspace=0.5)

            # Compute number of columns and rows in the subplots
            cols = 2
            rows = np.ceil(nbr_activ / cols)

            # General title
            plt.suptitle(
                "Evolution du nombre de personnes " + cat + " pour chaque activités\n(activités obligatoires en rouge)",
                fontsize=14, color='black', fontweight='bold')

            # Iterate over each activity
            for i in range(nbr_activ):
                ax = plt.subplot(rows, cols, i + 1)

                # Choose the color according if the activity is mandatory or not :
                # Red for mandatory, blue for non mandatory
                if mandatory_list[i]:
                    color = 'r'
                else:
                    color = 'b'

                plt.plot(np.arange(last_year - data.shape[0] + 1, last_year + 1, dtype=int), data[:, i], marker='.', color=color,
                         linestyle='-')

                # Fix the same limits for all subplots
                plt.xlim(last_year - data.shape[0], last_year + 1)
                plt.ylim(0, society_size)

                #Format the x ticks
                plt.xticks(np.arange(last_year - data.shape[0] + 1, last_year + 1, dtype=int))

                #Add a grid
                plt.grid(True, which='major', axis='y')

                # Title for the subplot
                plt.title(names_list[0, i], loc='center', fontsize=11, color=color)

                # Annotate with the values
                for x, y in zip(np.arange(last_year - data.shape[0] + 1, last_year + 1), data[:, i]):
                    label = "{:d}".format(int(y))

                    plt.annotate(label, (x, y), textcoords='offset points', xytext=(0, 6), ha='center')

            #Save figure to the pdf
            pdf.savefig()
            plt.close()

        #Add the averages

        mdt_list_index = np.argwhere(mandatory_list == True)

        mdt_data_present = data[-1, :nbr_activ][mdt_list_index]
        avg_mdt_present = average(mdt_data_present, society_size)

        mdt_data_excused = data[-1,nbr_activ:2*nbr_activ][mdt_list_index]
        avg_mdt_excused = average(mdt_data_excused, society_size)

        mdt_data_non_present = data[-1, 2 * nbr_activ:][mdt_list_index]
        avg_mdt_non_present = average(mdt_data_non_present, society_size)

        non_mdt_list_index = np.argwhere(mandatory_list == False)

        non_mdt_data_present = data[-1, :nbr_activ][non_mdt_list_index]
        avg_non_mdt_present = average(non_mdt_data_present, society_size)

        non_mdt_data_excused = data[-1, nbr_activ:2 * nbr_activ][non_mdt_list_index]
        avg_non_mdt_excused = average(non_mdt_data_excused, society_size)

        non_mdt_data_non_present = data[-1, 2 * nbr_activ:][non_mdt_list_index]
        avg_non_mdt_non_present = average(non_mdt_data_non_present, society_size)

        all_data_present = data[-1, :nbr_activ]
        avg_all_present = average(all_data_present, society_size)

        all_data_excused = data[-1, nbr_activ:2*nbr_activ]
        avg_all_excused = average(all_data_excused, society_size)

        all_data_non_present = data[-1, 2*nbr_activ:]
        avg_all_non_present = average(all_data_non_present, society_size)

        #Add the averages to the file
        fig = plt.figure(figsize=(11.93, 15.98))
        fig.text(0.10, 0.90, 'Activités obligatoires :', size=14, fontweight='bold')

        fig.text(0.10, 0.87, 'Moyenne des personnes présentes : ' + "{:.2f}".format(100 * avg_mdt_present) + '%, ' + str(int(np.around(avg_mdt_present * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.84, 'Moyenne des personnes excusées : ' + "{:.2f}".format(100 * avg_mdt_excused) + '%, ' + str(int(np.around(avg_mdt_excused * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.81, 'Moyenne des personnes non présentes : ' + "{:.2f}".format(100 * avg_mdt_non_present) + '%, ' + str(int(np.around(avg_mdt_non_present * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.70, 'Activités pas obligatoires :', size=14, fontweight='bold')

        fig.text(0.10, 0.67, 'Moyenne des personnes présentes : ' + "{:.2f}".format(100 * avg_non_mdt_present) + '%, ' + str(int(np.around(avg_non_mdt_present * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.64, 'Moyenne des personnes excusées : ' + "{:.2f}".format(100 * avg_non_mdt_excused) + '%, ' + str(int(np.around(avg_non_mdt_excused * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.61, 'Moyenne des personnes non présentes : ' + "{:.2f}".format(100 * avg_non_mdt_non_present) + '%, ' + str(
            int(np.around(avg_non_mdt_non_present * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.50, 'Toutes les activités :', size=14, fontweight='bold')

        fig.text(0.10, 0.47, 'Moyenne des personnes présentes : ' + "{:.2f}".format(100 * avg_all_present) + '%, ' + str(
            int(np.around(avg_all_present * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.44, 'Moyenne des personnes excusées : ' + "{:.2f}".format(100 * avg_all_excused) + '%, ' + str(
            int(np.around(avg_all_excused * society_size))) + ' personnes', size=11)

        fig.text(0.10, 0.41, 'Moyenne des personnes non présentes : ' + "{:.2f}".format(100 * avg_all_non_present) + '%, ' + str(
            int(np.around(avg_all_non_present * society_size))) + ' personnes', size=11)

        pdf.savefig()
        plt.close()

        #Set the file's metadata
        d = pdf.infodict()
        d['Subject'] = 'Evolution des présences - Jeunesse Marsens'


#lymdt, lmdt, names = fm.get_last_mandatory_and_names_from_db('/home/cpittet/jeunesse_app/data/dataApp.db')
#lycumul, lecumul = fm.get_last_cumulative('/home/cpittet/jeunesse_app/data/dataApp.db')

#create_pdf(lecumul, lmdt, lymdt, names, 100, '/home/cpittet/jeunesse_app')