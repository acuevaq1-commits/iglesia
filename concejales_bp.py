from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import MySQLdb.cursors
import config
#from flask_mysqldb import MySQL
#from datetime import datetime

concejales_bp = Blueprint("concejal", __name__)
#--------------------------------Para autenticación
@concejales_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))  # o abort(401) si es API
#--------------------------------------------------
@concejales_bp.route('/detaconcejo', methods=['POST'])
def detaconcejo():
    codeConcejo = request.form['codeConcejo']
    nombreConcejo = request.form['nombreConcejo']
    ministerios = get_ministerios()
    responsables = get_responsable()
    apoyos = get_apoyo()    
    return render_template("detaconcejo.html", nombreConcejo= nombreConcejo, codeConcejo = codeConcejo, ministerios= ministerios, responsables = responsables, apoyos = apoyos)    
#--------------------------------------------------
@concejales_bp.route('/tblconcejales/<int:cboConcejo>', methods=['GET', 'POST'])
def tblconcejales(cboConcejo):
    tabla_concejales = get_deta_concejo(cboConcejo)
    return render_template("_detaconcejales.html", deta_concejos=tabla_concejales)
#--------------------------------------------------
def get_deta_concejo(codigo):
    cursor = mysql.connection.cursor()
    cursor.callproc('sp_deta_concejo', (codigo,))
    concejales_ = cursor.fetchall()
    return concejales_
#--------------------------------------------------
def get_concejos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, nombre FROM concejo")
    apoyo_ = cursor.fetchall()
    return apoyo_
#--------------------------------------------------
def get_ministerios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, nombre FROM ministerio")
    apoyo_ = cursor.fetchall()
    return apoyo_
#--------------------------------------------------
def get_responsable():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, nombres FROM persona")
    responsables_ = cursor.fetchall()
    return responsables_
#--------------------------------------------------
def get_apoyo():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, nombres FROM persona")
    apoyo_ = cursor.fetchall()
    return apoyo_
#--------------------------------------------------
@concejales_bp.route('/edit_concejal/<int:codigo>', methods=['GET', 'POST'])
def edit_concejal(codigo):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_concejal(%s)', (codigo,))  # <- tupla correcta

        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe el concejal'), 404

        return jsonify({            
            "concejo": row.get("concejo", ""),
            "ministerio": row.get("ministerio", ""),
            "responsable": row.get("responsable", ""),
            "apoyo": row.get("apoyo", ""),
            "inicio": row.get("inicio", ""), #.strftime("%Y-%m-%d"),
            "termino": row.get("termino", ""), #.strftime("%Y-%m-%d"),
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@concejales_bp.route('/eli_concejal/<int:codigo>')
def eli_concejal(codigo):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_concejal", (codigo, cod_usuario, ''))
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
@concejales_bp.route('/nuevo_concejal', methods=['POST'])
def nuevo_concejal():
    cod_usuario = current_user.code
    codigo_ = request.form['valorCode']
    concejo = request.form['cboConcejo_hidden']
    ministerio = request.form['cboMinisterio']
    responsable = request.form['cboResponsable']
    apoyo = request.form['cboApoyo']        
    inicio = request.form['txt_desde']
    termino = request.form['txt_hasta']
    if not codigo_:

        if not ministerio:
            return jsonify({"error": "Seleccione un ministerio."})
        elif not responsable:
            return jsonify({"error": "Seleccione un responsable."})
        elif not apoyo:
            return jsonify({"error": "Seleccione un apoyo."})
        elif not inicio:
            return jsonify({"error": "Ingrese la fecha de inicio."})
        elif not termino:
            return jsonify({"error": "Ingrese la fecha de termino."})
        else:            
            cur = mysql.connection.cursor()
            cur.callproc('sp_reg_concejal', (concejo, ministerio, responsable, apoyo, inicio, termino, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro guardado satisfactoriamente."})                   
            else:
                return jsonify({"error": "No se pudo registrar" + str(codigo_)})
    else:

        if not ministerio:
            return jsonify({"error": "Seleccione un ministerio."})
        elif not responsable:
            return jsonify({"error": "Seleccione un responsable."})
        elif not apoyo:
            return jsonify({"error": "Seleccione un apoyo."})
        elif not inicio:
            return jsonify({"error": "Ingrese la fecha de inicio."})
        elif not termino:
            return jsonify({"error": "Ingrese la fecha de termino."})
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_upd_concejal', (codigo_, concejo, ministerio, responsable, apoyo, inicio, termino, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})                   
            else:
                return jsonify({"error": "No se pudo registrar" + str(codigo_)})
