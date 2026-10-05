-- =====================================================================
--  TiendaLab - Base de datos de laboratorio para la práctica de SQLi
--  Datos 100% ficticios. Uso exclusivamente educativo y local.
-- =====================================================================

IF DB_ID('TiendaLab') IS NULL
    CREATE DATABASE TiendaLab;
GO

USE TiendaLab;
GO

IF OBJECT_ID('dbo.Usuarios')  IS NOT NULL DROP TABLE dbo.Usuarios;
IF OBJECT_ID('dbo.Productos') IS NOT NULL DROP TABLE dbo.Productos;
IF OBJECT_ID('dbo.Clientes')  IS NOT NULL DROP TABLE dbo.Clientes;
GO

CREATE TABLE dbo.Usuarios (
    Id           INT IDENTITY(1,1) PRIMARY KEY,
    Usuario      NVARCHAR(50)  NOT NULL,
    PasswordHash NVARCHAR(100) NOT NULL,
    Rol          NVARCHAR(20)  NOT NULL,
    Email        NVARCHAR(100) NULL
);

CREATE TABLE dbo.Productos (
    Id        INT IDENTITY(1,1) PRIMARY KEY,
    Nombre    NVARCHAR(100) NOT NULL,
    Categoria NVARCHAR(50)  NOT NULL,
    Precio    DECIMAL(10,2) NOT NULL,
    Stock     INT           NOT NULL
);

CREATE TABLE dbo.Clientes (
    Id      INT IDENTITY(1,1) PRIMARY KEY,
    Nombre  NVARCHAR(100) NOT NULL,
    Tarjeta NVARCHAR(25)  NOT NULL,   -- dato "sensible" ficticio
    Email   NVARCHAR(100) NULL
);
GO

-- "Hashes" ficticios: no son credenciales reales, solo cadenas de ejemplo.
INSERT INTO dbo.Usuarios (Usuario, PasswordHash, Rol, Email) VALUES
('admin',   'e3b0c44298fc1c149afbf4c8996fb924', 'admin',    'admin@tiendalab.mx'),
('jlopez',  '5f4dcc3b5aa765d61d8327deb882cf99', 'vendedor', 'jlopez@tiendalab.mx'),
('mrivera', '21232f297a57a5a743894a0e4a801fc3', 'vendedor', 'mrivera@tiendalab.mx');

INSERT INTO dbo.Productos (Nombre, Categoria, Precio, Stock) VALUES
('Tenis Runner Pro', 'Calzado',    1299.00, 40),
('Bota Industrial',  'Calzado',     899.50, 25),
('Sandalia Verano',  'Calzado',     499.00, 60),
('Mochila Urbana',   'Accesorios',  650.00, 30);

INSERT INTO dbo.Clientes (Nombre, Tarjeta, Email) VALUES
('Cliente Demo 1', '4111-1111-1111-1111', 'demo1@correo.mx'),
('Cliente Demo 2', '5500-0000-0000-0004', 'demo2@correo.mx');
GO

-- ---------------------------------------------------------------------
--  Login de la aplicacion CON PRIVILEGIO EXCESIVO.
--  Esto es parte del problema que los alumnos deben detectar y corregir
--  en la fase de remediacion (principio de minimo privilegio).
-- ---------------------------------------------------------------------
IF SUSER_ID('app_login') IS NULL
    CREATE LOGIN app_login WITH PASSWORD = 'App_Pass_123!', CHECK_POLICY = OFF;
GO

USE TiendaLab;
GO

IF USER_ID('app_user') IS NULL
    CREATE USER app_user FOR LOGIN app_login;
GO

-- A proposito MAL: la aplicacion entra como dueno de la base de datos.
ALTER ROLE db_owner ADD MEMBER app_user;
GO

PRINT 'TiendaLab inicializada correctamente.';
GO
