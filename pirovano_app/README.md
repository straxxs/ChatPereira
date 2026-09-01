# Instituto Pirovano — estructura modular

Proyecto base para el sistema de consultas médico-paciente definido en el trabajo práctico.

## Módulos

- `auth.py`: inicio/cierre de sesión y control de roles.
- `consultas.py`: creación, consulta y bandeja de consultas.
- `medicos.py`: listado de médicos y especialidades.
- `pacientes.py`: perfil del paciente.
- `recetas.py`: creación de recetas por parte del médico.
- `admin.py`: administración de usuarios.
- `especialidades.py`: consulta de especialidades.
- `devoluciones.py`: respuestas del médico, derivación y vínculo con recetas.
- `registro.py`: alta de pacientes.
- `db.py`: conexión única a MySQL.
- `config.py`: configuración mediante variables de entorno.

## Puesta en marcha

1. Crear la base ejecutando `BaseDeDatos.sql`.
2. Ejecutar `triggers.sql` para crear el historial de estados y la auditoría de recetas. También podés usar `BaseDeDatosCompleta.sql` para hacer ambos pasos de una vez.
3. Ejecutar `InserciónRegistros.sql` para cargar los datos de prueba. Las contraseñas de prueba ya están almacenadas con hash compatible con Werkzeug.
4. Copiar `.env.example` a `.env` y completar las credenciales.
5. Instalar dependencias: `pip install -r requirements.txt`.
6. Ejecutar: `python app.py`.

## Próximas piezas

La estructura queda preparada para sumar frontend, validaciones, respuestas/devoluciones, derivación a turnos, auditoría y reportes sin concentrar toda la lógica en `app.py`.

### Triggers

Los triggers se ejecutan en MySQL y no se replican manualmente desde Flask:

- `actualizar_estado_consulta`: al insertar una `DEVOLUCION`, cambia automáticamente la `CONSULTA` relacionada a `Respondida`.
- `registrar_cambio_estado`: registra en `HISTORIAL_CONSULTA` cualquier cambio de estado. Por eso, el cambio producido por el trigger anterior también queda auditado.
- `registrar_receta`: registra en `AUDITORIA_RECETA` cada receta creada.

La aplicación inserta en `DEVOLUCION` y `RECETA`; MySQL se encarga de las acciones automáticas.

## Interfaz de conversación
La segunda etapa agrega una vista tipo chat asincrónico. Las consultas mantienen su modelo original y las respuestas médicas siguen insertándose en `DEVOLUCION`, por lo que el trigger `actualizar_estado_consulta` continúa siendo utilizado. `MENSAJE` guarda el historial visual del intercambio y permite mensajes posteriores del paciente y del médico. Las imágenes se almacenan en `static/uploads/chat`.

Para una base existente ejecutar `../MigracionChat.sql` (ruta desde la carpeta `ChatPereira`) antes de levantar la aplicación.
