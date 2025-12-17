from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import MySQLdb.cursors
import config
#from flask_mysqldb import MySQL
#from datetime import datetime

concejos_bp = Blueprint("concejo", __name__)
#--------------------------------Para autenticación
@concejos_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))  # o abort(401) si es API

#--------------------------------------------------
@concejos_bp.route('/lconcejos', methods=['GET'])
def lconcejos():
    tabla_concejos = get_tabla_concejo()
    return render_template('concejo.html', concejos = tabla_concejos)
#--------------------------------------------------
@concejos_bp.route('/tblconcejos')
def tblconcejos():
    tabla_concejos = get_tabla_concejo()
    return render_template("_concejo.html", concejos= tabla_concejos)
#--------------------------------------------------
def get_tabla_concejo():
    cursor = mysql.connection.cursor()
    cursor.callproc('sp_all_concejo')
    concejos = cursor.fetchall()
    return concejos
#--------------------------------------------------
@concejos_bp.route('/edit_concejo/<int:codigo>', methods=['GET', 'POST'])
def edit_concejo(codigo):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_concejo(%s)', (codigo,))  # <- tupla correcta

        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe el concejo'), 404

        return jsonify({            
            "nombre": row.get("nombre", ""),
            "descripcion": row.get("descripcion", ""),
            "inicio": row.get("inicio", "").strftime("%Y-%m-%d"),
            "termino": row.get("termino", "").strftime("%Y-%m-%d"),
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@concejos_bp.route('/eli_concejo/<int:codigo>')
def eli_concejo(codigo):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_concejo", (codigo, cod_usuario, ''))
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
@concejos_bp.route('/nuevo_concejo', methods=['POST'])
def nuevo_concejo():
    cod_usuario = current_user.code
    codigo_ = request.form['valorCode']
    concejo = request.form['txt_concejo']
    descripcion = request.form['txt_descripcion']
    inicio = request.form['txt_inicio']
    termino = request.form['txt_termino']
    if not codigo_:
        if not concejo:
            return jsonify({"error": "Ingrese el nombre del concejo."})
        elif not descripcion:
            return jsonify({"error": "Ingrese la descripción del concejo."})
        elif not inicio:
            return jsonify({"error": "Ingrese el inicio del concejo."})
        elif not termino:
            return jsonify({"error": "Ingrese el termino del concejo."})
        else:            
            cur = mysql.connection.cursor()
            cur.callproc('sp_reg_concejo', (concejo, descripcion, inicio, termino, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro guardado satisfactoriamente."})                   
            else:
                return 'No se pudo registrar ' + str(codigo_)
    else:
        if not concejo:
            return jsonify({"error": "Ingrese el nombre del concejo."})
        elif not descripcion:
            return jsonify({"error": "Ingrese la descripción del concejo."})
        elif not inicio:
            return jsonify({"error": "Ingrese la descripción del concejo."})
        elif not termino:
            return jsonify({"error": "Ingrese la descripción del concejo."})
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_upd_concejo', (codigo_, concejo, descripcion, inicio, termino, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})                   
            else:
                return 'No se pudo actualizar ' + str(codigo_)
#--------------------------------------------------
# @concejos_bp.route('/detaconcejo', methods=['POST'])
# def detaconcejo():
#     codigo_ = request.form['codigo']
#     deta_concejos = get_deta_concejo(codigo_)
#     responsables = get_responsable()
#     apoyos = get_apoyo()
#     ministerios = get_ministerios()
#     return render_template("detaconcejo.html", concejales=deta_concejos, responsables = responsables, apoyos = apoyos, ministerios= ministerios)    
# #--------------------------------------------------
# def get_deta_concejo(codigo):
#     cursor = mysql.connection.cursor()
#     cursor.callproc('sp_deta_concejo', (codigo))
#     concejales_ = cursor.fetchall()
#     return concejales_
# #--------------------------------------------------
# def get_responsable():
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT code, nombres FROM persona")
#     responsables_ = cursor.fetchall()
#     return responsables_
# #--------------------------------------------------
# def get_apoyo():
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT code, nombres FROM persona")
#     apoyo_ = cursor.fetchall()
#     return apoyo_
# #--------------------------------------------------
# def get_ministerios():
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT code, nombre, descripcion FROM ministerio")
#     apoyo_ = cursor.fetchall()
#     return apoyo_