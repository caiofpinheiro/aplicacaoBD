import qrcode
from cryptography.fernet import Fernet
import mysql.connector
from mysql.connector import Error
import os

# Geração da chave de criptografia ou carregamento de uma chave existente
chave_arquivo = 'chave.key'
if os.path.exists(chave_arquivo):
    with open(chave_arquivo, 'rb') as file:
        chave = file.read()
else:
    chave = Fernet.generate_key()
    with open(chave_arquivo, 'wb') as file:
        file.write(chave)

cipher_suite = Fernet(chave)

# Configuração do banco de dados
def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='controle_acesso',
            user='root',
            password='sua_senha',
            port='3306'
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
        matricula VARBINARY(255) NOT NULL UNIQUE
    )""")
    conexao.commit()

# Função para registrar usuário e gerar QR code
def registrar_usuario(conexao, nome, matricula):
    cursor = conexao.cursor()
    dados_criptografados = cipher_suite.encrypt(matricula.encode())
    cursor.execute("INSERT INTO usuarios (nome, matricula) VALUES (%s, %s)", (nome, dados_criptografados))
    conexao.commit()
    qr = qrcode.make(dados_criptografados)
    qr.save(f'{nome}_qr.png')
    print(f"QR code gerado para {nome}")

# Função para interface de administrador
def interface_administrador(conexao):
    while True:
        opcao = input("Digite '1' para registrar usuário ou '0' para sair: ")
        if opcao == '1':
            nome = input("Digite o nome do usuário: ")
            matricula = input("Digite a matrícula do usuário: ")
            registrar_usuario(conexao, nome, matricula)
        elif opcao == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    conexao = criar_conexao()
    if conexao:
        criar_tabela(conexao)
        interface_administrador(conexao)
        conexao.close()
