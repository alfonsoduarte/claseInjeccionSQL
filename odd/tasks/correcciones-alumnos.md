# Correcciones de la guía y verificación del laboratorio

## Objetivo
Corregir instrucciones erróneas y comprobar el montaje y uso básico de TiendaLab antes de publicar en main.

## Alcance y restricciones
- INSTRUCCIONES-ALUMNOS.md y README.md: comillas, comandos PowerShell, descarga y tiempos sin garantías infundadas; requisitos con margen.
- T1 mantuvo guion, evaluación, código y Compose sin cambios. Para T2 el usuario autorizó verificar SQLi/mínimo privilegio, corregir defectos comprobados y publicar; no corregir la vulnerabilidad deliberada de app.py ni cambiar el alcance didáctico.
- Instancia de prueba separada y solo en loopback; datos anteriores preservados.
- Usuario autorizó publicar en el repositorio. T1 se entregó a main desde docs/correcciones-alumnos. T2 trabaja en test/lab-sqli-privilegios y entrega las correcciones revisadas a main.

## Tareas
- [x] T1 — Corregir las guías, verificar estructura y montaje básico, y publicar en main. Estado: completada; pruebas aprobadas y publicación remota verificada.
- [ ] T2 — Completar comprobación de las prácticas de inyección y mínimo privilegio. Estado: pendiente/bloqueada; los ejecutores se detuvieron por su clasificador de seguridad. No se ejecutaron pruebas SQLi ni de permisos, no se creó tests/verify_lab.py ni se iniciaron fixtures nuevas.
- [ ] T3 — Corregir instrucciones de mínimo privilegio y publicar el helper SQL con comprobación estructural independiente. Estado: en curso. No equivale a completar T2.

## Criterios de aceptación T1
- Mostrar `’` (U+2019) frente a `'` (U+0027).
- grep para bash/zsh y Select-String para PowerShell en ambas guías.
- Sin confundir tamaño local y transferencia ni garantizar tiempos.
- Lectura estructural y git diff --check sin errores.
- Build, db saludable, init exitoso, web local, búsqueda normal y rechazo de credenciales inválidas en ambas versiones.
- Detener solo instancia creada para la prueba y verificar publicación remota.

## Criterios de aceptación T2
- Validar controles de sandbox antes de ejecutar: sin red externa, sin acceso a datos previos, raíz/código solo lectura, entorno permitido y scratch acotado, límites de recursos y tiempo.
- Usar imágenes ya presentes, sin descargar dependencias ni instalar herramientas del host.
- Confirmar prácticas A/B/C en fixture propia ficticia, restauración, bloqueo por parámetros y permisos mínimos.
- Añadir regresiones reproducibles y corregir solo defectos observados en código o instrucciones; test-first cuando corresponda a cambios de comportamiento.
- Detener la fixture nueva y conservar íntegro el laboratorio anterior.
- Registrar límites reales: este host, no Windows ni descarga limpia.
- Commit de unidad de trabajo, revisión nativa si corresponde, publicación autorizada y SHA remoto comprobado.

## Evidencia observada
- Base b2d37d8, árbol inicial limpio. Prueba: macOS arm64, OrbStack linux/arm64, Docker 29.4.0, 16.8 GB de RAM disponibles al motor Docker.
- Writer: git diff --check y script estructural Python aprobados; dos guías modificadas, +56/-35 líneas.
- ASSESS nativo no pudo evaluar por selección de untracked; se aplicó verificación independiente conservadora. Cambio pasivo de documentación: no hay RED/GREEN significativo ni cambios de comportamiento.
- El primer verificador falló antes de ejecutar comandos; el ejecutor alternativo rechazó la comprobación amplia de seguridad. Una verificación independiente más acotada sí completó build y uso básico.
- Instancia nueva tiendalab-docs-check-20261007: comando APP_FILE=app.py WEB_BIND=127.0.0.1 docker compose -f docker-compose.yml -p tiendalab-docs-check-20261007 up -d --build; build completado y estado confirmado. El verificador no conservó el código de salida del launch, por lo que la evidencia de éxito es el estado y las respuestas posteriores.
- db healthy; init Exited (0) con TiendaLab inicializada correctamente.; web running; puertos 1433/8000 solo en 127.0.0.1.
- HTTP GET /: 200 y título vulnerable. GET /buscar?q=Mochila: 200, producto Mochila Urbana y precio 650.00. POST /login con contraseña incorrecta: 200 y mensaje de rechazo.
- app_seguro.py vía Flask test_client dentro del contenedor: búsqueda normal y login inválido aprobados (exit 0).
- docker compose -f docker-compose.yml -p tiendalab-docs-check-20261007 stop: exit 0; todos los contenedores de prueba detenidos, puertos libres, proyecto original sin cambios.
- Parent spot-check: git diff --check aprobado y estado de contenedores de prueba detenido confirmado.

## Límites y pendientes
- No probados: inyección, privilegios, restauración destructiva, Windows/PowerShell real, navegador gráfico, descarga con caché vacía y mínimos de hardware recomendados.
- En docker-compose.yml queda un comentario con 1–3 minutos; no se editó por estar fuera del alcance. No afecta el comando ni las guías corregidas.
- Los contenedores de prueba quedan detenidos; no se borraron ni se tocaron datos anteriores.
- No asegurar compatibilidad universal: se verificó el montaje y uso básico en este host.

## Publicación
Work-unit commit: 1f08d4b2a846ac0e4bf06d44a6dbe40e1e736e01. Push a origin/main exitoso y SHA confirmado con git ls-remote. Reversión acotada: INSTRUCCIONES-ALUMNOS.md y README.md; no cambia comportamiento de aplicaciones ni base.

## Próximo paso
Publicar T3 solo con evidencia estructural/revisión; mantener T2 pendiente y sin garantías de validación funcional completa.

## Correcciones T3
- Worker agregó min_privilegios.sql: USE/GO, DROP MEMBER condicional, GRANT SELECT Productos/Usuarios, DENY SELECT Clientes, GO final.
- Guion: comandos stdin para bash y PowerShell, explicación correcta de -T, GO/EXIT interactivo, comprobación como app_login y límites del mínimo privilegio.
- Tres guías advierten que init.sql restaura db_owner y requiere reaplicar la corrección.
- Worker observó RED estructural: bloque original sin GO (grep exit 1); git diff --check posterior exit 0. GREEN independiente pendiente.
- Fallos de ejecutores: verificador sin handoff válido; writer alcanzó cambios documentales/SQL y luego bloqueó la escritura de la prueba por clasificador. Se preservaron cambios parciales y se detuvo ese alcance. No se evade el bloqueo.
- Código vulnerable y parametrizado, Compose y datos anteriores sin cambios. No se simula evidencia de ejecución.
