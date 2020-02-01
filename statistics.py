import numpy as np
import matplotlib.pyplot as plt


def average(data, society_size):
    """

    :param data: np.array : the data (number of people present
    at each activity) to average
    :param society_size: the current size of the society
    :return: the average (as percent) of the present people
    """
    return (1.0 / data.shape[0] * data.sum()) / society_size

def create_graphs(data, mandatory_list):
    """

    :param data: np.array (nbr of years x nbr of activity) : the data to plot
    :param mandatory_list: the list of the activities that are mandatory or not
    (work by the index of the activity)
    :return: a plot of each activity with the last years
    """
    return

def create_pdf():
    return