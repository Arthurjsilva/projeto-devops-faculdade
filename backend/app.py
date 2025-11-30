from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Configuração do Banco de Dados (vinda de variáveis de ambiente do Docker)
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS')
    )
    return conn

@app.route('/')
def hello():
    return jsonify({"message": "API DevOps funcionando!"})

# Rota GET (Listar dados)
@app.route('/items', methods=['GET'])
def get_items():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM items;')
        items = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota POST (Criar dados - JSON)
@app.route('/items', methods=['POST'])
def add_item():
    new_item = request.get_json()
    name = new_item.get('name')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO items (name) VALUES (%s)', (name,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Item criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Cria a tabela se não existir (apenas para teste rápido)
    try:
        # Nota: Em produção idealmente usamos migrations, mas aqui simplificaremos
        pass 
    except:
        pass
    app.run(host='0.0.0.0', port=5000)