
CREATE DATABASE IF NOT EXISTS instituto_pirovano_db;
USE instituto_pirovano_db;

CREATE TABLE IF NOT EXISTS ESPECIALIDAD (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS USUARIO (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL,
    apellido_usuario VARCHAR(50) NOT NULL,
    mail VARCHAR(100) NOT NULL UNIQUE,
    DNI VARCHAR(20) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS ADMINISTRADOR (
    id_usuario INT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

CREATE TABLE IF NOT EXISTS MEDICO (
    id_medico INT PRIMARY KEY,
    horarios_atencion VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    id_especialidad INT NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES USUARIO(id_usuario),
    FOREIGN KEY (id_especialidad) REFERENCES ESPECIALIDAD(id_especialidad)
);

CREATE TABLE IF NOT EXISTS PACIENTE (
    id_paciente INT PRIMARY KEY,
    sexo CHAR(1) CHECK (sexo IN ('M', 'F', 'X')),
    edad INT,
    telefono VARCHAR(20),
    historial_salud TEXT,
    FOREIGN KEY (id_paciente) REFERENCES USUARIO(id_usuario)
);

CREATE TABLE IF NOT EXISTS CONSULTA (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    descripcion_sintomas TEXT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente' CHECK (
        estado IN ('Pendiente', 'En Revision', 'Respondida', 'Cancelada')
    ),
    id_medico INT NOT NULL,
    id_paciente INT NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES MEDICO(id_medico),
    FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente)
);

CREATE TABLE IF NOT EXISTS DEVOLUCION (
    id_devolucion INT AUTO_INCREMENT PRIMARY KEY,
    turno VARCHAR(50),
    descripcion TEXT NOT NULL,
    fecha_hora_devolucion DATETIME NOT NULL,
    id_consulta INT NOT NULL,
    FOREIGN KEY (id_consulta) REFERENCES CONSULTA(id_consulta)
);

CREATE TABLE IF NOT EXISTS MENSAJE (
    id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta INT NOT NULL,
    id_usuario INT NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('paciente', 'medico')),
    contenido TEXT NULL,
    imagen VARCHAR(255) NULL,
    fecha_hora DATETIME NOT NULL,
    FOREIGN KEY (id_consulta) REFERENCES CONSULTA(id_consulta),
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

CREATE TABLE IF NOT EXISTS RECETA (
    id_receta INT AUTO_INCREMENT PRIMARY KEY,
    medicamentos VARCHAR(20),
    telefono VARCHAR(50),
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS DETALLE_DEVOLUCION (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_devolucion INT NOT NULL,
    id_receta INT NOT NULL,
    FOREIGN KEY (id_devolucion) REFERENCES DEVOLUCION(id_devolucion),
    FOREIGN KEY (id_receta) REFERENCES RECETA(id_receta)
);

CREATE TABLE IF NOT EXISTS HISTORIAL_CONSULTA (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta INT NOT NULL,
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20),
    fecha_cambio DATETIME,
    FOREIGN KEY (id_consulta) REFERENCES CONSULTA(id_consulta)
);

CREATE TABLE IF NOT EXISTS AUDITORIA_RECETA (
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
    id_receta INT NOT NULL,
    fecha DATETIME,
    accion VARCHAR(50),
    FOREIGN KEY (id_receta) REFERENCES RECETA(id_receta)
);

DROP TRIGGER IF EXISTS actualizar_estado_consulta;
DELIMITER //
CREATE TRIGGER actualizar_estado_consulta
AFTER INSERT ON DEVOLUCION
FOR EACH ROW
BEGIN
    UPDATE CONSULTA
    SET estado = 'Respondida'
    WHERE id_consulta = NEW.id_consulta;
END//
DELIMITER ;

DROP TRIGGER IF EXISTS registrar_cambio_estado;
DELIMITER //
CREATE TRIGGER registrar_cambio_estado
AFTER UPDATE ON CONSULTA
FOR EACH ROW
BEGIN
    IF NOT (OLD.estado <=> NEW.estado) THEN
        INSERT INTO HISTORIAL_CONSULTA (
            id_consulta,
            estado_anterior,
            estado_nuevo,
            fecha_cambio
        )
        VALUES (
            NEW.id_consulta,
            OLD.estado,
            NEW.estado,
            NOW()
        );
    END IF;
END//
DELIMITER ;

DROP TRIGGER IF EXISTS registrar_receta;
DELIMITER //
CREATE TRIGGER registrar_receta
AFTER INSERT ON RECETA
FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_RECETA (
        id_receta,
        fecha,
        accion
    )
    VALUES (
        NEW.id_receta,
        NOW(),
        'Receta creada'
    );
END//
DELIMITER ;

