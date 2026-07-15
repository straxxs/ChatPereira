CREATE DATABASE IF NOT EXISTS instituto_pirovano_db;
USE instituto_pirovano_db;

CREATE TABLE ESPECIALIDAD (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE USUARIO (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL,
    apellido_usuario VARCHAR(50) NOT NULL,
    mail VARCHAR(100) NOT NULL UNIQUE,
    DNI VARCHAR(20) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL
);

CREATE TABLE ADMINISTRADOR (
    id_usuario INT PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
); 

CREATE TABLE MEDICO (
    id_medico INT PRIMARY KEY,
    horarios_atencion VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    id_especialidad INT NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES USUARIO(id_usuario)
    FOREIGN KEY (id_especialidad)REFERENCES ESPECIALIDAD(id_especialidad) 
);

CREATE TABLE PACIENTE (
    id_paciente INT PRMARY KEY,
    sexo CHAR(1) CHECK (sexo IN ('M', 'F', 'X')),
    edad INT,
    telefono VARCHAR(20),
    historial_salud TEXT,
    FOREIGN KEY (id_paciente)REFERENCES USUARIO(id_usuario)
);

CREATE TABLE CONSULTA (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    descripcion_sintomas TEXT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado IN('Pendiente', 'En Revision', 'Respondida', 'Cancelada')),
    id_medico INT NOT NULL,
    id_paciente INT NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES MEDICO(id_medico),
    FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_paciente)
);

CREATE TABLE DEVOLUCION (
    id_devolucion INT AUTO_INCREMENT PRIMARY KEY,
    turno VARCHAR(50),
    descripcion TEXT NOT NULL,
    fecha_hora_devolucion DATETIME NOT NULL,
    id_consulta INT NOT NULL UNIQUE,
    FOREIGN KEY (id_consulta) REFERENCES CONSULTA(id_consulta)
);


CREATE TABLE RECETA (
    id_receta INT AUTO_INCREMENT PRMARY KEY,
    medicamentos varchar(20),
    telefono VARCHAR(50),
    descripcion TEXT 
);

CREATE TABLE DETALLE_DEVOLUCION (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_devolucion INT NOT NULL,
    id_receta INT NOT NULL,
    FOREIGN KEY (id_devolucion) REFERENCES DEVOLUCION(id_devolucion),
    FOREIGN KEY (id_receta) REFERENCES RECETA(id_receta)
);
