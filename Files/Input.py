from Tkinter import *
import tkFont
import ttk
import os
import datetime
import winsound
import threading
from ExcelFunctions import InputExcel
from functions import Die
from functions import CreateToolTip
from PIL import Image
from PIL import ImageTk
from PIL import ImageGrab

"""
Name:    Input.py
Desc:    Manages the frames and widgets which accept input from the user. The "input"
         window of Kami. The Entry widget, history, timer, etc can be found within
         this window. This is the window which the user will actually use to commit
         inputs to the excel file.
Imports: ExcelFunctions
"""


class EntryItemClass:
    def __init__(self, frame, root, WhichType, TimerCount, ExcelPath, ConfigList, History):
        """
        This is the input from the user when they are actually inputting notes.
        Hitting the enter key causes the SaveInput function to be run.
        :param frame: Which frame within the root window - WritingFrame
        :param root: The mainloop window - root
        :param WhichType: The note type being taken - Note, Test, Bug, etc.
        :param TimerCount: The current timer in place - 00:04:26 for example
        """
        self.frame = frame
        self.root = root
        self.WhichType = WhichType
        self.TimerCount = TimerCount
        self.StartingRow = 10
        self.EntryListInput = []
        self.ExcelPath = ExcelPath
        self.ConfigList = ConfigList
        self.History = History

        self.LogEntry = ttk.Entry(self.frame, width=90,
                                  font=tkFont.Font(family="Verdana", size=12))
        self.LogEntry.grid(column=0, row=1, columnspan=3, pady=(5, 5))
        self.LogEntry.focus()

        self.LogEntry.bind("<Control-KeyRelease-a>", self.SelectAll)
        self.root.bind("<Return>", self.SaveInput)

    def SaveInput(self, *args):
        """
        Grabs all of the required data and then puts them in a list (entryInput)
        It stores The inputted text, the note type, current timer count and the
        current time
        :return: EntryInput List
        """

        EntryInput = [self.WhichType.cget("text"), self.TimerCount.cget("text"),
                      self.LogEntry.get(), datetime.datetime.now().strftime("%H:%M:%S")]
        if EntryInput[2].isspace():  # If just space / nl do nothing
            self.LogEntry.delete(0, 'end')
            return
        if EntryInput[2] != "":  # If no input do nothing
            global InputExcelVar
            InputExcelVar = InputExcel(EntryInput, self.StartingRow, self.ExcelPath,
                                       self.EntryListInput, self.ConfigList)
            if InputExcelVar.Error != 1:
                self.StartingRow += 1
                self.LogEntry.delete(0, 'end')
            else:
                InputExcelVar.Error = 0

            # print self.History.MoreLess
            if self.History.MoreLess == 1:
                self.History.TearDownHistory()
                self.History.PrintExcel()

    @staticmethod
    def SelectAll(event):
        """
        Allows the user to use CTRL+a to select all text within entry widget
        """
        # print('entry.get():', self.LogEntry.get())
        # print('event.widget.get():', event.widget.get())

        # select text
        event.widget.select_range(0, 'end')
        # move cursor to the end
        event.widget.icursor('end')


class SeeThroughSlider:
    def __init__(self, frame, root):
        """
        This allows the user to set the opacity of the window, from 100% to 50%
        :param frame: Which frame within the root window - WritingFrame
        :param root: The main root window - root
        """
        self.frame = frame
        self.root = root

        # Must be in float as it only works out from 0.0 - 1.0
        self.SliderEntry = ttk.Scale(self.frame, from_=0.5, to=1, command=self.SetSeeThrough)
        CreateToolTip(self.SliderEntry, "Change the transparency of Kami Notes.")
        self.SliderEntry.set(1)
        self.SliderEntry.grid(column=0, row=2, sticky=W)

    def SetSeeThrough(self, *args):
        """
        When the slider is moved, this is called - each time.
        The slider edits the alpha (opacity) of the root window from the value
        set above
        :return: self.root.wm_attributes('-alpha', ScaleEntryValue)
        """
        global ScaleEntryValue
        ScaleEntryValue = round(self.SliderEntry.get(), 2)
        self.root.wm_attributes('-alpha', ScaleEntryValue)


