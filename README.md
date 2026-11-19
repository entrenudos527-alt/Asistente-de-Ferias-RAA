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

### Alternativa para Render: variables de entorno

En Render (plan free) no hay consola, así que la primera cuenta administradora
se puede crear con variables de entorno:

| Variable | Ejemplo | Para qué |
|---|---|---|
| `RAA_ADMIN_CORREO` | `admin@raa.cr` | Correo de la primera cuenta |
| `RAA_ADMIN_CLAVE` | `una-clave-larga` | Contraseña inicial (mínimo 8 caracteres) |
| `RAA_ADMIN_NOMBRE` | `Administración RAA` | Nombre visible (opcional) |

Solo se usa cuando la base todavía no tiene **ninguna** cuenta: si ya existe
una, no la duplica ni sobrescribe su contraseña. El paso a paso está en la
sección 6.

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

### 6.1 Cargar la cuenta administradora desde el panel

Render no tiene un usuario y contraseña propios para la aplicación: se cargan
como **variables de entorno** con los nombres que lee el código.

1. Entrá a <https://dashboard.render.com> y abrí el servicio
   `asistente-ferias-raa`.
2. En el menú lateral, elegí **Environment**.
3. En **Environment Variables**, tocá **Add Environment Variable** y cargá:

   | Key | Value |
   |---|---|
   | `RAA_ADMIN_CORREO` | tu correo, por ejemplo `admin@raa.cr` |
   | `RAA_ADMIN_CLAVE` | una contraseña de 8 caracteres o más |
   | `RAA_ADMIN_NOMBRE` | opcional, por ejemplo `Administración RAA` |

4. Verificá que también estén `SECRET_KEY` (Render la genera sola) y
   `API_IA_CLAVE` (la del proveedor de IA).
5. Tocá **Save Changes**. Render redeploya solo; si no, usá
   **Manual Deploy → Deploy latest commit**.
6. Abrí la URL del servicio y entrá en `/login` con ese correo y esa clave.

> Las claves de entorno se guardan cifradas y no se muestran de nuevo en el
> panel. Nunca las escribas en el repositorio ni en `.env.example`.

### 6.2 Después del primer ingreso

- Cambiá la contraseña desde **Cambiar contraseña**.
- Creá las demás cuentas desde **Usuarios**.
- Si el servicio usa un disco efímero (plan free), la base se reinicia en cada
  despliegue: el administrador vuelve a crearse con la clave del entorno y las
  demás cuentas se pierden. Para conservarlas, montá un disco persistente y
  apuntá `RAA_DB_PATH` a un archivo dentro de ese disco (por ejemplo
  `/var/data/raa.db`).
- Cuando la base sea persistente, podés borrar `RAA_ADMIN_CLAVE` del panel: la
  cuenta ya existe y la aplicación no la vuelve a crear.

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
