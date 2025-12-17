@app.before_request
def verificar_sesion():
    # Si no está logueado y quiere entrar a algo distinto de index o login → redirigir
    if "usuario" not in session and request.endpoint not in ("index", "login"):
        return redirect(url_for("index"))