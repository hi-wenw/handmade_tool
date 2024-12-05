## PYTHON
## ******************************************************************** ##
## author: hewenbao
## create time: 2024/07/31 10:22:58 GMT+08:00
## ******************************************************************** ##
import socket


def test_connection(host, port):
    try:
        # 创建一个socket对象
        sock = socket.create_connection((host, port), timeout=10)
        print(f"Successfully connected to {host} on port {port}")
        sock.close()
    except socket.error as e:
        print(f"Failed to connect to {host} on port {port}: {e}")


# MySQL服务器的IP地址和端口
host = "11.24.98.182"
port = 14568

# 测试连接
test_connection(host, port)
