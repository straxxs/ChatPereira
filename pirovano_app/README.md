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

1. Crear la base `instituto_pirovano_db` y ejecutar el SQL del trabajo.
2. Copiar `.env.example` a `.env` y completar las credenciales.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Ejecutar: `python app.py`.

## Próximas piezas

La estructura queda preparada para sumar frontend, validaciones, respuestas/devoluciones, derivación a turnos, auditoría y reportes sin concentrar toda la lógica en `app.py`.
