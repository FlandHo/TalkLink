from tkinter import *
from tkinter import ttk

def versionCommand():
    commandWindow = Tk()
    commandWindow.title("TalkLink - Version")
    commandWindow.geometry("300x100")
    commandWindow.resizable(False, False)

    versionText = Text(commandWindow, height=7, width=41, bg="lightyellow", state=NORMAL, )
    versionStr = "TalkLink Version 1.0.0\nThank you for using TalkLink software.\nCopyright (C) Fland Studios 2026.\nCrew: Fland_Ho - Coding"
    versionText.insert(END, versionStr)
    versionText.config(state=DISABLED)
    versionText.pack()

    commandWindow.mainloop()