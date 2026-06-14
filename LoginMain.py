from tkinter import *
from tkinter import ttk
import ProhibitedWord
import UsernameValue
global Login_Failed
login_root = Tk()

#====function ========

def login():
    global UsernameValue, Login_Failed
    if login_entry_username.get() == "":
        print("Username is empty!")
    elif login_entry_username.get() != "" and login_entry_username.get() not in ProhibitedWord.Prohibited_message and len(login_entry_username.get()) <=6:
        print("Username is set to:{}".format(login_entry_username.get()))
        UsernameValue.Chat_Username = login_entry_username.get()
        login_root.destroy()
        from ChatMain import window_root
        
#====set value ========
login_root.resizable(False, False)
login_entry_username = Entry(login_root, bd=3, width=35)
login_entry_username.place(x=100, y=100)
login_text_username = Label(text="请输入用户名")
login_text_username.place(x=100, y=50)
login_button_login = Button(login_root, text="  登录  ", command=login)
login_button_login.place(x=45, y=95)

#====set window ========
login_root.title("TalkLink - 用户名")
login_root.geometry("400x200")
login_text_username.config(font=(None, 24))

#====main loop ========
login_root.mainloop()