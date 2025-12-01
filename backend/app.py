import os
import psycopg2
from flask import Flask, request, jsonify, render_template
from time import sleep

app = Flask(__name__)

# Configurações do Banco de Dados (Vêm do docker-compose)
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')

def get_db_connection():
    # Tenta conectar com repetição (caso o banco demore a subir)
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            return conn
        except Exception as e:
            print(f"Banco indisponível, tentando novamente... Erro: {e}")
            retries -= 1
            sleep(2)
    return None

def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT NOT NULL);')
        conn.commit()
        cur.close()
        conn.close()

# Inicializa o banco ao ligar o app
with app.app_context():
    init_db()

@app.route('/')
def home():
    # Serve o arquivo HTML que criamos
    return render_template('index.html')

@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro ao conectar no banco"}), 500
    
    cur = conn.cursor()
    cur.execute('SELECT name FROM items;')
    items = cur.fetchall()
    cur.close()
    conn.close()
    
    # Formata para JSON
    lista_tarefas = [{"name": item[0]} for item in items]
    return jsonify(lista_tarefas)

@app.route('/items', methods=['POST'])
def add_item():
    new_item = request.json.get('name')
    if not new_item:
        return jsonify({"error": "Nome vazio"}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro ao conectar no banco"}), 500

    cur = conn.cursor()
    cur.execute('INSERT INTO items (name) VALUES (%s)', (new_item,))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Item criado!", "item": new_item}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)