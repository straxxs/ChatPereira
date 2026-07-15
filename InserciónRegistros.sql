INSERT INTO ESPECIALIDAD (nombre) VALUES 
('Clinica Medica'), ('Cardiologia'), ('Dermatologia'), ('Traumatologia'), 
('Pediatria'), ('Ginecologia'), ('Oftalmologia'), ('Neurologia'), 
('Gastroenterologia'), ('Endocrinologia');

INSERT INTO USUARIO (id_usuario, nombre_usuario, apellido_usuario, mail, DNI, contraseña) VALUES
-- Administradores (IDs 1-10)
(1, 'Andres', 'Gomez', 'andres.gomez@pirovano.com', '35111222', 'pass123'),
(2, 'Beatriz', 'Lopez', 'beatriz.lopez@pirovano.com', '35111223', 'andres123'),
(3, 'Carlos', 'Martinez', 'carlos.martinez@pirovano.com', '35111224', 'carlos123'),
(4, 'Daniela', 'Rodriguez', 'daniela.rodriguez@pirovano.com', '35111225', 'pass123'),
(5, 'Eduardo', 'Sanchez', 'eduardo.sanchez@pirovano.com', '35111226', 'eduardo123'),
(6, 'Florencia', 'Perez', 'florencia.perez@pirovano.com', '35111227', 'florencia123'),
(7, 'Gabriel', 'Fernandez', 'gabriel.fernandez@pirovano.com', '35111228', 'gabriel123'),
(8, 'Hugo', 'Alvarez', 'hugo.alvarez@pirovano.com', '35111229', 'hugo123'),
(9, 'Irene', 'Diaz', 'irene.diaz@pirovano.com', '35111230', 'irene123'),
(10, 'Jorge', 'Vasquez', 'jorge.vasquez@pirovano.com', '35111231', 'jorge123'),
-- Médicos (IDs 11-20)
(11, 'Juan', 'Perez', 'juan.perez@med.pirovano.com', '20111222', 'juan123'),
(12, 'Maria', 'Gonzalez', 'maria.gonzalez@med.pirovano.com', '21333444', 'maria123'),
(13, 'Ricardo', 'Darin', 'ricardo.darin@med.pirovano.com', '18555666', 'ricardo123'),
(14, 'Ana', 'Echeverria', 'ana.eche@med.pirovano.com', '25777888', 'ana123'),
(15, 'Luis', 'Scola', 'luis.scola@med.pirovano.com', '22999000', 'luis123'),
(16, 'Sofia', 'Loren', 'sofia.loren@med.pirovano.com', '30123456', 'sofia123'),
(17, 'Pedro', 'Almodovar', 'pedro.almo@med.pirovano.com', '17654321', 'pedro123'),
(18, 'Laura', 'Paussini', 'laura.pau@med.pirovano.com', '28987654', 'laura123'),
(19, 'Diego', 'Maradona', 'diego.diego@med.pirovano.com', '10101010', 'diego123'),
(20, 'Elena', 'Roger', 'elena.roger@med.pirovano.com', '31456789', 'elena123'),
-- Pacientes (IDs 21-30)
(21, 'Lucas', 'Mora', 'lucas.mora@gmail.com', '40111222', 'lucas123'),
(22, 'Martina', 'Stoessel', 'tini@gmail.com', '42333444', 'martina123'),
(23, 'Facundo', 'Campazzo', 'facu@gmail.com', '38555666', 'facundo123'),
(24, 'Camila', 'Bordonaba', 'cami@gmail.com', '29777888', 'camila123'),
(25, 'Bautista', 'Vicuna', 'bauti@gmail.com', '45999000', 'bautista123'),
(26, 'Valentina', 'Zenere', 'valen@gmail.com', '41123456', 'valentina123'),
(27, 'Mateo', 'Palacios', 'trueno@gmail.com', '43654321', 'mateo123'),
(28, 'Juana', 'Viale', 'juanita@gmail.com', '32987654', 'juana123'),
(29, 'Lionel', 'Messi', 'leomessi@gmail.com', '33101010', 'lionel123'),
(30, 'Antonela', 'Roccuzzo', 'anto@gmail.com', '34456789', 'antonela123');

INSERT INTO ADMINISTRADOR (id_usuario) VALUES 
(1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

INSERT INTO MEDICO (id_medico, horarios_atencion, telefono, id_especialidad) VALUES
(11, 'Lunes a Viernes 08:00 - 12:00', '1144445555', 1),
(12, 'Lunes y Miércoles 14:00 - 18:00', '1144445556', 2),
(13, 'Martes y Jueves 09:00 - 13:00', '1144445557', 3),
(14, 'Viernes 13:00 - 17:00', '1144445558', 4),
(15, 'Lunes a Jueves 10:00 - 14:00', '1144445559', 5),
(16, 'Martes, Miercoles y Viernes 15:00 - 19:00', '1144445560', 6),
(17, 'Miércoles 08:00 - 14:00', '1144445561', 7),
(18, 'Jueves 14:00 - 20:00', '1144445562', 8),
(19, 'Lunes 12:00 - 16:00', '1144445563', 9),
(20, 'Viernes 08:00 - 12:00', '1144445564', 10);

INSERT INTO PACIENTE (id_paciente, sexo, edad, telefono, historial_salud) VALUES
(21, 'M', 25, '1155556666', 'Ninguna enfermedad preexistente.'),
(22, 'F', 23, '1155556667', 'Asma leve controlado.'),
(23, 'M', 28, '1155556668', 'Operado de meniscos en 2022.'),
(24, 'F', 34, '1155556669', 'Alergia a la penicilina.'),
(25, 'M', 18, '1155556670', 'Hipertensión hereditaria bajo control.'),
(26, 'F', 24, '1155556671', 'Ninguna enfermedad preexistente.'),
(27, 'M', 22, '1155556672', 'Esguince crónico de tobillo izquierdo.'),
(28, 'F', 40, '1155556673', 'Hipotiroidismo crónico.'),
(29, 'M', 38, '1155556674', 'Excelente estado atlético, controles anuales.'),
(30, 'F', 36, '1155556675', 'Madre lactante, sin patologías.');

