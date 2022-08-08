__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2016, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

import wx
import inspect
import pickle

# From http://code.activestate.com/recipes/410692/
# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

# # EXAMPLE:
# # The following example is pretty much the exact use-case of a dictionary,
# # but is included for its simplicity. Note that you can include statements
# # in each suite.
# v = 'ten'
# for case in switch(v):
#     if case('one'):
#         print 1
#         break
#     if case('two'):
#         print 2
#         break
#     if case('ten'):
#         print 10
#         break
#     if case('eleven', 'twelve'):
#         print '11 or 12'
#         break
#     if case(): # default, could also just omit condition or 'if True'
#         print "something else!"
#         # No need to break here, it'll stop anyway

def ReportError(ErrorString):
    ''' ReportError(ErrorString): For generic reporting.  This produces a print to the console and a
    MessageBox (wxPython).
    '''

    # Get information about the caller.
    #Frame, FileName, Line, FunctionName, Lines, Index = inspect.getouterframes(inspect.currentframe())[1]

    # Get all the frames.  Because this can be called in a debugger, we may not actually be at the top of the stack.
    Frames = inspect.getouterframes(inspect.currentframe())

    # Loop through the frames until we get to MyPython.py.  That's us.
    for idx, frame in enumerate(Frames):
        if 'MyPython.py' in frame[1]:
            break;

    # Get the frame just above us.  That's our caller.
    idx +=1
    Frame, FileName, Line, FunctionName, Lines, Index = Frames[idx]

    # Print the caller's communication alongside the stack information.
    ReportStr = '%s\n\nFile:%s \nFunction: %s\nLine: %d\n\nPlease report to zackg@berkeley.edu' % (ErrorString, FileName, FunctionName, Line)

    print(ReportStr)

    wx.MessageBox(ReportStr, "Error", style=wx.OK)

    return


def GetSelectedItemsFromListCtrl(ListCtrl):
    """ GetSelectedItemsFromListCtrl(ListCtrl): Produces a list of only the selected items from a wxListCtrl.

    :param ListCtrl: A multiselect ListCtrl

    returns: List of strings: Text of selected item
    """

    # List of strings that the user clicked on.
    Strings = []
    #Start with item -1 means we get the first one.
    item = -1

    # Loop until GetNextSelected returns -1 which means no more items.
    while True:
        item = ListCtrl.GetNextSelected(item)

        # Got all selected items.
        if item == -1:
            break

        # Build our list of strings.
        Strings.append(ListCtrl.GetItemText(item))

    # If there aren't any selected items, then say so to the caller.
    if len(Strings) == 0:
        return None

    # Return the list.
    return Strings

def PickleVar(VarName, VarValue=None, DefaultValue=None):
    """ If a user supplies a VarValue, then he is writing it.  Otherwise, he is reading it.
    """

    # If VarValue exists, that means the user wants to write the value.
    if VarValue is not None:
        pickle.dump(VarValue, open(VarName.lower() + '.pickle', 'wb'))
        return

    # No VarValue means the user wants to read it.
    try:
        # Check for a pickle file.
        VarOut = pickle.load(open(VarName.lower() + '.pickle', 'rb'))
        return VarOut
    except:
        # It wasn't pickled.  Return the default.
        return DefaultValue
