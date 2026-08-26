/*
1) 
Este trigger permite automatizar la actualización del estado de una consulta cuando un médico registra una devolución. Evita que el personal administrativo tenga que modificar manualmente el estado y mantiene la información consistente. 
*/
  
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

/*
2)
Permite mantener un historial del seguimiento de las consultas médicas, pudiendo saber cuándo y cómo evolucionó cada caso. 
*/
  
CREATE TABLE HISTORIAL_CONSULTA(
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta INT,
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20),
    fecha_cambio DATETIME,
    FOREIGN KEY(id_consulta) REFERENCES CONSULTA(id_consulta)
);

DELIMITER //

CREATE TRIGGER registrar_cambio_estado
AFTER UPDATE ON CONSULTA
FOR EACH ROW
BEGIN
    IF OLD.estado <> NEW.estado THEN

        INSERT INTO HISTORIAL_CONSULTA(
            id_consulta,
            estado_anterior,
            estado_nuevo,
            fecha_cambio
        )
        VALUES(
            OLD.id_consulta,
            OLD.estado,
            NEW.estado,
            NOW()
        );

    END IF;
END//

DELIMITER ;


/*
 3)
 Registro de recetas creadas
*/
CREATE TABLE AUDITORIA_RECETA(
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
    id_receta INT,
    fecha DATETIME,
    accion VARCHAR(50)
);

DELIMITER //

CREATE TRIGGER registrar_receta
AFTER INSERT ON RECETA
FOR EACH ROW
BEGIN

INSERT INTO AUDITORIA_RECETA(
id_receta,
fecha,
accion
)
VALUES(
NEW.id_receta,
NOW(),
'Receta creada'
);

END//

DELIMITER ;

