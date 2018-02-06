import os
import matplotlib.pyplot as plt
import json
import datetime
import time

######################################################

def save(path, directory, ext = 'png', close = True, verbose = True):
    """Save a figure from pyplot.

    Parameters:
    -----------
    path: string
        The path(and filename, without the extension) to save the figure to

    ext: string (default = 'png')
        The file extension. This must be supported by the active matplotlib
        backend (see matplotlib.backends module). Most backends support
        'png', 'pdf', 'ps', 'eps' and 'svg'.

    close: boolean (default = True)
        Whether to close the figure after saving. If you want to save the
        figure multiple times (e.g., to multiple format), you should NOT
        close it in between saves or you will have to re-plot it.

    verbose: boolean (default = True)
        Whether to print information about when and where the image has been
        saved.
        """
    # Extract the directory and filename from the given path
    # timestr = time.strftime("%m_%d")
    # directory = 'Data_' + timestr +'/'
    filename = "%s.%s" % (os.path.split(path)[1], ext)
    if directory == '':
        directory = '.'

    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # The final path to save to
    savepath = os.path.join(directory, filename)

    if verbose:
        print ("Saving figure to '%s'..." % savepath)

    # Actually save the figure
    plt.savefig(savepath)

    # Close it
    if close:
        plt.close()

    if verbose:
        print ("Done")

######################################################

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


######################################################

def savejson(data, path, directory, ext = 'json', verbose = False):
    """ Save data to json for analysis. """
    # timestr = time.strftime("%m_%d")
    # directory = 'Data_' + timestr +'/'
    filename = "%s.%s" % (os.path.split(path)[1], ext)
    if directory == '':
        directory = '.'

    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # The final path to save to
    savepath = os.path.join(directory, filename)

    if verbose:
        print ("Saving data to '%s'..." % savepath)

    # Save data to json

    jsondata = json.dumps(data)
    fd = open(savepath, 'w')
    fd.write(jsondata)
    fd.close()

    if verbose:
        print ("Done")
