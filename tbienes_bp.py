from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import config
import MySQLdb.cursors

tipobien_bp = Blueprint("tipobien", __name__)
#--------------------------------Para autenticación
@tipobien_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
#--------------------------------------------------
@tipobien_bp.route('/ltbienes', methods=['GET'])
def ltbienes():
    tabla_tbienes = get_tabla_tbienes()    
    return render_template('tbienes.html', tablaTbienes = tabla_tbienes)
#--------------------------------------------------
@tipobien_bp.route('/tbltbienes')
def tbltbienes():
    tabla_tbienes = get_tabla_tbienes()
    return render_template("_tbienes.html", tablaTbienes = tabla_tbienes)
#--------------------------------------------------
def get_tabla_tbienes():
    cursor = mysql.connection.cursor()
    cursor.callproc("sp_all_tbienes")
    tbienes_ = cursor.fetchall()
    return tbienes_
#--------------------------------------------------
@tipobien_bp.route('/edit_tipobien/<int:codigo>', methods=['GET', 'POST'])
def edit_tipobien(codigo):
    try:        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_tipobien(%s)', (codigo,))  # <- tupla correcta

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
@tipobien_bp.route('/eli_tipobien/<int:code>')
def eli_tipobien(code):
    cod_usuario = current_user.code
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_tipobien", (code, cod_usuario, ''))
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
@tipobien_bp.route('/nuevo_tipobien', methods=['POST'])
def nuevo_tipobien():
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
            cur.callproc('sp_reg_tipobien', (tipo, descripcion, cod_usuario))
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
            cur.callproc('sp_upd_tipobien', (codigo_, tipo, descripcion, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo actualizar ' + str(codigo_)