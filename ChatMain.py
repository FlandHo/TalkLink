# ChatMain.py
from tkinter import *
from tkinter import ttk
import UsernameValue
import ProhibitedWord
import socket
import threading
import queue
import CmdMessage as CmdMessage

window_root = Tk()
chat_display = Text(window_root, height=12.4, width=50)
chat_display.pack()

SERVER_HOST = "fland.zh.kg"
SERVER_PORT = 49928
client_sock = None
recv_queue = queue.Queue()
connected = False

def safe_append(text):
    def _do():
        chat_display.config(state='normal')
        chat_display.insert(END, text + "\n")
        chat_display.see(END)
        chat_display.config(state='disabled')
    window_root.after(0, _do)

def receive_loop():
    global connected
    try:
        while True:
            data = client_sock.recv(4096)
            if not data:
                safe_append("*** 与服务器断开连接 ***")
                connected = False
                break
            for line in data.decode('utf-8').splitlines():
                if line:
                    recv_queue.put(line)
    except:
        safe_append("*** 网络错误 ***")
        connected = False

def poll_queue():
    while not recv_queue.empty():
        msg = recv_queue.get_nowait()
        safe_append(msg)
    window_root.after(100, poll_queue)

def connect_server():
    global client_sock, connected
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((SERVER_HOST, SERVER_PORT))
        client_sock.sendall((UsernameValue.Chat_Username + '\n').encode('utf-8'))
        connected = True
        threading.Thread(target=receive_loop, daemon=True).start()
        poll_queue()
    except Exception as e:
        safe_append(f"连接服务器失败: {e}")

def send_message():
    global connected
    message = input_text.get()
    if message:
        if message in ProhibitedWord.Prohibited_message:
            input_text.delete(0, END)
            input_text.insert(0, "检测到违禁词！请重新输入！")
            return
        if not connected:
            safe_append("未连接到服务器")
            input_text.delete(0, END)
            return
        if message == "/version":
            input_text.delete(0, END)
            safe_append(f"{UsernameValue.Chat_Username}: {message}")
            CmdMessage.versionCommand()
            return
        try:
            client_sock.sendall((message + '\n').encode('utf-8'))
            safe_append(f"{UsernameValue.Chat_Username}: {message}")
        except:
            safe_append("发送失败")
            connected = False
        input_text.delete(0, END)

def append_message(text):
    safe_append(text)

window_root.resizable(False, False)
input_text = Entry(window_root, bd=3, width=35)
input_text.place(x=100, y=100)
Text_message = Label(text="消息聊天栏")
Text_message.place(x=100, y=50)
root_chatMessage = Button(window_root, text=" 发送 ", command=send_message)
root_chatMessage.place(x=356, y=170)
chat_display.config(state=DISABLED)

window_root.title("TalkLink")
window_root.geometry("400x200")

Text_message.pack(side=LEFT)
Text_message.place(x=0, y=170)
Text_message.config(font=(None, 14))
input_text.pack(side=RIGHT)
input_text.place(x=100, y=173)

window_root.after(100, connect_server)
window_root.mainloop()