class SmallHistory:
    def __init__(self, frame, ShowMoreFrame, HistoryListCap):
        """
        Displays the last 3 entry history of writen notes. The history can be
        toggled via the see history label
        :param frame: The frame in which this sits in - Writing Frame
        """
        self.frame = frame
        self.ShowMoreFrame = ShowMoreFrame
        self.HistoryCount = 1
        self.MoreLess = 0  # 0=show non, 1=show more
        self.HistoryListCap = int(HistoryListCap)

        self.SeeMoreLabel = ttk.Label(self.frame, text="History", cursor="hand2", )
        CreateToolTip(self.SeeMoreLabel, "See or hide the history of your notes")
        if self.HistoryCount != 0:
            self.SeeMoreLabel.grid(column=0, row=2, columnspan=3)
        self.SeeMoreLabel.bind("<Button-1>", self.ShowHistory)

        u = tkFont.Font(self.SeeMoreLabel, self.SeeMoreLabel.cget("font"))
        # u.configure(underline=True)
        self.SeeMoreLabel.configure(font=u)

    def ShowHistory(self, event):
        try:  # This stops the many lines being printed if user clicks see more before entering anything
            # print "printing:", InputExcelVar.EntryInput
            InputExcelVar.EntryInput
        except NameError:
            return

        if self.MoreLess == 0:
            LineCanvas = Canvas(self.ShowMoreFrame, width=900, height=10)
            LineCanvas.pack()
            LineCanvas.create_line(0, 5, 900, 5, fill="#474747")
            self.PrintExcel()
            try:
                if InputExcelVar.EntryInputList:
                    pass
            except NameError:
                return
            self.SeeMoreLabel.configure(text="Hide")
            self.MoreLess = 1
        elif self.MoreLess == 1:
            # run hide tool tip
            for widget in self.ShowMoreFrame.winfo_children():
                widget.destroy()
            self.ShowMoreFrame.pack_forget()
            self.SeeMoreLabel.configure(text="History")
            self.MoreLess = 0

    def TearDownHistory(self):
        for widget in self.ShowMoreFrame.winfo_children():
            widget.destroy()
        LineCanvas = Canvas(self.ShowMoreFrame, width=900, height=10)
        LineCanvas.pack()
        LineCanvas.create_line(0, 5, 900, 5, fill="#474747")

    def DrawHRLine(self):
        HRLine = Canvas(self.ShowMoreFrame, width=900, height=10)
        HRLine.pack()
        HRLine.create_line(435, 5, 470, 5, fill="#474747")

    def PrintExcel(self):
        try:
            if InputExcelVar.EntryInputList:
                pass
        except NameError:
            return
        # print InputExcelVar.EntryInputList
        self.ShowMoreFrame.pack(padx=(5, 5), pady=(5, 5), fill=X)

        # if list of input <= config history cap or if history cap is 0 (0=everything)
        if len(InputExcelVar.EntryInputList) <= self.HistoryListCap or self.HistoryListCap == 0:
            # print InputExcelVar.EntryInputList
            for each in InputExcelVar.EntryInputList:
                # print each
                MoreHistoryLabel = Label(self.ShowMoreFrame, text=each, anchor=CENTER,
                                         font=("Verdana", 10), wraplength=900)
                MoreHistoryLabel.pack()
                self.DrawHRLine()

        else:
            InputExcelVar.EntryInputList = InputExcelVar.EntryInputList[-self.HistoryListCap:]
            for each in InputExcelVar.EntryInputList:
                MoreHistoryLabel = Label(self.ShowMoreFrame, text=each, anchor=CENTER,
                                         font=("Verdana", 10), wraplength=900)
                MoreHistoryLabel.pack()
                self.DrawHRLine()


