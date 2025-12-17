from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import config
import MySQLdb.cursors

usuarios_bp = Blueprint("usuario", __name__)
#--------------------------------Para autenticación
@usuarios_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))  # o abort(401) si es API

#--------------------------------------------------
@usuarios_bp.route('/lusuarios', methods=['GET'])
def lusuarios():
    tabla_usuarios = get_tabla_usuario()
    return render_template('usuarios.html', tabla = tabla_usuarios)
#--------------------------------------------------
@usuarios_bp.route('/tblusuarios')
def tblusuarios():
    tabla_usuarios = get_tabla_usuario()
    return render_template("_usuario.html", tabla=tabla_usuarios)
#--------------------------------------------------
def get_tabla_usuario():
    cursor = mysql.connection.cursor()
    cursor.callproc('sp_all_usuario')
    usuario_ = cursor.fetchall()    
    return usuario_
#--------------------------------------------------
@usuarios_bp.route('/edit_usuario/<int:codigo>', methods=['GET', 'POST'])
def edit_persona(codigo):
    try:
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('CALL sp_edi_usuario(%s)', (codigo,))  # <- tupla correcta

        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe el usuario'), 404

        return jsonify({
            "nombres":   row.get("nombres", ""),
            "apellidos": row.get("apellidos", ""),
            "email": row.get("email", ""),
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@usuarios_bp.route('/eli_usuario/<int:code>')
def eli_usuario(code):    
    cur = mysql.connection.cursor()
    try:
        cur.callproc("sp_eli_usuario", (code,))
        mysql.connection.commit()
        return jsonify({"status": "ok", "message": "✔ Registro eliminado correctamente"})
        #return jsonify(ok=True, deleted=code)
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@usuarios_bp.route('/nuevo_usuario', methods=['POST'])
def nuevo_usuario():
    codigo_ = request.form['valorCode']
    if not codigo_:
        nombres = request.form['txt_nombres']
        apellidos = request.form['txt_apellidos']
        email = request.form['txt_email']        
        
        if not nombres:
            return jsonify({"error": "Ingrese el nombre de la persona."})
        elif not apellidos:
            return jsonify({"error": "Ingrese los apellidos de la persona."})
        elif not email:
            return jsonify({"error": "Ingrese el email de la persona."})        
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_reg_usuario', (nombres, apellidos, email))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro guardado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo registrar ' + str(codigo_)
    else:
        nombres = request.form['txt_nombres']
        apellidos = request.form['txt_apellidos']
        email = request.form['txt_email']
        if not nombres:
            return jsonify({"error": "Ingrese el nombre de la persona."})
        elif not apellidos:
            return jsonify({"error": "Ingrese los apellidos de la persona."})
        elif not email:
            return jsonify({"error": "Ingrese el email de la persona."})        
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_upd_usuario', (codigo_, nombres, apellidos, email))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo actualizar ' + str(codigo_)

#--------------------------------------------------
@usuarios_bp.route('/tblhistorialUsu/<int:codigo>')
def tblhistorialUsu(codigo):
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_historial_usu", (codigo,))
        tabla_historial = cur.fetchall()
        cur.close()
        #return render_template("_usuhistorial.html", tablaHisto=tabla_historial)
        if tabla_historial:
            return render_template("_usuhistorial.html", tablaHisto=tabla_historial)           
        else:
            return render_template("_usuhistorial.html", tablaHisto=None) 
    except Exception as e:
        return f"Ocurrió un error: {str(e)}"

    #return render_template("_usuario.html", tablaHisto=tabla_historial)
#--------------------------------------------------
# def get_tabla_historialUsu():
#     cursor = mysql.connection.cursor()
#     cursor.callproc('sp_all_historialUsu')
#     historial_ = cursor.fetchall()    
#     return historial_