import socket

# Configuración del servidor TCP
HOST = 'localhost'
PORT = 3000

# Creamos el socket (AF_INET = IPv4, SOCK_STREAM = TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Reutilizar la dirección IP/Puerto si se cierra inesperadamente
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))
server_socket.listen(1) # Escucha hasta 1 cliente a la vez

print(f"Servidor corriendo en puerto {PORT}")

while True:
    # Aceptamos la conexión del cliente
    conn, addr = server_socket.accept()
    print(f"Cliente conectado desde: {addr}")
    
    try:
        while True:
            # Recibimos hasta 1024 bytes de datos
            data = conn.recv(1024)
            if not data or data == "/salir" :
                break # Si no hay datos, el cliente se desconectó
                
            # Decodificamos los bytes a texto plano
            mensaje = data.decode('utf-8')
            print(f"Mensaje recibido del cliente: {mensaje}")
            
            
    except ConnectionResetError:
        pass
    finally:
        print(f"Cliente {addr} desconectado.")
        conn.close() and server_socket.close()