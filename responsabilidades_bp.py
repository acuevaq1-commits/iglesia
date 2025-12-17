from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user
from flask import Blueprint #
from extensions import mysql
import config
import MySQLdb.cursors

responsabilidades_bp = Blueprint("responsabilidad", __name__)
#--------------------------------Para autenticación
@responsabilidades_bp.before_request
def require_login_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))  # o abort(401) si es API

#--------------------------------------------------
@responsabilidades_bp.route('/lresponsabilidades', methods=['GET'])
def lresponsabilidades():
    tabla_responsabilidades = get_tabla_responsabilidad()
    return render_template('responsabilidades.html', tabla_Respo = tabla_responsabilidades)
#--------------------------------------------------
@responsabilidades_bp.route('/tblresponsabilidades')
def tblresponsabilidades():
    tabla_responsabilidades = get_tabla_responsabilidad()
    return render_template("_responsabilidad.html", tablaRespo=tabla_responsabilidades)
#--------------------------------------------------
def get_tabla_responsabilidad():
    cursor = mysql.connection.cursor()
    cursor.callproc('sp_all_responsabilidad')
    responsabilidad_ = cursor.fetchall()    
    return responsabilidad_
#--------------------------------------------------
@responsabilidades_bp.route('/edit_responsabilidad/<int:codigo>', methods=['GET', 'POST'])
def edit_responsabilidad(codigo):
    try:        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)        
        cur.callproc("sp_edi_responsabilidad", (codigo,))
        row = cur.fetchone()
        if not row:
            return jsonify(ok=False, error='No existe el usuario'), 404

        return jsonify({
            "fecha":   row.get("fecha", ""),
            "turno":   row.get("turno", ""),
            "dirigente":   row.get("dirigente", ""),
            "ujier": row.get("ujier", ""),            
            "lectura": row.get("lectura", ""),
            "enseñanza": row.get("enseñanza", ""),
            "limpieza": row.get("limpieza", ""),
            "santacena": row.get("santacena", ""),
            "comensales": row.get("comensales", ""),
            "ok": True
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(ok=False, error=str(e)), 500
    finally:
        cur.close()
#--------------------------------------------------
@responsabilidades_bp.route('/eli_responsabilidad/<int:code>')
def eli_responsabilidad(code):
    cod_usuario = current_user.code    
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_eli_responsabilidad", (code, cod_usuario, ''))
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
@responsabilidades_bp.route('/nueva_responsabilidad', methods=['POST'])
def nueva_responsabilidad():
    cod_usuario = current_user.code
    codigo_ = request.form['valorCode']
    fecha = request.form['fecha_txt']
    turno = request.form['cboTurno']
    dirigente = request.form['cboDirigente']
    ujier = request.form['cboUjier']
    lectura = request.form['cboLectura']
    predicador = request.form['cboPredicador']
    limpieza = request.form['cboLimpieza']
    santacena = request.form['cboSantaCena']
    comensales = request.form['cboComensales']
    if not codigo_:
                
        if not fecha:
            return jsonify({"error": "Ingrese efecha."})
        elif not turno:
            return jsonify({"error": "Ingrese turno."})
        elif not dirigente:
            return jsonify({"error": "Ingrese dirigente."})
        elif not ujier:
            return jsonify({"error": "Ingrese ujier."})
        elif not lectura:
            return jsonify({"error": "Ingrese lectura"})
        elif not predicador:
            return jsonify({"error": "Ingrese predicador."})
        elif not limpieza:
            return jsonify({"error": "Ingrese limpieza."})
        elif not santacena:
            return jsonify({"error": "Ingrese santacena."})
        elif not comensales:
            return jsonify({"error": "Ingrese ecomensales."})
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_reg_responsabilidad', (fecha, turno, dirigente, ujier, lectura, predicador, limpieza, santacena, comensales, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro guardado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo registrar ' + str(codigo_)
    else:
        if not fecha:
            return jsonify({"error": "Ingrese efecha."})
        elif not turno:
            return jsonify({"error": "Ingrese turno."})
        elif not dirigente:
            return jsonify({"error": "Ingrese dirigente."})
        elif not ujier:
            return jsonify({"error": "Ingrese ujier."})
        elif not lectura:
            return jsonify({"error": "Ingrese lectura"})
        elif not predicador:
            return jsonify({"error": "Ingrese predicador."})
        elif not limpieza:
            return jsonify({"error": "Ingrese limpieza."})
        elif not santacena:
            return jsonify({"error": "Ingrese santacena."})
        elif not comensales:
            return jsonify({"error": "Ingrese ecomensales."})
        else:
            cur = mysql.connection.cursor()
            cur.callproc('sp_upd_responsabilidad', (codigo_, fecha, turno, dirigente, ujier, lectura, predicador, limpieza, santacena, comensales, cod_usuario))
            # Si el procedimiento devuelve resultados
            results = cur.fetchall()
            cur.close()
            if results:
                return jsonify({"success": "✔ Registro Actualizado satisfactoriamente."})
                #flash("✔ Registro guardado satisfactoriamente.", "success")                     
            else:
                return 'No se pudo actualizar ' + str(codigo_)

#--------------------------------------------------
@responsabilidades_bp.route('/tblCambiosRespo/<int:codigo>')
def tblhistorialUsu(codigo):
    try:
        cur = mysql.connection.cursor()
        cur.callproc("sp_cambios_respo", (codigo,))
        tabla_respohistorial = cur.fetchall()
        cur.close()
        #return render_template("_usuhistorial.html", tablaHisto=tabla_historial)
        if tabla_respohistorial:
            return render_template("_respohistorial.html", tablaRespoHisto=tabla_respohistorial)           
        else:
            return render_template("_respohistorial.html", tablaRespoHisto=None) 
    except Exception as e:
        return f"Ocurrió un error: {str(e)}"
#--------------------------------------------------