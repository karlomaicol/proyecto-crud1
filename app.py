# Importaciones necesarias
from flask import Flask, jsonify, request #Flask: crear la aplicación web (el servidor) #jsonify: convertir datos a JSON (lo que devuelve la API) #jsonify: convertir datos a JSON (lo que devuelve la API)                                    
import pymysql #Esto sirve para permitir que otro sistema (como React o HTML) pueda conectarse a mi API. #Sin esto, el navegador bloquea la conexión (por seguridad).
import bcrypt #Esto sirve para encriptar contraseñas. 
from flasgger import Swagger #Esto sirve para crear documentación automática de la API. Me genera una página donde puedo probar las rutas.

# Crear la aplicación Flask
app = Flask(__name__)

# Permitir conexiones externas (frontend) Activo permisos para que cualquier frontend pueda consumir la API
CORS(app)

# Activar documentación Swagger Activo Swagger para ver la documentación
swagger = Swagger(app)

# Función para conectar a la base de datos
def conectar(vhost, vuser, vpass, vdb):
    return pymysql.connect(
        host=vhost,
        user=vuser,
        passwd=vpass,
        db=vdb,
        charset='utf8mb4000000000'
    )

# =========================
# CONSULTA GENERAL
# =========================
@app.route("/", methods=['GET'])
def consultar_general():
    try:
        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor() #El cursor sirve para ejecutar consultas SQL

        # Consulta todos los registros
        cur.execute("SELECT * FROM baul")
        datos = cur.fetchall() #Traigo todos los resultados

        data = []

        # Convertir resultados a JSON
        for row in datos:
            data.append({
                'id_baul': row[0],
                'plataforma': row[1],
                'usuario': row[2],
                'clave': row[3]
            })

        cur.close()
        conn.close()

        return jsonify({'baul': data})

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# =========================
# CONSULTA INDIVIDUAL
# =========================
@app.route("/consulta_individual/<codigo>", methods=['GET'])
def consulta_individual(codigo):
    try:
        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        # busco un registro especifico (evita ataques deSQL injection)
        cur.execute("SELECT * FROM baul WHERE id_baul = %s", (codigo,))
        datos = cur.fetchone()

        cur.close()
        conn.close()

        if datos: #Verifico si existe el registro
            return jsonify({
                'id_baul': datos[0],
                'plataforma': datos[1],
                'usuario': datos[2],
                'clave': datos[3]
            })
        else:
            return jsonify({'mensaje': 'No encontrado'}) 

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# =========================
# REGISTRO
# =========================
@app.route("/registro", methods=['POST']) #Ruta para insertar datos
def registro():
    try:
        data = request.get_json()

        # Encriptar contraseña
        clave = bcrypt.hashpw(
            data['clave'].encode('utf-8'),
            bcrypt.gensalt()
        )

        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        # Insertar datos en la base
        cur.execute("""
            INSERT INTO baul (plataforma, usuario, clave)
            VALUES (%s, %s, %s)
        """, (data['plataforma'], data['usuario'], clave))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'mensaje': 'Registrado'})

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# =========================
# ELIMINAR
# =========================
@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar(codigo):
    try:
        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        cur.execute("DELETE FROM baul WHERE id_baul = %s", (codigo,)) #Borro un registro por ID
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'mensaje': 'Eliminado'})

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# =========================
# ACTUALIZAR
# =========================
@app.route("/actualizar/<codigo>", methods=['PUT'])
def actualizar(codigo):
    try:
        data = request.get_json()

        # Encriptar nueva contraseña
        clave = bcrypt.hashpw(
            data['clave'].encode('utf-8'),
            bcrypt.gensalt()
        )

        conn = conectar('localhost', 'root', '1234', 'gestor_contrasena')
        cur = conn.cursor()

        cur.execute("""
            UPDATE baul   
            SET plataforma=%s, usuario=%s, clave=%s
            WHERE id_baul=%s
        """, (data['plataforma'], data['usuario'], clave, codigo))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'mensaje': 'Actualizado'})

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})


# Ejecutar servidor
if __name__ == "__main__":
    app.run(debug=True) #Muestra errores en consola. Recarga automáticamente