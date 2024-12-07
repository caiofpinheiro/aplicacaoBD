import qrcode
from cryptography.fernet import Fernet
import mysql.connector
from mysql.connector import Error
import cv2
import pyzbar.pyzbar as pyzbar

# Configuração do banco de dados
def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='controle_acesso',
            user='seu_usuario',
            password='sua_senha'
        )
        if conexao.is_connected():
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Criação da tabela de usuários
def criar_tabela(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        matricula VARCHAR(255) NOT NULL UNIQUE
    )""")
    conexao.commit()

# Geração da chave de criptografia
chave = Fernet.generate_key()
cipher_suite = Fernet(chave)

# Função para registrar usuário e gerar QR code
def registrar_usuario(conexao, nome, matricula):
    cursor = conexao.cursor()
    dados_criptografados = cipher_suite.encrypt(matricula.encode())
    cursor.execute("INSERT INTO usuarios (nome, matricula) VALUES (%s, %s)", (nome, dados_criptografados))
    conexao.commit()
    qr = qrcode.make(dados_criptografados)
    qr.save(f'{nome}_qr.png')
    print(f"QR code gerado para {nome}")

# Função para verificar acesso com QR code
def verificar_acesso(qr_code_img):
    decoded_objects = pyzbar.decode(qr_code_img)
    for obj in decoded_objects:
        dados_decriptografados = cipher_suite.decrypt(obj.data).decode()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE matricula=%s", (dados_decriptografados,))
        resultado = cursor.fetchone()
        if resultado:
            print(f"Acesso permitido para {resultado[1]}")
        else:
            print("Acesso negado")

if __name__ == "__main__":
    conexao = criar_conexao()
    if conexao:
        criar_tabela(conexao)
        registrar_usuario(conexao, 'João Silva', '12345')
        qr_code_img = cv2.imread('João Silva_qr.png')
        verificar_acesso(qr_code_img)
        conexao.close()