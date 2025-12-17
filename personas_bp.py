from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import MySQLdb.cursors
import config
#from flask_mysqldb import MySQL
#from datetime import datetime

personas_bp = Blueprint("persona", __name__)
#--------------------------------Para autenticación
@personas_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))  # o abort(401) si es API

#--------------------------------------------------
@personas_bp.route('/lpersonas', methods=['GET'])
def lpersonas():
    tabla_personas = get_tabla_persona()
    condicion = get_condicion()
    return render_template('personas.html', condiciones=condicion, persona = tabla_personas)
#--------------------------------------------------
@personas_bp.route('/tblpersonas')
def tblpersonas():    
    tabla_personas = get_tabla_persona()
    return render_template("_persona.html", persona=tabla_personas)
#--------------------------------------------------
def get_tabla_persona():
    cursor = mysql.connection.cursor()
    cursor.callproc('sp_all_persona')
    personas_ = cursor.fetchall()
    return personas_



#--------------------------------------------------
@personas_bp.route('/edit_persona/<int:codigo>', methods=['GET', 'POST'])
def edit_persona(codigo):
    try:        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_persona(%s)', (codigo,))  # <- tupla correcta

        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe la persona'), 404

        return jsonify({
            "nombres":   row.get("nombres", ""),
            "apellidos": row.get("apellidos", ""),
            "documento": row.get("documento", ""),
            "telefono":  row.get("telefono", ""),
            "direccion": row.get("direccion", ""),
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@personas_bp.route('/eli_persona/<int:codigo>')
def eli_persona(codigo):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_persona", (codigo, cod_usuario, ''))
        # Obtener el OUT param (mensaje)
        cur.execute("SELECT @p_mensaje;")
        mensaje = cur.fetchone()[0]
        cur.close()

        return jsonify({'status': True,'mensaje': mensaje or '✔ Operación completada correctamente.' }), 200 #'data': result_data
    except Exception as ex:
        # Cualquier otro error (de Python)
        mysql.connection.rollback()
        return jsonify({'status': False, 'mensaje': f'Error interno: {str(ex)}' }), 500
    finally:
        cur.close()
#--------------------------------------------------
@personas_bp.route('/nueva_persona', methods=['POST'])
def nueva_persona():
    cod_usuario = current_user.code
    codigo_ = request.form['valorCode']
    nombres = request.form['txt_nombres']
    apellidos = request.form['txt_apellidos']
    documento = request.form['txt_documento']
    telefono = request.form['txt_telefono']
    direccion = request.form['txt_direccion']
    nacimiento = request.form['fecNacimiento']
    sexo = request.form['cboSexo']
    estado_civil = request.form['cboEstadoCivil']
    grado = request.form['cboGradoAcademico']
    profesion = request.form['txt_profesion']
    correo = request.form['txt_Correo']
    condicion = request.form['cboCondicion']
    if not codigo_:
                
        if not nombres:
            return jsonify({"error": "Ingrese el nombre de la persona."})
        elif not apellidos:
            return jsonify({"error": "Ingrese los apellidos de la persona."})
        elif not documento:
            return jsonify({"error": "Ingrese el documento de la persona."})
        elif not nacimiento:
            return jsonify({"error": "Ingrese la fecha de Nacimiento."})        
        elif not sexo:
            return jsonify({"error": "Ingrese el sexo de la persona."})
        elif not telefono:
            return jsonify({"error": "Ingrese el teléfono de la persona."})
        elif not direccion:
            return jsonify({"error": "Ingrese la dirección de la persona."})
        elif not estado_civil:
            return jsonify({"error": "Ingrese el estado civil de la persona."})
        elif not grado:
            return jsonify({"error": "Ingrese la grado de la persona."})
        elif not profesion:
            return jsonify({"error": "Ingrese la profesión de la persona."})
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_reg_persona', (nombres, apellidos, documento, telefono, direccion, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro guardado satisfactoriamente."})             
            else:
                return jsonify({"error": "No se pudo registrar" + str(codigo_)})
    else:
        
        if not nombres:
            return jsonify({"error": "Ingrese el nombre de la persona."})
        elif not apellidos:
            return jsonify({"error": "Ingrese los apellidos de la persona."})
        elif not documento:
            return jsonify({"error": "Ingrese el número de documento."})
        elif not nacimiento:
            return jsonify({"error": "Ingrese la fecha de Nacimiento."})        
        elif not sexo:
            return jsonify({"error": "Ingrese el sexo de la persona."})
        elif not telefono:
            return jsonify({"error": "Ingrese el teléfono de la persona."})
        elif not direccion:
            return jsonify({"error": "Ingrese la dirección de la persona."})
        elif not estado_civil:
            return jsonify({"error": "Ingrese el estado civil de la persona."})
        elif not grado:
            return jsonify({"error": "Ingrese la grado de la persona."})
        elif not profesion:
            return jsonify({"error": "Ingrese la profesión de la persona."})
        elif not correo:
            return jsonify({"error": "Ingrese el correo de la persona."})
        elif not condicion:
            return jsonify({"error": "Ingrese la condición de la persona."})
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_upd_persona', (codigo_, nombres, apellidos, documento, nacimiento, sexo, telefono, direccion, estado_civil, grado, profesion, correo, condicion))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})                  
            else:
                return jsonify({"error": "No se pudo registrar" + str(codigo_)})
#--------------------------------------------------
def get_condicion():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, condicion FROM condicion")
    condicion_ = cursor.fetchall()
    return condicion_
