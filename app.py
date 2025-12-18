from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from personas_bp import personas_bp #para personas.py
from usuarios_bp import usuarios_bp #para personas.py
from responsabilidades_bp import responsabilidades_bp #para personas.py
from ministerios_bp import ministerios_bp #para personas.py
from aportes_bp import aportes_bp #para aportes.py
from concejos_bp import concejos_bp #para concejos.py
from concejales_bp import concejales_bp #para concejales.py
from tbienes_bp import tipobien_bp #para tipobien.py
from taportes_bp import tipoaporte_bp #para tipobien.py
from condicion_bp import condicion_bp #
from extensions import mysql
from datetime import datetime
import config

app = Flask(__name__)

app.config['SECRET_KEY'] = config.HEX_SEC_KEY
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql.init_app(app)

app.register_blueprint(personas_bp) #para personas_bp.py
app.register_blueprint(usuarios_bp) #para usuarios_bp.py
app.register_blueprint(responsabilidades_bp) #para responsabilidades_bp.py
app.register_blueprint(ministerios_bp) #para ministerios_bp.py
app.register_blueprint(aportes_bp) #para aportes_bp.py
app.register_blueprint(concejos_bp) #para concejos_bp.py
app.register_blueprint(concejales_bp) #para concejales_bp.py
app.register_blueprint(tipobien_bp) #para tipobien_bp.py
app.register_blueprint(tipoaporte_bp) #para tipoaporte_bp.py
app.register_blueprint(condicion_bp) #para condicion_bp.py

# ---------------- CONFIGURAR FLASK-LOGIN ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"   # si no hay sesión, redirige a /login

#--------------------------------------------------
class User(UserMixin):
    def __init__(self, name, surnames, email, code): #password
        self.name = name
        self.surnames = surnames
        self.email = email
        self.code = code        
    # Flask-Login llamará a esto para almacenar el “ID” en la sesión
    def get_id(self):
        return self.email
#--------------------------------------------------
@login_manager.user_loader
def load_user(email: str):
    cur = mysql.connection.cursor()
    # Ajusta columnas/orden a tu tabla real
    cur.execute("SELECT name, surnames, email, code FROM usuario WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close()
    if row:
        return User(row[0], row[1], row[2], row[3])
    return None
#--------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('persona.lpersonas'))
    return render_template('index.html')

#--------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('persona.lpersonas'))
        return render_template('index.html')        

    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT name, surnames, email, password, code FROM usuario WHERE email = %s AND password = %s", (email, password))
    row = cur.fetchone()
    cur.close()

    if row is not None:
        user = User(row[0], row[1], row[2], row[3])
        login_user(user)  # <-- esto marca current_user.is_authenticated = True

        return redirect(url_for('persona.lpersonas'))
    else:
        return render_template('index.html', message="Las credenciales no son correctas")

#--------------------------------------------------
@app.route("/logout")
@login_required  # 👈 obliga a tener sesión activa
def logout():
    logout_user()  # Cierra la sesión del usuario
    #return redirect(url_for("/"))
    return render_template('index.html')
#--------------------------------------------------
@app.route('/responsabilidades')
@login_required  # 👈 obliga a tener sesión activa
def responsabilidades():
    dirigentes = get_dirigentes()
    ujieres = get_ujieres()
    lecturas = get_lecturas()
    predicadores = get_predicadores()
    limpiadores = get_limpiadores()
    santacena = get_santacena()
    comensales = get_comensales()
    return render_template('responsabilidades.html', dirigentes=dirigentes, ujieres = ujieres, lecturas = lecturas, Predicadores = predicadores, Limpiadores = limpiadores, SantaCena = santacena, Comensales= comensales)
#--------------------------------------------------
def get_dirigentes():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, concat(nombres, ' ', apellidos) nombre FROM persona")
    dirigentes_ = cursor.fetchall()
    return dirigentes_
#--------------------------------------------------
def get_ujieres():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, concat(nombres, ' ', apellidos) nombre FROM persona")
    ujieres_ = cursor.fetchall()
    return ujieres_
#--------------------------------------------------
def get_lecturas():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, concat(nombres, ' ', apellidos) nombre FROM persona")
    lecturas_ = cursor.fetchall()
    return lecturas_
#--------------------------------------------------
def get_predicadores():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, concat(nombres, ' ', apellidos) nombre FROM persona")
    predicadores_ = cursor.fetchall()
    return predicadores_
#--------------------------------------------------
def get_limpiadores():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, concat(nombres, ' ', apellidos) nombre FROM persona")
    limpiadores_ = cursor.fetchall()
    return limpiadores_
#--------------------------------------------------
def get_santacena():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, concat(nombres, ' ', apellidos) nombre FROM persona")
    santacena_ = cursor.fetchall()
    return santacena_
#--------------------------------------------------
def get_comensales():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT code, concat(nombres, ' ', apellidos) nombre FROM persona")
    comensales_ = cursor.fetchall()
    return comensales_

#--------------------------------------------------
def get_client_ip():
    # Respeta proxies/Nginx si usas X-Forwarded-For
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr
#--------------------------------------------------
@app.errorhandler(404)
def handle_404(e):

    # Ignora rutas ruidosas
    if request.path.startswith('/static/') or request.path == '/favicon.ico':
        # Opcional: no registres, solo responde
        return render_template('index.html'), 404  # o redirect(url_for('login'))

    path = request.path
    method = request.method
    ip = get_client_ip()
    ua = request.headers.get('User-Agent', '')[:512]  # evita textos muy largos
    email = current_user.email if getattr(current_user, 'is_authenticated', False) else None
    print(path)
    print(method)
    print(ip)
    print(ua)
    print(email)
    try:
        cur = mysql.connection.cursor()
        # Llama a tu SP (ajusta nombre/tipos/longitudes según tu BD)
        cur.callproc('sp_reg_intento_ruta_invalida', (path, method, ip, ua, email))
        mysql.connection.commit()
        cur.close()
    except Exception as ex:
        # No rompas el flujo si el log falla
        app.logger.exception(f"Error registrando 404 de {path}: {ex}")

    # Redirige al "index": en tu app, /login (GET) muestra index.html
    return redirect(url_for('login'))
#--------------------------------------------------
@app.errorhandler(405)
def handle_405(e):
    # (opcional) registrar similar al 404
    return redirect(url_for('login'))
#--------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)