class TypeOfLog:
    def __init__(self, frame, root, colorframe, WhichType, WhichTypeBGColor):
        """
        This shows the user what note type they are currently writing in. It
        will also change the color of the color frame depending on what the
        note type is. The note type and colors are defined within the config.txt
        file.

        Allows the use of the up and down arrows, or just left/right clicking on
        the label will change the state
        :param frame: The frame in which this sits in - WritingFrame
        :param root: The root window - root
        :param colorframe: The frame which changes color - ColorFrame
        :param WhichType: The note type list which is being used - defined within config
        :param WhichTypeBGColor: The frame color list which is being used - defined in config
        """
        self.frame = frame
        self.root = root
        self.colorframe = colorframe
        self.WhichType = WhichType
        self.WhichTypeBGColor = WhichTypeBGColor
        self.Index = 0

        self.root.bind("<KeyRelease-Up>", self.UpSelectionLogType)
        self.root.bind("<KeyRelease-Down>", self.DownSelectionLogType)

        self.colorframe.configure(background=self.WhichTypeBGColor[self.Index], borderwidth=2)

        self.LoggingTypeLabel = Label(self.frame, text=self.WhichType[self.Index],
                                      font="Verdana", cursor="hand2")
        CreateToolTip(self.LoggingTypeLabel, "Change the type of note you are taking. Keybinding of up and down arrows.")
        self.LoggingTypeLabel.grid(column=2, row=0, sticky=E)
        self.LoggingTypeLabel.bind("<ButtonRelease-1>", self.UpSelectionLogType)
        self.LoggingTypeLabel.bind("<ButtonRelease-3>", self.DownSelectionLogType)

    # Should probs join these two functions into one a pass through a parameter(?)
    def UpSelectionLogType(self, event):
        """
        This cycles through the list of note types and colors. Adding 1 to the
        index each time up arrow or left click. If the end of the index is reached,
        it will loop back through the beginning again. 5 > 6 > 0 > 1 > etc...
        """
        if self.Index < len(self.WhichType)-1:
            self.Index += 1
            self.LoggingTypeLabel.configure(text=self.WhichType[self.Index])
            self.colorframe.configure(background=self.WhichTypeBGColor[self.Index])
        else:
            self.Index = 0
            self.LoggingTypeLabel.configure(text=self.WhichType[self.Index])
            self.colorframe.configure(background=self.WhichTypeBGColor[self.Index])

    def DownSelectionLogType(self, event):
        """
        This cycles through the lost of note types and colors. Subtracting 1 to
        the index each time down arrow or right click. if the end of the index is
        reached it will loop back through the beginning again. 2 > 1 > 0 > 6 > etc...
        """
        if self.Index > 0:
            self.Index -= 1
            self.LoggingTypeLabel.configure(text=self.WhichType[self.Index])
            self.colorframe.configure(background=self.WhichTypeBGColor[self.Index])
        else:
            self.Index = len(self.WhichType)-1
            self.LoggingTypeLabel.configure(text=self.WhichType[self.Index])
            self.colorframe.configure(background=self.WhichTypeBGColor[self.Index])


