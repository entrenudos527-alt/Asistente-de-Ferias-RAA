# Asistente de Eventos RAA

Aplicación Flask para consultar eventos de la Red Alajuelita Artesanal y
preguntar al asistente. Los eventos se leen de un Excel; las cuentas y los
permisos se guardan en una base SQLite aparte.

## Ingreso obligatorio

Todas las páginas (listado, detalle, asistente y administración) requieren
sesión. No existe registro público: las cuentas las crea una persona
administradora. Solo quedan públicos el ingreso (`/login`), el logo
(`/static`) y el chequeo de salud (`/salud`).

| Rol | Puede |
|-----|-------|
| **Administrador** | Consultar eventos, usar el asistente, crear y desactivar cuentas, cambiar roles, generar contraseñas temporales y cargar una versión nueva del Excel. |
| **Usuario** | Consultar eventos y usar el asistente. No puede modificar datos ni entrar a administración. |

## 1. Crear la primera cuenta administradora

No hay contraseñas predeterminadas en el código. La primera cuenta se crea
desde la consola, en la carpeta del proyecto:

```powershell
# Windows (PowerShell)
.venv\Scripts\python.exe -m flask --app wsgi crear-admin
```

El comando pide correo, nombre y contraseña (mínimo 8 caracteres). También
acepta los datos como opciones:

```powershell
.venv\Scripts\python.exe -m flask --app wsgi crear-admin `
  --correo admin@raa.cr --nombre "Ana Pérez"
```

Luego ingresá en <http://127.0.0.1:5000/login>.

> Si usás `uv`: `uv run flask --app wsgi crear-admin`.

## 2. Agregar a las demás personas

1. Ingresá como administrador.
2. Abrí **Usuarios** en el menú.
3. Completá correo, nombre y rol, y tocá **Crear cuenta con contraseña temporal**.
4. La contraseña temporal aparece **una sola vez** en un aviso morado.
   Entregala a la persona por un medio seguro.
5. En su primer ingreso, la aplicación la obliga a cambiarla antes de ver
   cualquier evento.

Desde la misma pantalla podés:

- **Desactivar / Activar** una cuenta (al desactivarla se cierra su sesión).
- **Cambiar rol** entre usuario y administrador.
- **Nueva temporal**: genera otra contraseña temporal. La anterior deja de
  funcionar y no es posible verla ni recuperarla.

No se puede desactivar la propia cuenta ni dejar la aplicación sin al menos
una persona administradora activa.

## 3. Iniciar la aplicación

```powershell
iniciar_app.bat
```

Abre el servidor y el navegador en el ingreso. Si todavía no hay cuentas, la
consola recuerda el comando para crear la primera.

## 4. Actualizar los eventos (Excel)

**Opción A — desde la aplicación (recomendada):** como administrador, entrá a
**Eventos (Excel)** y subí el archivo `.xlsx`. Se lee solo la hoja `Eventos`
con los encabezados en la fila 1. La carga **reemplaza** la versión anterior
(no se duplican eventos) y guarda una copia en `datos/eventos.xlsx`.
El botón **Volver al Excel original** descarta esa copia.

**Opción B — reemplazar el archivo:** sustituí
`Insumos/Plantilla_Eventos_RAA (1).xlsx` por la nueva versión con el mismo
nombre y estructura, y reiniciá la aplicación. No hace falta ejecutar ningún
comando extra.

## 5. Seguridad implementada

- Contraseñas con hash **PBKDF2-SHA256** (Werkzeug). Nunca se guardan en texto
  plano ni se pueden recuperar.
- **Token CSRF** en todos los formularios y en el chat.
- Sesión firmada con `SECRET_KEY`, cookie `HttpOnly` + `SameSite=Lax`
  (`Secure` con `RAA_COOKIE_SEGURA=1` en producción) y token de sesión en la
  base: al cerrar sesión, desactivar la cuenta o restablecer la contraseña, la
  sesión anterior deja de valer.
- **Límite de intentos**: 5 fallos en 15 minutos bloquean ese correo desde esa
  IP.
- Contraseñas temporales generadas al azar (12 caracteres).
- Cabeceras `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` y
  `Cache-Control: no-store` en páginas autenticadas.
- La base `datos/raa.db` está excluida de Git.

## 6. Despliegue en Render

- Build: `pip install -r requirements.txt`
- Start: `gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2`
- Variables: `SECRET_KEY`, `API_IA_CLAVE`, `RAA_COOKIE_SEGURA=1` y,
  opcionalmente, `RAA_DB_PATH`.
- En el plan free el disco es efímero: al redeployar se pierden las cuentas.
  Para conservarlas, montá un disco persistente y apuntá `RAA_DB_PATH` a un
  archivo dentro de ese disco (por ejemplo `/var/data/raa.db`).
- Después del primer despliegue, creá la cuenta administradora desde la
  consola del servicio en Render con el mismo comando `flask --app wsgi crear-admin`.

## 7. Estructura

```
app/
  __init__.py                  rutas, sesión, CSRF, roles, carga de Excel
  seguridad.py                 token CSRF, sesión y decorador de administrador
  services/
    base_datos.py              SQLite: usuarios, intentos de ingreso
    autenticacion.py           hash, validaciones, bloqueo, cuentas
    lectura_eventos.py         lectura del Excel (hoja "Eventos")
    agente_ia.py               flujo del asistente
  templates/                   login, listado, detalle, asistente, administración
datos/                         base de cuentas y copia del Excel (no se sube a Git)
Insumos/                       archivos originales (no se modifican)
```

## 8. Verificación rápida

```powershell
# 1) Sin sesión, el listado pide ingreso
curl.exe -I http://127.0.0.1:5000/inicio

# 2) El listado carga con sesión (desde el navegador tras ingresar)

# 3) La base guarda hashes, no contraseñas
.venv\Scripts\python.exe -c "from app.services import base_datos; [print(u['correo'], u['hash_contrasena'][:20]) for u in base_datos.listar_usuarios()]"
```
