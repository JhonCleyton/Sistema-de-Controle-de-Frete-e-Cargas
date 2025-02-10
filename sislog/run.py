import subprocess
import webbrowser
import time
import os
import sys
import signal
import psutil

def kill_process_on_port(port):
    """Mata qualquer processo que esteja usando a porta especificada"""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    os.kill(proc.pid, signal.SIGTERM)
                    time.sleep(1)  # Espera um pouco para o processo terminar
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def main():
    # Configurações
    PORT = 2000
    URL = f"http://localhost:{PORT}"
    
    try:
        # Mata qualquer processo que esteja usando a porta
        kill_process_on_port(PORT)
        
        # Inicia o servidor Flask em um processo separado
        print("Iniciando o servidor...")
        server_process = subprocess.Popen([sys.executable, "app.py"], 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        
        # Espera um pouco para o servidor iniciar
        time.sleep(2)
        
        # Verifica se o servidor iniciou corretamente
        if server_process.poll() is not None:
            print("Erro ao iniciar o servidor!")
            return
        
        # Abre o navegador padrão
        print(f"Abrindo o navegador em {URL}")
        webbrowser.open(URL)
        
        # Mantém o script rodando
        try:
            while True:
                time.sleep(1)
                # Se o servidor parar, também para o script
                if server_process.poll() is not None:
                    break
        except KeyboardInterrupt:
            print("\nEncerrando o servidor...")
            server_process.terminate()
            server_process.wait()
    
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        # Garante que o processo do servidor seja terminado
        try:
            server_process.terminate()
            server_process.wait()
        except:
            pass

if __name__ == "__main__":
    main()
