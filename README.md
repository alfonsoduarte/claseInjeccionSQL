# Laboratorio SQLi — TiendaLab

Entorno **aislado y local** para practicar inyección SQL contra SQL Server.
Datos ficticios. Uso exclusivamente educativo.

## Arranque

```bash
docker compose up -d --build
```

Esto levanta tres servicios:

- `db` → SQL Server 2025 (puerto 1433)
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

### Por qué la web se publica en el 8000 y no en el 5000

En macOS el puerto **5000 lo ocupa el AirPlay Receiver** (`ControlCenter`).
Ese proceso responde `403` antes de que Docker pueda atender el pedido, así
que `http://localhost:5000` devolvería un 403 vacío y parecería que la app
está rota. Por eso el laboratorio publica la web en **8000**.

Si preferís el 5000, desactivá *Ajustes del Sistema → General → AirDrop y
Handoff → Receptor de AirPlay* y cambiá el mapeo en `docker-compose.yml`.

## Probar la versión corregida

Las dos versiones ya están dentro de la imagen: no hay que renombrar
archivos ni reconstruir nada.

```bash
APP_FILE=app_seguro.py docker compose up -d web
```

Para volver a la vulnerable:

```bash
docker compose up -d web
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
> En equipos Apple Silicon corre bajo emulación, por lo que el primer
> arranque tarda más (1–3 min). Docker avisa con
> *"requested image's platform does not match the host platform"*: es
> esperado y no impide que funcione.

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
