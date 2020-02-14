import numpy as np

"""
X is the input data of type np.array of dimensions (nbr of years, nbr of activities + 1), where the data for one year , i.e. 1 input,
represents the number of points we want to give for each activity. The + 1 accounts for the bias ! So the data given as
input should already have been expanded with this 1 for the bias !
Y is the output vector of shape (nbr of years, nbr of activities) representing the predicted percentage of presence for
each of the activities.
"""


def linear_kernel(xi, xj):
    """
    Computes the linear kernel function, i.e. produces a linear ridge regression
    :param xi: np.array (nbr of activities + 1, ) : First input
    :param xj: np.array (nbr of activities + 1, ) : Second input
    :return:
    """
    return xi @ xj


def polynomial_kernel(xi, xj, d=2):
    """
    Computes the kernel polynomial function
    :param xi: np.array (nbr of activities + 1, ) : First input
    :param xj: np.array (nbr of activities + 1, ) : Second input
    :param d: the degree of the polynomial, by default 2
    :return:
    """
    return (xi @ xj + 1)**d


def rbf_kernel(xi, xj, sigma):
    """
    Computes the kernel RBF (Gaussian) function
    :param xi: np.array (nbr of activities + mandatory_list size + 1, ) : First input
    :param xj: np.array (nbr of activities + mandatory_list size + 1, ) : Second input
    :param sigma: the sigma parameter, smaller implies sharper function
    :return:
    """
    return np.exp( - ( 1. / (2. * sigma**2)) * ((xi - xj)**2).sum())


def matrix_kernel(X, kernel_function, *kernel_args):
    """
    Computes the kernel matrix K, where K[i,j] corresponds to kernel_function(xi, xj)
    :param X: np.array (nbr of years, nbr of activities + 1) : the input data
    :param kernel_function: the kernel function
    :param kernel_args: the arguments for the kernel function if needed
    :return:
    """
    nbr_years, nbr_activ = X.shape

    K = np.zeros((nbr_years, nbr_years))
    for i in range(nbr_years):
        for j in range(nbr_years):
            K[i,j] = kernel_function(X[i], X[j], *kernel_args)
    #The kernel matrix must be symmetric
    assert np.allclose(K, K.T)

    return K


def prediction_matrix(Y, K, lambd=0):
    """
    Computes the matrix Y^T (K + lambda * Id)^(-1) used for the prediction
    :param Y: np.array (nbr of years, nbr of activities) : the ground truth outputs of the training data
    :param K: np.array (nbr of years, nbr of years) : the kernel matrix
    :param lambd: the regularizer influence, default to 0, i.e. no regularization
    :return:
    """
    return Y.T @ np.linalg.inv(K + lambd * np.eye(Y.shape[0]))


def prediction_vector(X, x, kernel_function, *kernel_args):
    """
    Computes k(X, x), i.e. the kernel function between the training data and the input sample
    :param X: np.array (nbr of years, nbr of activities + 1) : the input data
    :param x: np.array (nbr of activities, ) : the input sample
    :param kernel_function: the kernel function
    :param kernel_args: the arguments for the kernel function if needed
    :return: np.array (nbr of years, 1)
    """
    nbr_years = X.shape[0]

    kXx = np.zeros((nbr_years, 1))
    for i in range(nbr_years):
        kXx[i, 0] = kernel_function(X[i], x, *kernel_args)
    return kXx


def predict_KRR(X, x, Y, lambd, kernel_function, *kernel_args, pred_matrix=None):
    """
    Computes the prediction for the sample x by using the kernel ridge regression with multiple outputs
    :param X: np.array (nbr of years, nbr of activities + 1) : the input data
    :param x: np.array (nbr of activities, ) : the input sample
    :param Y: np.array (nbr of years, nbr of activities) : the ground truth outputs of the training data
    :param lambd: the regularizer influence
    :param kernel_function: the kernel function
    :param kernel_args: the arguments for the kernel function if needed
    :param pred_matrix: the prediction matrix, if None (default) it is computed
    :return: np.array (nbr of activities, 1)
    """
    if pred_matrix is None:
        K = matrix_kernel(X, kernel_function, *kernel_args)
        pred_matrix = prediction_matrix(Y, K, lambd)
    return pred_matrix @ prediction_vector(X, x, kernel_function,*kernel_args)