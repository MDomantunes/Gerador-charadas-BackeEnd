from flask import Flask, jsonify, request  # Importa o Flask para criar a API e jsonify para formatar as respostas em JSON.
import random  # Usado para selecionar uma charada aleatória.
import firebase_admin  # Biblioteca do Firebase para conectar ao Firestore.
from firebase_admin import credentials, firestore  # Importa credenciais e o cliente Firestore.
from flask_cors import CORS  # Permite requisições de diferentes origens (Cross-Origin Resource Sharing).
import os 
import json
from dotenv import load_dotenv  # Carrega variáveis de ambiente de um arquivo .env.

app = Flask(__name__)  # Inicializa a aplicação Flask.
CORS(app)  # Habilita o CORS para permitir que a API seja acessada de diferentes domínios.


load_dotenv()
FBKEY = json.loads(os.getenv('CONFIG_FIREBASE')) # Carrega as credenciais do Firebase a partir de variáveis de ambiente.

# Inicializa a conexão com o Firebase usando um arquivo de credenciais.
cred = credentials.Certificate(FBKEY)  
firebase_admin.initialize_app(cred)

# Conecta ao Firestore.
db = firestore.client()

# ---- Rota principal de teste ----
@app.route('/', methods=['GET'])  # Define uma rota principal de teste.
def index():
    return 'CHARADAS API', 200  # Retorna uma mensagem simples para confirmar que a API está rodando.

# ---- Método GET - Charada aleatória ----
@app.route('/charadas', methods=['GET'])
def charada_aleatoria():
    charadas = []  # Lista para armazenar as charadas.
    lista = db.collection('charadas').stream()  # Busca todas as charadas no Firestore.
    
    for item in lista:
        charadas.append(item.to_dict())  # Converte os documentos do Firestore em dicionários.

    if charadas:
        return jsonify(random.choice(charadas)), 200  # Retorna uma charada aleatória.
    else:
        return jsonify({'mensagem': 'Erro! Nenhuma charada encontrada'}), 404  # Retorna erro se não houver charadas.

# ---- Método GET - Buscar charada pelo ID ----
@app.route('/charadas/<id>', methods=['GET'])
def busca(id):
    doc_ref = db.collection('charadas').document(id)  # Acessa um documento específico pelo ID.
    doc = doc_ref.get().to_dict()  # Obtém os dados do documento.

    if doc:
        return jsonify(doc), 200  # Retorna a charada encontrada.
    else:
        return jsonify({'mensagem': 'Erro! - Charada não encontrada'}), 404  # Retorna erro se não encontrar.

# ---- Método POST - Adicionar nova charada ----
@app.route('/charadas', methods=['POST'])
def adicionar_charada():
    dados = request.json  # Recebe os dados enviados no corpo da requisição.

    # Verifica se os campos obrigatórios estão presentes.
    if 'pergunta' not in dados or 'resposta' not in dados:
        return jsonify({'mensagem': 'Erro! - Dados inválidos'}), 400  # Retorna erro se estiver faltando informação.

    # Acessa o documento que controla o ID das charadas.
    contador_ref = db.collection('controle_id').document('contador')
    contador_doc = contador_ref.get().to_dict()
    ultimo_id = contador_doc.get('id')  # Obtém o último ID utilizado.
    novo_id = int(ultimo_id) + 1  # Incrementa o ID para a nova charada.

    contador_ref.update({'id': novo_id})  # Atualiza o ID no Firestore.

    # Adiciona a nova charada ao Firestore com o novo ID.
    db.collection('charadas').document(str(novo_id)).set({
        "id": novo_id,
        "pergunta": dados['pergunta'],
        "resposta": dados['resposta']
    })

    return jsonify({'mensagem': 'Charada adicionada com sucesso!'}), 201  # Retorna sucesso.

# ---- Método PUT - Alterar charada ----
@app.route('/charadas/<id>', methods=['PUT'])
def alterar_charada(id):
    dados = request.json  # Recebe os novos dados da charada.

    # Verifica se os campos obrigatórios foram enviados.
    if 'pergunta' not in dados or 'resposta' not in dados:
        return jsonify({'mensagem': 'Erro! - Dados inválidos'}), 400

    doc_ref = db.collection('charadas').document(id)  # Acessa o documento pelo ID.
    doc = doc_ref.get()  # Obtém os dados da charada.

    if doc.exists:
        doc_ref.update({
            "pergunta": dados['pergunta'],
            "resposta": dados['resposta']
        })
        return jsonify({'mensagem': 'Charada alterada com sucesso!'}), 201  # Retorna sucesso na alteração.
    else:
        return jsonify({'mensagem': 'Erro! - Charada não encontrada'}), 404  # Retorna erro se a charada não existir.

# ---- Método DELETE - Deletar charada ----
@app.route('/charadas/<id>', methods=['DELETE'])
def excluir_charada(id):
    doc_ref = db.collection('charadas').document(id)  # Acessa o documento pelo ID.
    doc = doc_ref.get()  # Obtém os dados.

    if not doc.exists:
        return jsonify({'mensagem': 'Erro! - Charada não encontrada'}), 404  # Retorna erro se não existir.

    doc_ref.delete()  # Exclui a charada do Firestore.
    return jsonify({'mensagem': 'Charada excluída com sucesso!'}), 200  # Retorna sucesso.

# ---- Execução do servidor ----
if __name__ == '__main__':
    app.run()  # Inicia o servidor Flask, permitindo acessos externos.