# noinspection PyTypeChecker
class CountDownTimer:
    def __init__(self, TimerStatus, TimerCount, frame):
        """
        Inits the CountDownTimer - This is used to tell the user how long is
        left on the countdown timer. Grabs the inputted time from the user in
        the timer entry
        :param TimerStatus: Grabbed from OptionTimer - see if the tick box is
                            selected or not. If it isnt the timer isnt drawn
                            but the logic is set in place still
        :param TimerCount:  Grabbed from TimerEntry and is the time in minutes
                            set by the user. It is * by 60 to turn the entry
                            from seconds to minutes so that it can be worked
                            with correctly. If the TimerCount < 20% of
                            remaining time it will bleep and turn font red
        :param frame:       Which frame the timer is drawn on
        """
        # TimerAlarm = datetime.timedelta(minutes=TimerAlarm)
        self.TimerCount = TimerCount
        self.TimerStatus = TimerStatus
        self.frame = frame

        self.TimerState = 1  # 1=Ticking, 0=paused
        self.TimerStatus = TimerStatus.state()
        self.TimerCount = TimerCount.get()
        self.TimerCount = int(self.TimerCount) * 60  # Make it into seconds. 60*60=3600seconds=1hour
        self.TimerAlarm = 0.2 * self.TimerCount  # change float for different percentage
        self.TimerAlarm = datetime.timedelta(seconds=self.TimerAlarm)
        self.TimerCount = datetime.timedelta(seconds=self.TimerCount)
        self.TimerCountLabel = ttk.Label(frame, text=self.TimerCount, font="Verdana", cursor="hand2")
        CreateToolTip(self.TimerCountLabel, "Remaining time for the session. Click to pause.")
        self.TimerCountLabel.bind("<ButtonRelease-1>", self.ChangeTimerState)
        if "selected" in self.TimerStatus:  # Only draws timer if state is true
            self.TimerCountLabel.grid(column=0, row=0, sticky=W)
        else:
            return
        self.frame.after(1000, self.Update)

    @staticmethod
    def BleepSound():  # Replace this with a wav file ... Doesnt work on new machines
        for x in range(0, 3):
            winsound.Beep(3278, 500)

    def Update(self):
        """
        This handles the updating of the label when the timer hsa ticked over
        one second. It also handles the pausing and starting of the timer via the
        Timerstate

        Along with that, it manages the 20% left alarm. It will bleep to the user
        to hint that they have only 20% of the time left and it will change the
        text red. When the timer is 00:00:00 it will remain there and be bold red

        Makes use of multi threading so that if bleeping is happening the user
        doesnt lose the ability to keep on typing
        """
        if self.TimerState == 1:  # If the timer is on 00:00 and you unpause it carries on
            self.TimerCount = self.TimerCount - datetime.timedelta(seconds=1)
            self.TimerCountLabel.configure(text=self.TimerCount)
            if self.TimerCount == self.TimerAlarm:
                # New thread so that text isnt lost if typing when bleeping
                threading.Thread(target=self.BleepSound())  # Bleeps if < 20% remaining time
                self.TimerCountLabel.configure(foreground="red")
            if str(self.TimerCount) == "0:00:00":
                self.TimerCount = datetime.timedelta(seconds=0)
                self.TimerCountLabel.configure(text=self.TimerCount, font="Verdana 12 bold")
                threading.Thread(target=self.BleepSound())  # Bleeps if timer == 0:00:00
                self.TimerCountLabel.configure(foreground="#C81616")
                return
        else:
            return
        self.frame.after(1000, self.Update)  # Every 1s, configure & redraw
        # print self.TimerCountLabel.cget("text")

    def UnbindClick(self):
        self.TimerCountLabel.bind("<ButtonRelease-1>", self.ChangeTimerState)

    def ChangeTimerState(self, *args):
        """
        This handles the timer appearance if the timer state (pause or ticking)
        has changed. Purple for paused, black for ticking and red if ticking
        but below the 20% mark
        """
        if str(self.TimerCount) == "0:00:00":
            return
        if self.TimerState == 1:
            self.TimerState = 0
            self.TimerCountLabel.configure(foreground="#8150E2")
            self.TimerCountLabel.unbind("<ButtonRelease-1>")
            self.TimerCountLabel.after(1000, self.UnbindClick)  # Stops the increase countdown speed bug
        elif self.TimerState == 0:
            self.TimerState = 1
            if self.TimerCount < self.TimerAlarm:
                self.TimerCountLabel.configure(foreground="#C81616")
            else:
                self.TimerCountLabel.configure(foreground="black")
            self.Update()
        else:
            "The Clocks broken!"  # Not needed but nice to have


