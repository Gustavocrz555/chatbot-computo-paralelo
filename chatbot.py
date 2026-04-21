import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Función para conectar con la base de datos de Render
def get_db_connection():
    # Esta URL la configuraremos en el panel de Render
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url, sslmode='require')

def motor_nlu_db(mensaje):
    """Lógica NLU: Busca conceptos en la base de datos."""
    mensaje = mensaje.lower()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query para buscar el mensaje dentro del array de keywords en la DB
        query = "SELECT respuesta FROM conocimiento_paralelo WHERE %s ILIKE ANY(keywords);"
        cur.execute(query, (f"%{mensaje}%",))
        
        resultado = cur.fetchone()
        cur.close()
        conn.close()

        if resultado:
            return resultado[0]
        else:
            return "Lo siento, no tengo ese concepto en mi base de datos técnica. Intenta con: Amdahl, Flynn, MPI o Memoria Compartida."
    
    except Exception as e:
        if conn: conn.close()
        return f"Error de conexión con la base de datos: {str(e)}"

@app.route('/')
def index():
    return "<h1>Servidor del Chatbot de Cómputo Paralelo</h1><p>Estado: Activo</p>"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'mensaje' not in data:
        return jsonify({"respuesta": "Error: No se recibió ningún mensaje."}), 400
    
    # Procesar el mensaje
    respuesta_final = motor_nlu_db(data['mensaje'])
    
    return jsonify({
        "respuesta": respuesta_final,
        "usuario": data['mensaje']
    })

if __name__ == '__main__':
    # Render asigna un puerto dinámico
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)