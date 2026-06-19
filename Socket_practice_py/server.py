import socket
import threading
from sqlalchemy import String, create_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import sessionmaker

class Base(DeclarativeBase):
    pass

class Usuarios(Base):
    __tablename__ = "Usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, username={self.username})>"

engine = create_engine(
    "sqlite:///usuarios.db", 
    connect_args={"check_same_thread": False} # Permite que varios hilos usen el mismo archivo
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

HOST = 'localhost'
PORT = 3000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
# Aumentamos el listen para permitir una cola de espera más grande si llegan todos a la vez
server_socket.listen(5) 

print(f"Servidor corriendo en puerto {PORT}. Esperando conexiones...")

def registro(username, password):
    with Session() as session:
        user = session.query(Usuarios).filter(Usuarios.username == username).first()
        if user:
            return "El nombre de usuario ya está en uso."
        new_user = Usuarios(username=username, password=password)
        session.add(new_user)
        session.commit()
        return "Usuario registrado exitosamente."

def login(username, password):
    with Session() as session:
        user = session.query(Usuarios).filter(Usuarios.username == username).first()
        if not user:
            return "Usuario no encontrado."
        if user.password != password:
            return "Contraseña incorrecta."
        return f"Login exitoso. ¡Bienvenido {username}!"

def manejar_cliente(conn, addr):
    """
    Esta función se ejecutará en un hilo independiente para cada cliente conectado.
    """
    print(f"[NUEVA CONEXIÓN] Cliente conectado desde: {addr}")
    command = ["/salir", "/ayuda", "/login", "/registro"] 
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"[DESCONEXIÓN] Cliente {addr} se desconectó inesperadamente.")
                break
                
            mensaje = data.decode('utf-8').strip()
            
            if mensaje.startswith("/"):
                if mensaje in command:
                    if mensaje == "/salir":
                        print(f"[DESCONEXIÓN] Cliente {addr} solicitó desconexión")
                        break
                        
                    elif mensaje == "/ayuda":
                        ayuda = "\n/salir - Desconectar del servidor\n/ayuda - Mostrar ayuda\n/login - Iniciar sesión\n/registro - Registrar usuario"
                        conn.sendall(ayuda.encode('utf-8'))
                        
                    elif mensaje == "/registro":
                        conn.sendall("Ingrese nombre de usuario:".encode('utf-8'))
                        username = conn.recv(1024).decode('utf-8').strip()
                        
                        conn.sendall("Ingrese contraseña:".encode('utf-8'))
                        password = conn.recv(1024).decode('utf-8').strip()
                        
                        resultado = registro(username, password)
                        print(f"[REGISTRO] {resultado} para el usuario: {username}")
                        conn.sendall(resultado.encode('utf-8'))
                        
                    elif mensaje == "/login":
                        conn.sendall("Ingrese nombre de usuario:".encode('utf-8'))
                        username = conn.recv(1024).decode('utf-8').strip()
                        
                        conn.sendall("Ingrese contraseña:".encode('utf-8'))
                        password = conn.recv(1024).decode('utf-8').strip()
                        
                        resultado = login(username, password)
                        conn.sendall(resultado.encode('utf-8'))
                else:
                    conn.sendall("Comando no reconocido. Usa /ayuda para ver los comandos.".encode('utf-8'))
            else: 
                print(f"[{addr}] Dice: {mensaje}")

    except ConnectionResetError:
        print(f"[ERROR] Conexión con {addr} reseteada por el cliente.")
    finally:
        conn.close()
        print(f"[CIERRE] Conexión con {addr} cerrada de forma segura.")


# --- BUCLE PRINCIPAL DEL SERVIDOR ---
while True:
    try:
        # 1. El servidor se queda bloqueado aquí esperando a que alguien llegue
        conn, addr = server_socket.accept()
        
        # 2. Cuando llega alguien, creamos un hilo asignándole la función 'manejar_cliente'
        # Pasamos 'conn' y 'addr' como argumentos para que sepa con quién hablar
        hilo_cliente = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
        hilo_cliente.start()
        
        # Imprimimos cuántos hilos activos hay (restamos 1 porque el servidor en sí es un hilo)
        print(f"[SISTEMA] Conexiones activas actualmente: {threading.active_count() - 1}")
        
    except KeyboardInterrupt:
        print("\nApagando el servidor...")
        break

server_socket.close()