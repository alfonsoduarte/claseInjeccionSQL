# Laboratorio SQLi — TiendaLab

Entorno **aislado y local** para practicar inyección SQL contra SQL Server.
Datos ficticios. Uso exclusivamente educativo.

## Requisitos

- **Docker**, instalado y corriendo:
  - Windows y macOS → [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - macOS (alternativa) → [OrbStack](https://orbstack.dev/)
- **`git`**, o bajarte el ZIP desde GitHub: *Code → Download ZIP*.
- Unos **2 GB libres** y **conexión a internet la primera vez**, para que `pip`
  instale Flask y pymssql dentro de la imagen de la web.

No hace falta instalar SQL Server, Python ni nada más: todo vive dentro de los
contenedores.

## Bajar el laboratorio

```bash
git clone https://github.com/alfonsoduarte/claseInjeccionSQL.git
cd claseInjeccionSQL
```

Si bajaste el ZIP, descomprimilo y entrá a la carpeta con `cd`.

## Arranque

```bash
docker compose up -d --build
```

Esto levanta tres servicios:

- `db` → SQL Server 2025 (puerto 1433, solo en `127.0.0.1`)
- `init` → siembra la base `TiendaLab` y termina (one-shot)
- `web` → la app **vulnerable** en <http://localhost:8000>

No hace falta esperar ni recargar a mano: el servicio `db` publica un
`healthcheck` y `init` arranca recién cuando SQL Server acepta conexiones.
La web, a su vez, solo arranca cuando `init` terminó con éxito. Si algo
falla, el propio `docker compose` lo detiene en vez de dejarte una web que
no conecta.

Para ver el resultado del sembrado:

```bash
docker compose logs init
```

Abrí <http://localhost:8000>. **Punto de control:** tenés que ver el título
`TiendaLab` con un cartel rojo que dice *Aplicacion deliberadamente vulnerable*,
y la pestaña del navegador tiene que decir **`TiendaLab (VULNERABLE)`**. Si eso
aparece, el laboratorio quedó montado.

### La sintaxis de las variables cambia según la terminal

Varias instrucciones de esta guía pasan variables de entorno (`WEB_BIND` y
`APP_FILE`). **La sintaxis es distinta en Windows**, y copiar la equivocada es el
error más común. Por suerte falla con un error visible, no en silencio: las dos
formas hacen exactamente lo mismo.

```bash
# macOS / Linux (bash, zsh)
WEB_BIND=127.0.0.1 docker compose up -d web
```

```powershell
# Windows (PowerShell)
$env:WEB_BIND = "127.0.0.1"; docker compose up -d web
```

> **Diferencia que sí es silenciosa.** En macOS/Linux la variable vale **solo
> para ese comando**. En PowerShell queda **puesta en la sesión**: si después
> corrés `docker compose up -d web` a secas, sigue valiendo la anterior. Por eso
> en Windows hay que **resetear explícitamente** para volver atrás, como se
> muestra en cada caso más abajo.

### Por qué la web se publica en el 8000 y no en el 5000

En macOS el puerto **5000 lo ocupa el AirPlay Receiver** (`ControlCenter`).
Ese proceso responde `403` antes de que Docker pueda atender el pedido, así
que `http://localhost:5000` devolvería un 403 vacío y parecería que la app
está rota. Por eso el laboratorio publica la web en **8000**.

Si preferís el 5000, desactivá *Ajustes del Sistema → General → AirDrop y
Handoff → Receptor de AirPlay* y cambiá el mapeo en `docker-compose.yml`.

### La web solo escucha en `127.0.0.1`

Por defecto la web se publica **solo en loopback**: la abrís desde tu máquina en
<http://localhost:8000>, pero **no es alcanzable desde la red**. Todos los
ejercicios se hacen así, cada uno desde su propio navegador.

Eso importa más de lo que parece. La app es **deliberadamente inyectable**,
muestra el SQL ejecutado y los errores del motor, con el payload de `UNION` de la
Práctica B se volcan todos los usuarios y sus hashes, y como la conexión usa
`autocommit=True` las escrituras del ataque **persisten**. Expuesta en una red
que no controlás (wifi del campus, un hotspot) eso queda al alcance de
cualquiera, no solo del compañero que debería estar atacándola.

Para abrirla a la red en un ejercicio supervisado —el reto de la sección 7 del
guion, o si corrés Docker dentro de una VM y navegás desde el host—:

```bash
WEB_BIND=0.0.0.0 docker compose up -d web              # macOS / Linux
```

```powershell
$env:WEB_BIND = "0.0.0.0"; docker compose up -d web     # Windows (PowerShell)
```

Y para volver al estado seguro, **indicá la interfaz de loopback de forma
explícita**:

```bash
WEB_BIND=127.0.0.1 docker compose up -d web            # macOS / Linux
```

```powershell
$env:WEB_BIND = "127.0.0.1"; docker compose up -d web   # Windows (PowerShell)
```

> **No alcanza con `docker compose up -d web` a secas.** Si `WEB_BIND` quedó
> exportada en la terminal o, peor, escrita en un archivo `.env` —que persiste
> entre terminales y reinicios—, Compose la sigue leyendo y la web **continúa
> abierta a la red** aunque creas que la cerraste. Verificalo siempre así:
>
> ```bash
> docker compose config | grep host_ip
> ```
>
> Tiene que decir `127.0.0.1`. Si dice `0.0.0.0`, todavía está expuesta.

### Conectarse al motor como `sa`

El puerto 1433 se publica **solo en `127.0.0.1`**: podés conectarte desde tu
máquina con SSMS, Azure Data Studio o `sqlcmd`, pero el motor **no es alcanzable
desde la red**. Nada del laboratorio necesita exponerlo — la app conecta por la
red interna de Compose (`DB_HOST: db`) y las consultas de administración se hacen
por dentro del contenedor:

```bash
docker compose exec db /opt/mssql-tools18/bin/sqlcmd -C -b -S localhost -U sa -P 'Lab_Sa_Pass_2024!'
```

La `-C` es necesaria porque `sqlcmd` v18 valida el certificado del servidor y el
laboratorio usa uno autofirmado. Para un cliente gráfico, conectate a
`localhost,1433` con el usuario `sa`.

## Probar la versión corregida

Las dos versiones ya están dentro de la imagen: no hay que renombrar
archivos ni reconstruir nada.

```bash
APP_FILE=app_seguro.py docker compose up -d web        # macOS / Linux
```

```powershell
$env:APP_FILE = "app_seguro.py"; docker compose up -d web   # Windows (PowerShell)
```

Para volver a la vulnerable. En Windows hay que indicarlo explícitamente, porque
la variable sigue puesta en la sesión:

```bash
docker compose up -d web                               # macOS / Linux
```

```powershell
$env:APP_FILE = "app.py"; docker compose up -d web     # Windows (PowerShell)
```

## Restaurar los datos

La Práctica C incluye una sentencia apilada destructiva
(`'; UPDATE Productos SET Precio = 0; --`). Para devolver la base a su
estado original:

```bash
docker compose run --rm init
```

El servicio `init` vuelve a ejecutar `init.sql`, que recrea las tablas y
las siembra de nuevo. No hace falta bajar todo el laboratorio.

## Detener y limpiar

```bash
docker compose down
```

Los datos viven dentro del contenedor de SQL Server, así que `down` los
borra y el próximo `up` vuelve a sembrar la base desde cero.

## Imágenes utilizadas

Se usan imágenes que ya están descargadas en la máquina, sin necesidad de
bajar nada adicional:

| Servicio | Imagen |
|---|---|
| `db`, `init` | `mcr.microsoft.com/mssql/server:2025-latest` |
| `web` | `python:3.12-slim-bookworm` (vía `Dockerfile`) |

El servicio `init` reutiliza la misma imagen de SQL Server en lugar de la
imagen `mcr.microsoft.com/mssql-tools`: la herramienta `sqlcmd` v18 ya viene
dentro de la imagen del motor, en `/opt/mssql-tools18/bin/sqlcmd`, y la
etiqueta `mssql-tools` fue retirada por Microsoft.

> **Plataforma.** La imagen de SQL Server solo se publica para `linux/amd64`.
> En **Windows y Linux** sobre x86_64 corre nativa. En **Apple Silicon** (M1 y
> posteriores) corre bajo emulación, así que el primer arranque tarda más
> (1–3 min) y Docker avisa con *"requested image's platform does not match the
> host platform"*: es esperado y no impide que funcione.

`docker compose up -d --build` sí necesita red la primera vez, pero solo
para que `pip` instale Flask y pymssql dentro de la imagen de la web.

## Archivos

- `docker-compose.yml` — orquestación
- `init.sql` — esquema + datos + login con privilegio excesivo (a corregir)
- `app.py` — versión **vulnerable**
- `app_seguro.py` — versión **corregida** (consultas parametrizadas)
- `Dockerfile` — imagen de la web
- `requirements.txt` — dependencias de Python
- `clase-sql-injection-isir.md` — guion de la clase

## Nota sobre el modo transaccional

Las dos apps abren la conexión con `autocommit=True`. Sin eso, `pymssql`
abre una transacción implícita y el cierre de la conexión la revierte: la
sentencia apilada de la Práctica C llegaría al motor pero no dejaría ningún
efecto visible, y el alumno creería que el ataque no funcionó.

El `autocommit` **no es un control de seguridad**; solo refleja el modo
transaccional en el que corre la aplicación.
