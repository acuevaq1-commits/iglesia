from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import config
import MySQLdb.cursors

tipoaporte_bp = Blueprint("tipoaporte", __name__)
#--------------------------------Para autenticación
@tipoaporte_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
#--------------------------------------------------
@tipoaporte_bp.route('/ltaportes', methods=['GET'])
def ltaportes():
    tabla_taportes = get_tabla_taportes()    
    return render_template('taportes.html', tablaTaportes = tabla_taportes)
#--------------------------------------------------
@tipoaporte_bp.route('/tbltaportes')
def tbltaportes():
    tabla_taportes = get_tabla_taportes()
    return render_template("_taportes.html", tablaTaportes = tabla_taportes)
#--------------------------------------------------
def get_tabla_taportes():
    cursor = mysql.connection.cursor()
    cursor.callproc("sp_all_taportes")
    tbienes_ = cursor.fetchall()
    return tbienes_
#--------------------------------------------------
@tipoaporte_bp.route('/edit_tipoaporte/<int:codigo>', methods=['GET', 'POST'])
def edit_tipoaporte(codigo):
    try:        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_tipoaporte(%s)', (codigo,))  # <- tupla correcta

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
@tipoaporte_bp.route('/eli_tipoaporte/<int:code>')
def eli_tipoaporte(code):
    cod_usuario = current_user.code    
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_tipoaporte", (code,cod_usuario, ''))
        mysql.connection.commit()
        return jsonify({"status": "ok", "message": "✔ Registro eliminado correctamente"})
        #return jsonify(ok=True, deleted=code)
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@tipoaporte_bp.route('/nuevo_tipoaporte', methods=['POST'])
def nuevo_tipoaporte():    
    codigo_ = request.form['valorCode']
    tipo = request.form['txt_tipo']
    descripcion = request.form['txt_descripcion']
    cod_usuario = current_user.code
    if not codigo_:

        if not tipo:
            return jsonify({"error": "Ingrese tipo de aporte."})
        elif not descripcion:
            return jsonify({"error": "Ingrese descripcionl del tipo."}) 
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_reg_tipoaporte', (tipo, descripcion, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro guardado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'aNo se pudo registrar ' + str(codigo_)
    else:
                
        if not tipo:
            return jsonify({"error": "Ingrese tipo de aporte."})
        elif not descripcion:
            return jsonify({"error": "Ingrese descripcion del tipo."})        
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_upd_tipoaporte', (codigo_, tipo, descripcion, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo actualizar ' + str(codigo_)