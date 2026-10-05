"""
TiendaLab - Version CORREGIDA.

Misma funcionalidad que app.py pero con consultas PARAMETRIZADAS.
La entrada del usuario viaja como PARAMETRO, nunca como parte del texto
del SQL, por lo que ya no puede alterar la estructura de la consulta.

Nota de driver: pymssql usa el marcador %s (paramstyle 'pyformat').
Con pyodbc el marcador seria ? en lugar de %s.

Para probar la version segura, en docker-compose.yml cambia el CMD de la
imagen web a:  ["python", "app_seguro.py"]  (o renombra este archivo a
app.py) y reconstruye:  docker compose up -d --build web
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
    # Mismo modo transaccional que app.py, para que la unica diferencia
    # entre las dos versiones sea la parametrizacion de las consultas.
    return pymssql.connect(autocommit=True, **DBCFG)


PAGE = """
<!doctype html><html lang="es"><meta charset="utf-8">
<title>TiendaLab (SEGURA)</title>
<body style="font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;line-height:1.5">
<h1>TiendaLab (version segura)</h1>
<p style="background:#e8f5e9;color:#1b5e20;padding:.5rem .75rem;border-radius:6px">
  Consultas parametrizadas. Intenta las mismas inyecciones: ya no funcionan.</p>

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

    # ---- SEGURO: consulta parametrizada ----
    query = ("SELECT Id, Usuario, Rol FROM Usuarios "
             "WHERE Usuario = %s AND PasswordHash = %s")
    cx = get_conn()
    cur = cx.cursor()
    cur.execute(query, (usuario, password))
    fila = cur.fetchone()
    cx.close()
    # ----------------------------------------

    if fila:
        salida = (f"<p style='color:green'>Acceso concedido. "
                  f"Bienvenido <b>{fila[1]}</b> (rol: {fila[2]})</p>")
    else:
        salida = "<p style='color:#b00'>Usuario o contrasena invalidos</p>"
    return PAGE.format(resultado=salida)


@app.route("/buscar")
def buscar():
    q = request.args.get("q", "")

    # ---- SEGURO: consulta parametrizada (el comodin se arma en el parametro) ----
    query = "SELECT Nombre, Categoria, Precio FROM Productos WHERE Nombre LIKE %s"
    cx = get_conn()
    cur = cx.cursor()
    cur.execute(query, ("%" + q + "%",))
    filas = cur.fetchall()
    cx.close()
    # ---------------------------------------------------------------------------

    celdas = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in filas
    )
    salida = ("<table border='1' cellpadding='6'>"
              "<tr><th>Nombre</th><th>Categoria</th><th>Precio</th></tr>"
              f"{celdas}</table>")
    return PAGE.format(resultado=salida)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
