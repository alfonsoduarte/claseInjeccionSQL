# Correcciones de la guía y verificación del laboratorio

## Objetivo
Corregir instrucciones erróneas y comprobar el montaje y uso básico de TiendaLab antes de publicar en main.

## Alcance y restricciones
- INSTRUCCIONES-ALUMNOS.md y README.md: comillas, comandos PowerShell, descarga y tiempos sin garantías infundadas; requisitos con margen.
- Guion, evaluación, código, dependencias y Compose sin cambios.
- Instancia de prueba separada y solo en loopback; datos anteriores preservados.
- Usuario autorizó publicar en main. Rama de trabajo: docs/correcciones-alumnos.

## Tareas
- [x] T1 — Corregir las guías, verificar estructura y montaje básico, y publicar en main. Estado: completada; pruebas aprobadas y publicación remota verificada.
- [ ] T2 — Completar comprobación de las prácticas de inyección y mínimo privilegio. Estado: pendiente; no ejecutadas. No es un bloqueo para publicar las correcciones documentales, pero impide declarar todo el laboratorio validado.

## Criterios de aceptación T1
- Mostrar `’` (U+2019) frente a `'` (U+0027).
- grep para bash/zsh y Select-String para PowerShell en ambas guías.
- Sin confundir tamaño local y transferencia ni garantizar tiempos.
- Lectura estructural y git diff --check sin errores.
- Build, db saludable, init exitoso, web local, búsqueda normal y rechazo de credenciales inválidas en ambas versiones.
- Detener solo instancia creada para la prueba y verificar publicación remota.

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
Alumnos pueden seguir el montaje publicado en main. Completar T2 antes de afirmar que todas las prácticas fueron verificadas.
