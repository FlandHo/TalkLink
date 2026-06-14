# server.py
import socket
import threading

clients = {}
nicknames = set()
lock = threading.Lock()
HOST = '0.0.0.0'
PORT = 5000

def broadcast(message, exclude_sock=None):
    with lock:
        for sock in list(clients.keys()):
            if sock is exclude_sock:
                continue
            try:
                sock.sendall((message + '\n').encode('utf-8'))
            except:
                sock.close()
                if sock in clients:
                    del clients[sock]

def handle_client(conn, addr):
    try:
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        nickname = data.decode('utf-8').strip()
    except:
        conn.close()
        return

    with lock:
        if nickname in nicknames:
            try:
                conn.sendall('错误：昵称已被占用，请重新连接\n'.encode('utf-8'))
            except:
                pass
            conn.close()
            return
        nicknames.add(nickname)
        clients[conn] = nickname

    print(f"客户端已连接: {nickname} @ {addr}")
    welcome_msg = f"欢迎 {nickname} 加入 Fland 的聊天室\n可用命令：\n/version - 查看版本\n/list - 查看在线人数与用户名"
    try:
        conn.sendall((welcome_msg + '\n').encode('utf-8'))
    except:
        pass
    join_msg = f"*** {nickname} 加入了聊天室 ***"
    broadcast(join_msg, exclude_sock=conn)

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            message = data.decode('utf-8').strip()
            if not message:
                continue

            if message == '/list':
                with lock:
                    if not nicknames:
                        reply = "当前没有其他在线用户"
                    else:
                        users = ', '.join(sorted(nicknames))
                        reply = f"在线用户 ({len(nicknames)} 人): {users}"
                try:
                    conn.sendall((reply + '\n').encode('utf-8'))
                except:
                    pass
            elif message.startswith('/'):
                try:
                    conn.sendall('未知命令，可用命令：/version, /list\n'.encode('utf-8'))
                except:
                    pass
            else:
                full_msg = f"{nickname}: {message}"
                broadcast(full_msg, exclude_sock=conn)
    except:
        pass
    finally:
        with lock:
            if conn in clients:
                del clients[conn]
            nicknames.discard(nickname)
        try:
            conn.close()
        except:
            pass
        leave_msg = f"*** {nickname} 离开了聊天室 ***"
        broadcast(leave_msg)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(50)
    print(f"Server running on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer closed")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()