# Instrucciones del laboratorio — TiendaLab (Inyección SQL)

**Materia:** Ingeniería en Seguridad Informática y Redes (ISIR) — UAdeO
**Entorno:** SQL Server 2025 + app Flask vulnerable, todo dentro de Docker, en tu máquina.

> Este laboratorio es **tuyo y está aislado**. Atacar sistemas de terceros sin
> autorización por escrito es un delito (Código Penal Federal, arts. 211 bis).
> Acá se practica para **aprender a defender**.

---

## 1. Antes de la clase

- **Docker Desktop instalado y abierto.** No alcanza con tenerlo instalado: si
  no está corriendo, nada de lo que sigue funciona. En Windows, con backend WSL2.
- **`git`**, o bajarte el ZIP desde GitHub: *Code → Download ZIP*.
- **2 GB libres** en disco.
- **Internet la primera vez.** El primer arranque descarga las imágenes
  (≈1.9 GB, ver sección 2). Se hace una sola vez.

No hay que instalar SQL Server, Python ni nada más: todo vive dentro de los
contenedores.

---

## 2. Montaje

```bash
git clone https://github.com/alfonsoduarte/claseInjeccionSQL.git
cd claseInjeccionSQL
docker compose up -d --build
```

**El comando tiene que salir desde la carpeta que contiene `docker-compose.yml`.**
Si ves `no configuration file provided: not found`, estás parado en otra carpeta.

La primera vez, el `--build` descarga las imágenes:

| Imagen | Tamaño |
|---|---|
| SQL Server 2025 (`db`, `init`) | 1.75 GB |
| Python 3.12 (`web`) | 150 MB |

Eso tarda **entre 5 y 15 minutos** según la conexión. No está colgado: está
descargando. Las próximas veces arranca en segundos.

### Qué levanta

- `db` → SQL Server 2025, escuchando solo en `127.0.0.1:1433`
- `init` → siembra la base `TiendaLab` y **termina** (servicio de un solo uso)
- `web` → la app, en <http://localhost:8000>

No hay que esperar ni recargar a mano. `db` publica un `healthcheck`, `init`
arranca recién cuando SQL Server acepta conexiones, y `web` arranca recién
cuando `init` terminó bien. Si algo falla, Compose lo detiene en vez de dejarte
una web que no conecta.

---

## 3. Punto de control — no sigas hasta que se cumpla

**a) El sembrado terminó:**

```bash
docker compose logs init
```

La última línea tiene que decir `TiendaLab inicializada correctamente.`

**b) Los contenedores están donde tienen que estar:**

```bash
docker compose ps -a
```

`db` y `web` en `running`, `init` como `Exited (0)`. Un `init` en `Exited (1)`
significa que el sembrado falló: mirá `docker compose logs init`.

**c) La app responde:** abrí <http://localhost:8000>

Tenés que ver el título **TiendaLab** con un cartel rojo que dice
*Aplicacion deliberadamente vulnerable*, y la pestaña del navegador tiene que
decir **`TiendaLab (VULNERABLE)`**.

Si esas tres cosas están, el laboratorio quedó montado. Si no, ver sección 5.

---

## 4. Reglas de la sesión

- **Es local.** Se abre en <http://localhost:8000>, desde tu máquina, y no se
  comparte ni se publica. La app es inyectable a propósito, muestra el SQL y los
  errores del motor, y **escribe de verdad** en la base.
- **No la expongas a la red.** Si necesitás publicarla para un ejercicio
  supervisado, se hace a propósito y se cierra después (ver `README.md`).
  Verificá siempre con `docker compose config | grep host_ip`: tiene que decir
  `127.0.0.1`.
- **No crees un archivo `.env`** en la carpeta del laboratorio. Persiste entre
  terminales y reinicios, y cambia el comportamiento sin que te des cuenta.
- **Escribí las comillas a mano, en el teclado.** Las comillas, el `--` y el `%`
  tienen que ser **ASCII**, no tipográficos. Si copiás un payload desde Word,
  Notas o un PDF, la comilla llega como `'` en lugar de `'` y **la inyección no
  rompe nada**: el motor la trata como texto literal. Vas a creer que el ataque
  no funciona cuando el problema es la comilla. Es el error que más tiempo
  cuesta en clase.
- **En Windows la sintaxis de las variables es distinta** (PowerShell, no bash):

  ```powershell
  $env:APP_FILE = "app_seguro.py"; docker compose up -d web
  ```

  Y a diferencia de macOS/Linux, **la variable queda puesta en la sesión**: para
  volver atrás hay que resetearla explícitamente.

- **El guion de la clase no es material de esta sesión.** El archivo
  `clase-sql-injection-isir.md` trae la teoría, los payloads y las respuestas de
  análisis. Si lo abrís antes de tiempo te salteás el paso donde se entiende la
  **causa**, y terminás memorizando un truco en lugar de aprender a defender. Se
  abre al final, para contrastar lo que hiciste.

---

## 5. Si algo falla

| Lo que ves | Qué pasa | Qué hacer |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop no está abierto | Abrilo, esperá a que diga *Running*, reintentá |
| `requested image's platform (linux/amd64) does not match the detected host platform` | Tenés Apple Silicon (M1 o posterior). La imagen de SQL Server solo existe para `linux/amd64` | **Es esperado.** No hagas nada: corre bajo emulación y el primer arranque tarda 1–3 min más |
| `no configuration file provided: not found` | No estás en la carpeta del laboratorio | `cd claseInjeccionSQL` y reintentá |
| `port is already allocated` (8000 o 1433) | Otro programa usa ese puerto (otro SQL Server local, otra app) | Bajá lo que lo ocupa, o cambiá el mapeo en `docker-compose.yml` |
| El `--build` corta en `pip install` | Se cortó la conexión (portal cautivo de la wifi) | Reconectate y repetí `docker compose up -d --build`. Docker continúa desde donde quedó |
| `init` en `Exited (1)` | El sembrado falló | `docker compose logs init` y avisá |
| La web no responde, y `docker compose ps` no la muestra | Todavía no llegó a arrancar, o `init` no terminó bien | `docker compose logs web` y `docker compose logs init` |

Si nada de esto funciona, el reinicio limpio es:

```bash
docker compose down
docker compose up -d --build
```

---

## 6. Si rompés los datos

Una de las prácticas es destructiva a propósito. Para devolver la base a su
estado original, **sin bajar el laboratorio**:

```bash
docker compose run --rm init
```

Vuelve a ejecutar `init.sql`, que recrea las tablas y las siembra de nuevo.

---

## 7. Al terminar la clase

```bash
docker compose down
```

Los datos viven dentro del contenedor de SQL Server, así que `down` los borra.
El próximo `up` siembra la base desde cero.

---

## 8. Qué se entrega

Por cada práctica: **captura de pantalla**, el **SQL que se ejecutó** (la app lo
muestra abajo de cada resultado, copialo tal cual) y una **explicación con tus
palabras de por qué funcionó**. Lo que se evalúa es el *porqué*, no el *qué*.

Y la pregunta de cierre, individual y por escrito:

> **¿En qué momento exacto dejó de ser un dato y pasó a ser código?**

Para responderla, ubicá en `app.py` la línea marcada con
`# ---- VULNERABLE: concatenacion directa de la entrada del usuario ----` y
citala junto con tu respuesta.
