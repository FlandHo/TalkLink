# server.py
import socket
import threading

clients = {}
nicknames = set()
pending_auth = set()
lock = threading.Lock()
HOST = '0.0.0.0'
PORT = 5000
ADMIN_USERNAME = "Fland"
ADMIN_PASSWORD = " **请将此处修改为自己的管理员密码** "

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

def send_to_sock(sock, message):
    try:
        sock.sendall((message + '\n').encode('utf-8'))
    except:
        pass

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
            send_to_sock(conn, "错误：昵称已被占用，请重新连接")
            conn.close()
            return

    if nickname == ADMIN_USERNAME:
        with lock:
            pending_auth.add(conn)
        send_to_sock(conn, "请输入特殊用户的账户密码")
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                password = data.decode('utf-8').strip()
                if password == ADMIN_PASSWORD:
                    with lock:
                        pending_auth.discard(conn)
                        nicknames.add(nickname)
                        clients[conn] = {"nickname": nickname, "is_admin": True}
                    send_to_sock(conn, "验证通过，欢迎管理员 " + nickname)
                    join_msg = f"*** {nickname} 加入了聊天室 ***"
                    broadcast(join_msg, exclude_sock=conn)
                    break
                else:
                    send_to_sock(conn, "密码错误，连接已关闭")
                    conn.close()
                    return
            if not conn._closed:
                pass
        except:
            pass
        finally:
            with lock:
                pending_auth.discard(conn)
                if conn in clients:
                    del clients[conn]
                nicknames.discard(nickname)
            try:
                conn.close()
            except:
                pass
            return

    with lock:
        clients[conn] = {"nickname": nickname, "is_admin": False}
        nicknames.add(nickname)

    print(f"客户端已连接: {nickname} @ {addr}")
    welcome_msg = f"欢迎 {nickname} 加入 Fland 的聊天室\n可用命令：\n/version - 查看版本\n/list - 查看在线人数与用户名"
    send_to_sock(conn, welcome_msg)
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
                send_to_sock(conn, reply)
                continue

            if message.startswith('/kick '):
                with lock:
                    if conn not in clients or not clients[conn].get("is_admin", False):
                        send_to_sock(conn, "权限不足，仅管理员可执行此命令")
                        continue
                    target = message[6:].strip()
                    if not target:
                        send_to_sock(conn, "用法: /kick 用户名")
                        continue
                    if target == clients[conn]["nickname"]:
                        send_to_sock(conn, "不能踢自己")
                        continue
                    target_sock = None
                    for sock, info in clients.items():
                        if info["nickname"] == target:
                            target_sock = sock
                            break
                    if target_sock is None:
                        send_to_sock(conn, f"用户 {target} 不在线")
                        continue
                    send_to_sock(target_sock, "你已被管理员踢出聊天室")
                    try:
                        target_sock.close()
                    except:
                        pass
                    del clients[target_sock]
                    nicknames.discard(target)
                    kick_msg = f"*** {target} 被管理员踢出聊天室 ***"
                    broadcast(kick_msg)
                continue

            if message.startswith('/'):
                send_to_sock(conn, "未知命令，可用命令：/version, /list, /kick 用户名 (仅管理员)")
                continue

            full_msg = f"{nickname}: {message}"
            broadcast(full_msg, exclude_sock=conn)
    except:
        pass
    finally:
        with lock:
            if conn in clients:
                info = clients.pop(conn)
                nicknames.discard(info["nickname"])
            else:
                nicknames.discard(nickname)
            pending_auth.discard(conn)
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
