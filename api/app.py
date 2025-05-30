from flask import Flask, request, jsonify
import psycopg
import os
from psycopg.rows import dict_row

app = Flask(__name__)

# database config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'testdb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        return None

def init_db():
    """Create the clients table if it does not exist."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            print("Clients table created/verified successfully!")
        except Exception as e:
            print(f"Error creating/verifying clients table: {e}")

@app.route('/')
def hello_world():
    return {'message': 'Hello World from Kubernetes!'}

@app.route('/health')
def health():
    conn = get_db_connection()
    if conn:
        conn.close()
        return {'status': 'healthy', 'database': 'connected'}
    return {'status': 'unhealthy', 'database': 'disconnected'}, 500

@app.route('/clients', methods=['POST'])
def create_client():
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'email' not in data:
            return {'error': 'Invalid input: name and email are required'}, 400

        conn = get_db_connection()
        if not conn:
            return {'error': 'Database connection error'}, 500

        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO clients (name, email) VALUES (%s, %s) RETURNING id',
            (data['name'], data['email'])
        )
        client_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return {'message': 'Client successfully created', 'id': client_id}, 201

    except psycopg.IntegrityError:
        return {'error': 'Email already exists'}, 409
    except Exception as e:
        return {'error': f'Internal error: {str(e)}'}, 500

@app.route('/clients', methods=['GET'])
def get_clients():
    try:
        conn = get_db_connection()
        if not conn:
            return {'error': 'Internal error'}, 500

        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute('SELECT id, name, email, created_at FROM clients ORDER BY created_at DESC')
        clients = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert the fetched data into a list of dictionaries
        clients_list = []
        for client in clients:
            clients_list.append({
                'id': client['id'],
                'name': client['name'],
                'email': client['email'],
                'created_at': client['created_at'].isoformat() if client['created_at'] else None
            })

        return {'clients': clients_list}, 200

    except Exception as e:
        return {'error': f'Internal error: {str(e)}'}, 500

if __name__ == '__main__':
    init_db() # Only init postgress after api
    app.run(host='0.0.0.0', port=8000, debug=True)