class OpenExcelFile:
    def __init__(self, frame, root, ExcelPath, EntryLog):
        """
        Simple button which opens the current working excel file.
        :param frame: Writting Frame
        :param ExcelPath: CWD for excel path + name of file
        :param EntryLog: Entry widget
        """
        self.frame = frame
        self.root = root
        self.ExcelPath = ExcelPath
        self.EntryLog = EntryLog

        try:  # Incase there is no image.
            self.LoadExcelButton = ttk.Button(self.frame, command=lambda: self.OpenExcel())
            image = ImageTk.PhotoImage(file="Res\\Images\\open.png")
            self.LoadExcelButton.config(image=image)
            self.LoadExcelButton.image = image
            self.LoadExcelButton.grid(column=0, row=2, columnspan=3, padx=39, pady=(5, 5), sticky=E)
        except IOError:
            self.LoadExcelButton = ttk.Button(self.frame, text="Open Excel", command=lambda: self.OpenExcel())
            self.LoadExcelButton.grid(column=0, row=2, columnspan=3, padx=90, pady=(5, 5), sticky=E)

        CreateToolTip(self.LoadExcelButton, "Opens the Excel file you are currently working on")

    def OpenExcel(self):
        os.startfile(self.ExcelPath)
        self.EntryLog.focus()  # Return focus to entry after losing it to button
        PrintStatusUpdate(self.frame, self.root, "Excel file opened!")


class SaveNew:
    def __init__(self, frame, Mainloop, ConfigList, ExcelLocal, BugNumber, FocusState):
        self.frame = frame
        self.Mainloop = Mainloop
        self.Configlist = ConfigList
        self.ExcelLocal = ExcelLocal
        self.BugNumber = BugNumber
        self.FocusState = FocusState



        try:  # Incase there is no image.
            self.SaveNewButton = ttk.Button(self.frame, command=self.DieAndOpen)
            image = ImageTk.PhotoImage(file="Res\\Images\\save.png")
            self.SaveNewButton.config(image=image)
            self.SaveNewButton.image = image
            self.SaveNewButton.grid(column=0, row=2, columnspan=3, pady=(5, 5), sticky=E)
        except IOError:
            self.SaveNewButton = ttk.Button(self.frame, text="Save and New", command=lambda: self.DieAndOpen())
            self.SaveNewButton.grid(column=0, row=2, columnspan=3, pady=(5, 5), sticky=E)


        CreateToolTip(self.SaveNewButton, "Saves the current notes taken and restarts Kami for another session")


    def DieAndOpen(self):
        Die(self.Mainloop, self.Configlist, self.ExcelLocal, self.BugNumber, self.FocusState)
        # This makes it start back up under a different process
        os.execv(sys.executable, [sys.executable] + sys.argv)


class ToggleLoseFocus:
    def __init__(self, frame, root, EntryLog, HideOption):
        self.frame = frame
        self.root = root
        self.EntryLog = EntryLog
        self.HideOption = HideOption
        self.InvisibleCheckBox = ttk.Checkbutton(self.frame,
                                                 text="Hide",
                                                 state="normal",
                                                 command=self.CheckFocus)
        CreateToolTip(self.InvisibleCheckBox, "Enable or disable changing transparency when Kami loses focus")
        if self.HideOption == 1:
            self.InvisibleCheckBox.state(["selected", "!alternate"])
        else:
            self.InvisibleCheckBox.state(["!alternate"])
        self.InvisibleCheckBox.grid(column=0, row=2, sticky=W, padx=105)
        self.CheckFocus()  # So that it allows the first click to register

    def CheckFocus(self):
        self.EntryLog.focus()
        if "selected" in self.InvisibleCheckBox.state():
            self.root.bind("<FocusOut>", self.LostFocus)
            self.root.bind("<FocusIn>", self.GainFocus)
        else:
            self.root.unbind("<FocusOut>")  # To make sure its always on.
            # self.root.unbind("<FocusIn>")

    def LostFocus(self, event):
        if event.widget == self.root:
            self.root.wm_attributes('-alpha', 0.5)

    def GainFocus(self, event):
        if event.widget == self.root:
            self.root.wm_attributes('-alpha', ScaleEntryValue)  # Grabs the value of the scale.


