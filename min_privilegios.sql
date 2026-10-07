-- =====================================================================
--  TiendaLab - Correccion 2: minimo privilegio para el login de la app.
--  Ejecutar como sa. Se puede ejecutar varias veces sin error.
--
--  OJO: `docker compose run --rm init` vuelve a ejecutar init.sql, que
--  recrea las tablas y devuelve app_user a db_owner A PROPOSITO. Despues
--  de restaurar los datos hay que volver a aplicar este script.
--
--  El minimo privilegio NO corrige la inyeccion: el bypass del login y la
--  lectura de Usuarios y de los metadatos siguen funcionando en app.py.
--  Solo acota el dano (no leer Clientes, no modificar, no borrar).
-- =====================================================================

USE TiendaLab;
GO

IF IS_ROLEMEMBER('db_owner', 'app_user') = 1
    ALTER ROLE db_owner DROP MEMBER app_user;
GO

-- Solo lo que la app realmente necesita:
GRANT SELECT ON dbo.Productos TO app_user;
GRANT SELECT ON dbo.Usuarios  TO app_user;   -- o mejor: solo EXECUTE de un SP de login

-- Datos sensibles fuera del alcance de la app:
DENY SELECT ON dbo.Clientes TO app_user;
GO

PRINT 'Minimo privilegio aplicado a app_user.';
GO
