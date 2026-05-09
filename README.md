# ⚡ Food Hub Bot

Automatiza la reserva de tickets del USU Food Hub (USYD) en Humanitix.

El bot detecta automáticamente la próxima franja disponible del día, espera hasta que los tickets abran y completa la reserva en segundos.

---

## Requisitos

- Windows 10/11
- [Python 3.10+](https://www.python.org/downloads/) — marca **"Add Python to PATH"** al instalar

---

## Instalación

1. Descarga o clona este repositorio
2. Haz doble click en **`setup.bat`**

Esto instala todas las dependencias automáticamente (~200MB, solo la primera vez).

---

## Uso

1. Haz doble click en **`run.bat`**
2. Rellena tus datos la primera vez (se guardan automáticamente)
3. Pulsa **Ejecutar Bot**

El bot:
- Lee los slots disponibles para hoy
- Espera hasta la hora de apertura del próximo ticket
- Recarga la página hasta que el botón esté activo
- Rellena el formulario y confirma la reserva

---

## Notas

- Funciona de lunes a viernes entre las 8:00 y las 12:30
- Necesita el PC encendido y conectado a internet
- Se abrirá una ventana de Firefox — no la cierres mientras el bot está corriendo
- Los tickets de Food Hub abren 2 horas antes del evento

---

## Estructura

```
foodhub-app/
├── app.py        # Interfaz gráfica
├── bot.py        # Lógica del bot
├── setup.bat     # Instalador (ejecutar una vez)
├── run.bat       # Lanzador
└── config.json   # Tus datos (se crea automáticamente)
```
