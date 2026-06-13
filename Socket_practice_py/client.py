import socket
import sys
import threading

HOST = 'localhost'
PORT = 3000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def escuchar_servidor(sock):
    """Función que corre en segundo plano esperando datos del servidor"""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nEl servidor cerró la conexión.")
                break
            
            mensaje = data.decode('utf-8')
            # \r vuelve al inicio para no romper el formato del "> "
            sys.stdout.write(f"\rMensaje del server: {mensaje}\n> ")
            sys.stdout.flush()
        except (ConnectionAbortedError, ConnectionResetError):
            break
            
    print("\nHilo de escucha finalizado.")
    sys.exit(0)

try:
    client_socket.connect((HOST, PORT))
    print("Conectado al servidor.")
    
    # Iniciamos el hilo para escuchar al servidor en paralelo
    threading.Thread(target=escuchar_servidor, args=(client_socket,), daemon=True).start()
    
    # Bucle principal para leer el teclado
    while True:
        line = input("> ")
        if line.strip():
            # Enviamos el texto convertido a bytes
            client_socket.sendall(line.encode('utf-8'))
            
            if line == "/salir":
                print("Desconectando...")
                client_socket.close()
                break
            

except Exception as e:
    print(f"Error: {e}")
finally:
    client_socket.close()
    print("Socket cerrado. Programa finalizado.")