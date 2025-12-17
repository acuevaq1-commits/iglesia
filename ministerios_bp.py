from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import MySQLdb.cursors
import config
import os
from werkzeug.utils import secure_filename
#from flask_mysqldb import MySQL
#from datetime import datetime

ministerios_bp = Blueprint("ministerio", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#--------------------------------Para autenticación
@ministerios_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))  # o abort(401) si es API

#--------------------------------------------------
@ministerios_bp.route('/lministerios', methods=['GET'])
def lministerios():
    tabla_ministerios = get_tabla_ministerio()
    return render_template('ministerios.html', ministerio_ = tabla_ministerios)
#--------------------------------------------------
@ministerios_bp.route('/tblministerios')
def tblministerios():
    tabla_ministerios = get_tabla_ministerio()
    return render_template("ministerio.html", ministerio_= tabla_ministerios)
#--------------------------------------------------
def get_tabla_ministerio():
    cursor = mysql.connection.cursor()
    cursor.callproc('sp_all_ministerio')
    ministerios_ = cursor.fetchall()
    return ministerios_
#--------------------------------------------------
@ministerios_bp.route('/edit_ministerio/<int:codigo>', methods=['GET', 'POST'])
def edit_ministerio(codigo):
    try:
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_ministerio(%s)', (codigo,))  # <- tupla correcta

        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe el ministerio'), 404

        return jsonify({
            "opcion": row.get("opcion", ""),
            "nombre": row.get("nombre", ""),
            "descripcion": row.get("descripcion", ""),
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@ministerios_bp.route('/eli_ministerio/<int:codigo>')
def eli_ministerio(codigo):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_ministerio", (codigo, cod_usuario, ''))
         # Obtener el OUT param (mensaje)
        cur.execute("SELECT @p_mensaje;")
        mensaje = cur.fetchone()[0]
        cur.close()

        return jsonify({'status': True,'mensaje': mensaje or 'Operación completada correctamente.' }), 200 #'data': result_data
    except Exception as ex:
        # Cualquier otro error (de Python)
        mysql.connection.rollback()
        return jsonify({'status': False, 'mensaje': f'Error interno: {str(ex)}' }), 500
    finally:
        cur.close()
#--------------------------------------------------
@ministerios_bp.route('/estado_ministerio/<int:codigo>')
def estado_ministerio(codigo):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_estado_ministerio", (codigo, cod_usuario, ''))
         # Obtener el OUT param (mensaje)
        cur.execute("SELECT @p_mensaje;")
        mensaje = cur.fetchone()[0]
        cur.close()

        return jsonify({'status': True,'mensaje': mensaje or 'Operación completada correctamente.' }), 200 #'data': result_data
    except Exception as ex:
        # Cualquier otro error (de Python)
        mysql.connection.rollback()
        return jsonify({'status': False, 'mensaje': f'Error interno: {str(ex)}' }), 500
    finally:
        cur.close()
#--------------------------------------------------
@ministerios_bp.route('/nuevo_ministerio', methods=['POST'])
def nuevo_ministerio():
    cod_usuario = current_user.code
    codigo_ = request.form['valorCode']
    opcion = request.form['cboOpcion']
    nombre = request.form['txt_nombre']
    descripcion = request.form['txt_descripcion']
    funciones = request.form['txt_funciones']     
    estado = request.form.get('chck_estado', 'I') #I: inactivo

    # 👉 Aquí obtienes el archivo correctamente
    ruta_adjunto = request.files.get('ruta_archivo')
    
    if ruta_adjunto and ruta_adjunto.filename != '':
        filename = secure_filename(ruta_adjunto.filename)
        save_path = os.path.join('uploads', filename)   # carpeta donde guardarás
        ruta_adjunto.save(save_path)
        ruta_adjunto = save_path  # puedes guardar la ruta en BD
        
    if not codigo_:

        if not nombre:
            return jsonify({"error": "Ingrese el nombre del Ministerio."})
        elif not descripcion:
            return jsonify({"error": "Ingrese la descripción del ministerio."})
        else:
            try:
                cur = mysql.connection.cursor()
                cur.callproc('sp_reg_ministerio', (opcion, nombre, descripcion, funciones, ruta_adjunto, estado, cod_usuario, ''))
                # Si el procedimiento devuelve resultados
                #results = cur.fetchall()
                cur.execute("SELECT @p_mensaje;")
                mensaje = cur.fetchone()[0]
                cur.close()

                return jsonify({'mensaje': mensaje or 'Operación completada correctamente.'}), 200 #'data': result_data
            except Exception as ex:
                # Cualquier otro error (de Python)
                mysql.connection.rollback()
                return jsonify({'status': False, 'mensaje': f'Error interno: {str(ex)}' }), 500
            finally:
                cur.close()
    else:
        if not nombre:
            return jsonify({"error": "Ingrese el nombre del Ministerio."})
        elif not descripcion:
            return jsonify({"error": "Ingrese la descripción del ministerio."})        
        else:
            try:
                cur = mysql.connection.cursor()
                cur.callproc('sp_upd_ministerio', (codigo_, opcion, nombre, descripcion, funciones, ruta_adjunto, estado, cod_usuario, ''))
                # Si el procedimiento devuelve resultados
                #results = cur.fetchall()
                cur.execute("SELECT @p_mensaje;")
                mensaje = cur.fetchone()[0]
                cur.close()
                return jsonify({'mensaje': mensaje or 'Operación completada correctamente.'}), 200 #'data': result_data
            except Exception as ex:
                # Cualquier otro error (de Python)
                mysql.connection.rollback()
                return jsonify({'status': False, 'mensaje': f'Error interno: {str(ex)}' }), 500
            finally:
                cur.close()
#--------------------------------------------------


@ministerios_bp.route("/upload_file", methods=["POST"])
def upload_file():
    if "archivo" not in request.files:
        return jsonify({"mensaje": "No se envió ningún archivo"}), 400

    archivo = request.files["archivo"]
    if archivo.filename == "":
        return jsonify({"mensaje": "No se seleccionó ningún archivo"}), 400

    nombre_seguro = secure_filename(archivo.filename)
    ruta_destino = os.path.join(UPLOAD_FOLDER, nombre_seguro)
    archivo.save(ruta_destino)

    return jsonify({"mensaje": f"Archivo '{nombre_seguro}' subido correctamente ✅"})