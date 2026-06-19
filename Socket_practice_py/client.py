import socket
import sys
import threading
import os

HOST = 'localhost'
PORT = 3000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def escuchar_servidor(sock):
    # Función que corre en segundo plano esperando datos del servidor
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nEl servidor cerró la conexión.")
                # os._exit(0) fuerza el cierre total del programa. 
                # sys.exit() solo cerraría este hilo y te dejaría trabado en el input()
                os._exit(0) 
            
            mensaje = data.decode('utf-8')
            # \r vuelve al inicio para no romper el formato del "> "
            sys.stdout.write(f"\rMensaje del server: {mensaje}\n> ")
            sys.stdout.flush()
            
        except (ConnectionAbortedError, ConnectionResetError, OSError):
            # OSError se lanza si el socket se cierra desde el hilo principal mientras recv() espera
            break
            
    print("\nHilo de escucha finalizado.")

try:
    client_socket.connect((HOST, PORT))
    print("Conectado al servidor. Escribe /ayuda para ver los comandos.")
    
    # Iniciamos el hilo para escuchar al servidor en paralelo
    threading.Thread(target=escuchar_servidor, args=(client_socket,), daemon=True).start()
    
    # Bucle principal para leer el teclado
    while True:
        try:
            line = input("> ")
            if line.strip():
                # Enviamos el texto convertido a bytes
                client_socket.sendall(line.encode('utf-8'))
                
                if line == "/salir":
                    print("Desconectando...")
                    break # Salimos del bucle para que el bloque finally cierre todo limpiamente
                    
        except (KeyboardInterrupt, EOFError):
            # Permite salir limpiamente si el usuario presiona Ctrl+C
            print("\nCierre forzado detectado. Desconectando...")
            break

except ConnectionRefusedError:
    print("Error: No se pudo conectar. Verifica que el servidor esté encendido.")
except Exception as e:
    print(f"Error inesperado: {e}")
finally:
    # Nos aseguramos de cerrar el socket pase lo que pase
    try:
        client_socket.close()
    except:
        pass
    print("Socket cerrado. Programa finalizado.")