from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import config
import MySQLdb.cursors

aportes_bp = Blueprint("aporte", __name__)
#--------------------------------Para autenticación
@aportes_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))  # o abort(401) si es API

#--------------------------------------------------
def get_personas():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, nombres FROM persona")
    personas_ = cursor.fetchall()
    return personas_
#--------------------------------------------------
def get_tipoaporte():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, tipo FROM tipoaporte")
    personas_ = cursor.fetchall()
    return personas_
#--------------------------------------------------
@aportes_bp.route('/laportes', methods=['GET'])
def laportes():
    tabla_aportes = get_tabla_aportes(1)
    personas = get_personas()
    tipoaporte = get_tipoaporte()
    return render_template('aportes.html', tablaAporte = tabla_aportes, listaPersona = personas, listatipoaporte= tipoaporte)
#--------------------------------------------------
@aportes_bp.route('/tblaportes/<int:tipo>')
def tblaportes(tipo):
    tabla_aportes = get_tabla_aportes(tipo)
    return render_template("_aporte.html", tablaAporte = tabla_aportes)
#--------------------------------------------------
def get_tabla_aportes(tipo):
    cursor = mysql.connection.cursor()
    cursor.callproc("sp_aportes_filtro", (tipo,))
    aporte_ = cursor.fetchall()    
    return aporte_
#--------------------------------------------------
@aportes_bp.route('/edit_aporte/<int:codigo>', methods=['GET', 'POST'])
def edit_responsabilidad(codigo):
    try:        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_aporte(%s)', (codigo,))  # <- tupla correcta

        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe el usuario'), 404

        return jsonify({
            "aporte": row.get("aporte", ""),
            "fecha":   row.get("fecha", ""),            
            "turno":   row.get("turno", ""),
            "monto": row.get("monto", ""),
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@aportes_bp.route('/eli_aporte/<int:code>')
def eli_aporte(code):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_aporte", (code, cod_usuario, ''))
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
# #--------------------------------------------------
# @aportes_bp.route('/nuevo_aporte', methods=['POST'])
# def nueva_responsabilidad():
#     codigo_ = request.form['valorCode']
#     if not codigo_:
#         fecha = request.form['fecha_txt']
#         turno = request.form['cboTurno']
#         dirigente = request.form['cboDirigente']
#         ujier = request.form['cboUjier']
        
#         if not fecha:
#             return jsonify({"error": "Ingrese efecha."})
#         elif not turno:
#             return jsonify({"error": "Ingrese turno."})
#         elif not dirigente:
#             return jsonify({"error": "Ingrese dirigente."})
#         elif not ujier:
#             return jsonify({"error": "Ingrese ujier."})        
#         else:
#             cur = mysql.connection.cursor()
#             cur.callproc('sp_reg_responsabilidad', (fecha, turno, dirigente, ujier))
#             # Si el procedimiento devuelve resultados
#             results = cur.fetchall()
#             cur.close()
#             if results:
#                 return jsonify({"success": "✔ Registro guardado satisfactoriamente."})
#                 #flash("✔ Registro guardado satisfactoriamente.", "success")                     
#             else:
#                 return 'No se pudo registrar ' + str(codigo_)
#     else:
#         nombres = request.form['txt_nombres']
#         apellidos = request.form['txt_apellidos']
#         email = request.form['txt_email']
#         if not nombres:
#             return jsonify({"error": "Ingrese el nombre de la persona."})
#         elif not apellidos:
#             return jsonify({"error": "Ingrese los apellidos de la persona."})
#         elif not email:
#             return jsonify({"error": "Ingrese el email de la persona."})        
#         else:
#             cur = mysql.connection.cursor()
#             cur.callproc('sp_upd_responsabilidad', (codigo_, fecha, turno, dirigente, ujier))
#             # Si el procedimiento devuelve resultados
#             results = cur.fetchall()
#             cur.close()
#             if results:
#                 return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})
#                 #flash("✔ Registro guardado satisfactoriamente.", "success")                     
#             else:
#                 return 'No se pudo actualizar ' + str(codigo_)
#--------------------------------------------------