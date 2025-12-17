from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import config
import MySQLdb.cursors

condicion_bp = Blueprint("condicion", __name__)
#--------------------------------Para autenticación
@condicion_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
#--------------------------------------------------
@condicion_bp.route('/lcondicion', methods=['GET'])
def lcondicion():
    tabla_condicion = get_tabla_tcondicion()    
    return render_template('condicion.html', tablaCondiciones = tabla_condicion)
#--------------------------------------------------
@condicion_bp.route('/tblcondiciones')
def tblcondiciones():
    tabla_condicion = get_tabla_tcondicion()
    return render_template("_tcondicion.html", tablaCondiciones = tabla_condicion)
#--------------------------------------------------
def get_tabla_tcondicion():
    cursor = mysql.connection.cursor()
    cursor.callproc("sp_all_condiciones")
    tbienes_ = cursor.fetchall()
    return tbienes_
#--------------------------------------------------
@condicion_bp.route('/edit_condicion/<int:codigo>', methods=['GET', 'POST'])
def edit_condicion(codigo):
    try:        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_condicion(%s)', (codigo,))  # <- tupla correcta

        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe el tipo de bien'), 404

        return jsonify({
            "tipo": row.get("tipo", ""),
            "descripcion":   row.get("descripcion", ""),            
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@condicion_bp.route('/eli_condicion/<int:code>')
def eli_condicion(code):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_condicion", (code, cod_usuario, ''))
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
@condicion_bp.route('/nueva_condicion', methods=['POST'])
def nueva_condicion():
    codigo_ = request.form['valorCode']
    tipo = request.form['txt_tipo']
    descripcion = request.form['txt_descripcion']
    cod_usuario = current_user.code
    if not codigo_:

        if not tipo:
            return jsonify({"error": "Ingrese tipo."})
        elif not descripcion:
            return jsonify({"error": "Ingrese descripcion."}) 
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_reg_condicion', (tipo, descripcion, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro guardado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo registrar ' + str(codigo_)
    else:
                
        if not tipo:
            return jsonify({"error": "Ingrese tipo."})
        elif not descripcion:
            return jsonify({"error": "Ingrese descripcion."})        
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_upd_condicion', (codigo_, tipo, descripcion, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo actualizar ' + str(codigo_)