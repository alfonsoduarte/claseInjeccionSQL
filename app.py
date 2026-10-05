"""
TiendaLab - Aplicacion DELIBERADAMENTE VULNERABLE a inyeccion SQL.

Uso exclusivamente educativo y en entorno local aislado.
NO desplegar en Internet ni reutilizar este patron en produccion.

El login y la busqueda construyen el SQL concatenando directamente la
entrada del usuario -> inyeccion SQL. La pagina muestra el SQL ejecutado
y los errores para que el alumno vea exactamente como su entrada aterriza
en la consulta.
"""
import os

import pymssql
from flask import Flask, request

app = Flask(__name__)

DBCFG = dict(
    server=os.getenv("DB_HOST", "db"),
    user=os.getenv("DB_USER", "app_login"),
    password=os.getenv("DB_PASS", "App_Pass_123!"),
    database=os.getenv("DB_NAME", "TiendaLab"),
)


def get_conn():
    # autocommit=True para que las sentencias apiladas de la Practica C
    # (por ejemplo '; UPDATE Productos SET Precio = 0; --) dejen un efecto
    # visible y el alumno compruebe el impacto real del ataque.
    # OJO: el autocommit NO es un control de seguridad. Solo refleja el modo
    # transaccional en el que corre la aplicacion. Sin el, pymssql abre una
    # transaccion implicita y el cierre de la conexion la revierte, con lo
    # que el ataque se ejecutaria pero no persistiria.
    return pymssql.connect(autocommit=True, **DBCFG)


PAGE = """
<!doctype html><html lang="es"><meta charset="utf-8">
<title>TiendaLab (VULNERABLE)</title>
<body style="font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;line-height:1.5">
<h1>TiendaLab</h1>
<p style="background:#fdecea;color:#b00;padding:.5rem .75rem;border-radius:6px">
  Aplicacion deliberadamente vulnerable. Solo uso educativo y local.</p>

<h2>Login</h2>
<form method="post" action="/login">
  Usuario: <input name="usuario"><br><br>
  Password: <input name="password" type="text"><br><br>
  <button>Entrar</button>
</form>

<h2>Buscar producto</h2>
<form method="get" action="/buscar">
  <input name="q" placeholder="nombre del producto" size="40">
  <button>Buscar</button>
</form>

{resultado}
</body></html>
"""


@app.route("/")
def home():
    return PAGE.format(resultado="")


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario", "")
    password = request.form.get("password", "")

    # ---- VULNERABLE: concatenacion directa de la entrada del usuario ----
    query = (
        "SELECT Id, Usuario, Rol FROM Usuarios "
        f"WHERE Usuario = '{usuario}' AND PasswordHash = '{password}'"
    )
    # --------------------------------------------------------------------

    try:
        cx = get_conn()
        cur = cx.cursor()
        cur.execute(query)
        fila = cur.fetchone()
        cx.close()
    except Exception as e:
        return PAGE.format(
            resultado=f"<pre style='color:#b00;white-space:pre-wrap'>"
                      f"SQL ejecutado:\n{query}\n\nError:\n{e}</pre>")

    if fila:
        salida = (f"<p style='color:green'>Acceso concedido. "
                  f"Bienvenido <b>{fila[1]}</b> (rol: {fila[2]})</p>")
    else:
        salida = "<p style='color:#b00'>Usuario o contrasena invalidos</p>"

    return PAGE.format(resultado=f"{salida}<pre style='white-space:pre-wrap'>"
                                 f"SQL ejecutado:\n{query}</pre>")


@app.route("/buscar")
def buscar():
    q = request.args.get("q", "")

    # ---- VULNERABLE: concatenacion directa de la entrada del usuario ----
    query = f"SELECT Nombre, Categoria, Precio FROM Productos WHERE Nombre LIKE '%{q}%'"
    # --------------------------------------------------------------------

    try:
        cx = get_conn()
        cur = cx.cursor()
        cur.execute(query)
        filas = cur.fetchall()
        cx.close()
    except Exception as e:
        return PAGE.format(
            resultado=f"<pre style='color:#b00;white-space:pre-wrap'>"
                      f"SQL ejecutado:\n{query}\n\nError:\n{e}</pre>")

    celdas = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in filas
    )
    salida = ("<table border='1' cellpadding='6'>"
              "<tr><th>Nombre</th><th>Categoria</th><th>Precio</th></tr>"
              f"{celdas}</table>")

    return PAGE.format(resultado=f"{salida}<pre style='white-space:pre-wrap'>"
                                 f"SQL ejecutado:\n{query}</pre>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
