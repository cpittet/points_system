import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.backends.backend_pdf

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

def create_graphs(data, mandatory_list, last_year, names_list, society_size, category):
    """
    Creates the graphs for each activity with the past years only for the specified category
    (the data must corresponds to only that category)
    :param data: np.array (nbr of years x nbr of activity) : the data to plot, containing the past years
    :param mandatory_list: the list of the activities that are mandatory or not
    (work by the index of the activity)
    :param last_year: the last year of the data
    :param names_list: the names of the activities
    :param society_size: the current size of the society
    :param category: present, excused or non present
    :return: a plot of each activity with the last years
    """
    nbr_activ = data.shape[1]

    fig = plt.figure()

    #Adjust the spacing between the plots
    fig.subplots_adjust(hspace=2.00, wspace=0.5)

    years = mdates.YearLocator()

    #Compute number of columns and rows in the subplots
    cols = 2
    rows = np.ceil(nbr_activ / cols)

    #Iterate over each activity
    for i in range(nbr_activ):
        ax = plt.subplot(rows, cols, i + 1)

        #Choose the color according if the activity is mandatory or not :
        #Red for mandatory, blue for non mandatory
        if mandatory_list[0,i]:
            color = 'r'
        else:
            color = 'b'

        plt.plot(np.arange(last_year - data.shape[0] + 1, last_year + 1), data[:,i], marker='.', color=color, linestyle='-')

        #Fix the same limits for all subplots
        plt.xlim(last_year - data.shape[0], last_year + 1)
        plt.ylim(0, society_size)

        #Format the ticks
        ax.xaxis.set_major_locator(years)
        ax.grid(True)

        #Title for the subplot
        plt.title(names_list[0,i], loc='center', fontsize=12, color=color)

        #Annotate with the values
        for x, y in zip(np.arange(last_year - data.shape[0] + 1, last_year + 1), data[:,i]):
            label = "{:d}".format(int(y))

            plt.annotate(label, (x,y), textcoords='offset points', xytext=(0, 6), ha='center')

    #General title
    plt.suptitle("Evolution du nombre de personnes " + str(category) + " pour chaque activités\n(activités obligatoires en rouge)",
                 fontsize=16, color='black')

    #Axis title
    plt.text(0.5, 0.02, 'Années', ha='center', va='center')
    plt.text(0.06, 0.5, "Personnes " + str(category), ha='center', va='center', rotation='vertical')

    plt.show()
    return

def create_pdf():
    return

#lymdt, lmdt, names = fm.get_last_mandatory_and_names_from_db('/home/cpittet/jeunesse_app/data/dataApp.db')
#lycumul, lecumul = fm.get_last_cumulative('/home/cpittet/jeunesse_app/data/dataApp.db')

#create_graphs(lecumul[:,:22], lmdt, lymdt, names, 80, "présentes")