class PrintStatusUpdate:
    """
    Displays the status update when it is called, after 3s it closes the label.
    For example, good for displaying label and letting the user know that the
    screenshot has been taken, etc.
    """
    def __init__(self, frame, root, InputtedText):
        """
        :param frame: The writting frame
        :param root: The main loop
        :param InputtedText: Which text you would like to display
        """
        self.frame = frame
        self.root = root
        self.InputtedText = InputtedText

        self.PrintedText = ttk.Label(frame, text=self.InputtedText, font=("Verdana", 10))
        self.PrintedText.grid(column=0, row=0, columnspan=3, sticky=N)
        self.root.after(3000, lambda: self.PrintedText.grid_forget())


# TODO: select specific screen region. - Don't even know how you would begin to do this lol
class TakeScreenShotButton:
    def __init__(self, frame, root, LocalSavePath, Config, BugNumber, SVNOption, StartingNumber, EntryLog):
        """
        Handles the creation of screenshots when the user clicks the screenshot
        button. It will dump the png to the local path with a timestamp. It will
        also dump it in the SVN if the option was ticked

        :param frame: Writting frame
        :param root: Root window
        :param LocalSavePath: path for the local excel save
        :param Config: config list, used to grab the SVN path
        :param BugNumber: Current bug number
        :param SVNOption: Check box state for save to svn
        :param StartingNumber: starting number which increments every time a
        screenshot is taken within the session
        :param EntryLog: The entry field, used for focus
        """
        self.frame = frame
        self.root = root
        self.LocalSavePath = LocalSavePath
        self.Config = Config
        self.BugNumber = BugNumber
        self.SVNOption = SVNOption
        self.StartingNumber = StartingNumber
        self.EntryLog = EntryLog

        try:  # Incase there is no image.
            self.ScreenshotButton = ttk.Button(self.frame, command=lambda: self.TakeScreenshot())
            image = ImageTk.PhotoImage(file="Res\\Images\\cam.png")
            self.ScreenshotButton.config(image=image)
            self.ScreenshotButton.image = image
            self.ScreenshotButton.grid(column=0, row=2, columnspan=3, padx=78, pady=(5, 5), sticky=E)
        except IOError:
            self.ScreenshotButton = ttk.Button(self.frame, text="Screenshot", command=lambda: self.TakeScreenshot())
            self.ScreenshotButton.grid(column=0, row=2, columnspan=3, padx=172, pady=(5, 5), sticky=E)

        CreateToolTip(self.ScreenshotButton, "Take a screenshot of your main monitor, Keyboard shortcut is CTRL+P. Currently only captures main monitor.")
        self.root.bind("<Control-KeyRelease-p>", self.TakeScreenshot)
        self.root.bind("<Control-KeyRelease-P>", self.TakeScreenshot)  # Incase caps is on

    # TODO: Maybe handle which monitor to screen cap?
    def TakeScreenshot(self, *args):
        PrintStatusUpdate(self.frame, self.root, "Screenshot taken!")
        self.root.wm_attributes('-alpha', 0.0)
        TakenImage = ImageGrab.grab()
        self.root.wm_attributes('-alpha', ScaleEntryValue)
        self.EntryLog.focus()
        self.StartingNumber += 1
        TimeStamp = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

        ImageFileName = "image"+str(self.StartingNumber)+"-"+TimeStamp+".png"
        TakenImage.save(self.LocalSavePath+ImageFileName)

        if "selected" in self.SVNOption:
            if not os.path.exists(self.Config[3] + "/" + self.BugNumber):
                os.makedirs(self.Config[3] + "/" + self.BugNumber)
                TakenImage.save(self.Config[3] + "/" + self.BugNumber + ImageFileName)
            else:
                TakenImage.save(self.Config[3] + "/" + self.BugNumber + ImageFileName)
        else:
            return
