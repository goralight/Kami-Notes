# from Tkinter import *
# from tkinter.scrolledtext import ScrolledText <-- Not sure if need?
# import ttk
import tkMessageBox
import os
from shutil import copy
# import time
# import datetime
# import winsound
# import threading

FirstCWD = os.path.dirname(os.path.realpath(__file__))
ResDir = FirstCWD[:-5]+"\Res"


def ConfigureOptions():
    """
    Reads the config.txt file within the Res dir.
    reads a line and then places it inside a list, moves onto the next one.
    :return: List of options. 6 Options total.
    """
    with open(ResDir+"\config.txt") as options:
        lines = options.read().split("\n")
    return lines
    # 0 = enable timer tick value
    # 1 = default timer val
    # 2 = enable save to svn tick value
    # 3 = path to svn
    # 4 = path to local save
    # 5 = list of jira types
    # 6 = reporters name
    # 7 = setup
    # 8 = log types
    # 9 = log type colors

# [0] # Enable timer tick box
EnableTimerTickBox = ConfigureOptions()[0]
EnableTimerTickBox = EnableTimerTickBox[22:]
EnableTimerTickBox = int(EnableTimerTickBox)

# [1] # Default timer value
DefaultTimerValue = ConfigureOptions()[1]
DefaultTimerValue = DefaultTimerValue[15:]
DefaultTimerValue = int(DefaultTimerValue)

# [2] # Enable save to SVN tick box
EnableSaveToSVN = ConfigureOptions()[2]
EnableSaveToSVN = EnableSaveToSVN[17:]
EnableSaveToSVN = int(EnableSaveToSVN)

# [3] # Default value for the path to SVN
SVNDefaultPath = ConfigureOptions()[3]
SVNDefaultPath = SVNDefaultPath[18:]

# [4] # Default Path for local save
LocalSavePathway = ConfigureOptions()[4]
LocalSavePathway = LocalSavePathway[25:]

# [5] # Sorts the listing out for the Jira type in the dropdown menu
JiraList = ConfigureOptions()[5]
JiraList = JiraList.split(", ")
JiraList[0] = JiraList[0][12:]

# [6] # Default value for the reporters name
ReporterName = ConfigureOptions()[6]
ReporterName = ReporterName[15:]

# [7] # Default value for the setup
SetupInfo = ConfigureOptions()[7]
SetupInfo = SetupInfo[7:]

# [8] # Log Type value list
Logtype = ConfigureOptions()[8]
Logtype = Logtype.split(", ")
Logtype[0] = Logtype[0][10:]

# [9] # Log Type background color linked to log type
LogTypeColor = ConfigureOptions()[9]
LogTypeColor = LogTypeColor.split(", ")
LogTypeColor[0] = LogTypeColor[0][19:]

# [10] # Charter Type List
CharterType = ConfigureOptions()[10]
CharterType = CharterType.split(", ")
CharterType[0] = CharterType[0][14:]


def ConfirmButtonReturn(TimerStatus, TimerCount, SVNStatus, SVNPath,
                        LocalPath, JiraType, JiraNumber, ReportersName,
                        SetupEntryInfo, CharterType):
    """
    Grabs the options set by the user and assigns them to their respective
    parameter.
    :param TimerStatus: Tuple, Tick Box of the Timer State.
                        selected= ticked, ()= unticked
    :param TimerCount: String, Number inputted from user for the minute timer.
    :param SVNStatus: Tuple, Tick Box of the SVN State.
                      selected= ticked, ()= unticked
    :param SVNPath: String, Inputted path for SVN for saving inside SVN dir,
                    C:/...
    :param LocalPath: String, Inputted path for Local save copy, C:/...
    :param JiraType: String, Abbreviation of Jira type, EP= Eprais, etc...
    :param JiraNumber: String, Jira number entry, 426
    :param ReportersName: String, name of the reporter for the current testing
    :param SetupEntryInfo: String, current setup for the testing environment

    Example:
    [('selected',), '60', ('selected',), 'C:/Users/jfriend.SPIDEX/Desktop/SVN',
    'C:/Users/jfriend.SPIDEX/Desktop/Kami/JiraLogs', 'EP', '426', 'JFriend',
    'W10, S4B26, SQL2016, Chrome']
    """

    # List of getters for pulling data of where their respective location is
    # within the gui. TimerStatus checks the state of the timer checkbox and
    # assigns it to the var and so on...
    TimerStatus = TimerStatus.state()
    TimerCount = TimerCount.get()
    SVNStatus = SVNStatus.state()
    SVNPath = SVNPath.get()
    LocalPath = LocalPath.get()
    JiraType = JiraType.get()
    JiraNumber = JiraNumber.get()
    ReportersName = ReportersName.get()
    SetupEntryInfo = SetupEntryInfo.get()
    CharterTypeInfo = CharterType.get()

    # Once all assigned place in a list to work with.
    ConfigList = [TimerStatus, TimerCount, SVNStatus,
                  SVNPath, LocalPath, JiraType,
                  JiraNumber, ReportersName, SetupEntryInfo,
                  CharterTypeInfo]

    return ConfigList


def ValidationError(ErrorMessage):
    """
    Simple error popup window which has the title Validation Error and
    contains the error messages which is passed through as a parameter
    :param ErrorMessage: String of the errror
    :return: The popup window itself
    """
    tkMessageBox.showerror("Validation Error!", ErrorMessage)


def ClearWindow(*args):
    """
    Cleans the window, should input as many frames as is needed
    for just showing the root window. But this could also be used for
    clearing out just one frame.
    """
    for each in args:
        each.pack_forget()


def Die(MainLoop, ConfigList, ExcelLocal):
    """
    Simple function to perform other processes before actually killing the
    script. Here could add saving / other close down features before it is
    killed from the user
    :param MainLoop: The Root frame to kill.
    """
    print "It closed and I printed before I died... YAY!"
    if "selected" in ConfigList[2]:
        if not os.path.exists(ConfigList[3]):
            os.makedirs(ConfigList[3])
            copy(ExcelLocal, ConfigList[3])
        else:
            copy(ExcelLocal, ConfigList[3])

    MainLoop.destroy()  # Same as using the W10 kill protocol


# Placeholder function
def PrintMe():
    print "I am a placeholder!"