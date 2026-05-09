"""
bot.py — Lógica del bot separada de la interfaz.
Se importa desde app.py y también puede ejecutarse standalone.
"""

import asyncio
import re
from datetime import datetime, timedelta
from camoufox.async_api import AsyncCamoufox

EVENT_URL        = "https://events.humanitix.com/food-hub-2026-semester-1b"
BASE_TICKETS_URL = "https://events.humanitix.com/food-hub-2026-semester-1b/tickets"

SLOTS = [
    (10,  0), (10, 30), (11,  0), (11, 30),
    (12,  0), (12, 30), (13,  0), (13, 30),
    (14,  0), (14, 30),
]

MONTHS_EN = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}


def parse_slot_time(text):
    match = re.search(r'(\d{1,2})(?::(\d{2}))?(am|pm)', text.lower())
    if not match:
        return None
    hour   = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    ampm   = match.group(3)
    if ampm == 'pm' and hour != 12: hour += 12
    elif ampm == 'am' and hour == 12: hour = 0
    return (hour, minute)


def parse_slot_date(text):
    match = re.search(r'\w{3},\s*(\d{1,2})\s+(\w{3})', text)
    if not match:
        return None
    day   = int(match.group(1))
    month = MONTHS_EN.get(match.group(2))
    if not month:
        return None
    year = datetime.now().year
    try:
        from datetime import date
        return date(year, month, day)
    except:
        return None


async def fetch_today_slots(browser, log):
    today = datetime.now().date()
    page  = await browser.new_page()
    log("📋 Leyendo slots de hoy…", "live")
    await page.goto(EVENT_URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2000)

    links = await page.evaluate('''() =>
        Array.from(document.querySelectorAll('a[href*="dateId"]')).map(a => ({
            text: a.innerText.trim(), href: a.href
        }))
    ''')
    await page.close()

    slots = []
    for link in links:
        text = link['text']
        href = link['href']
        slot_date  = parse_slot_date(text)
        if not slot_date or slot_date != today:
            continue
        time_tuple = parse_slot_time(text)
        if not time_tuple or time_tuple not in SLOTS:
            continue
        match = re.search(r'dateId=([a-f0-9]+)', href)
        if not match:
            continue
        eh, em    = time_tuple
        open_time = datetime.now().replace(hour=eh-2, minute=em, second=0, microsecond=0)
        slots.append({
            'event_hour': eh, 'event_min': em,
            'open_time': open_time,
            'date_id': match.group(1),
        })

    slots.sort(key=lambda x: (x['event_hour'], x['event_min']))
    log(f"   {len(slots)} slots encontrados para hoy.", "")
    return slots


def get_next_slot(slots):
    now = datetime.now()
    for slot in slots:
        if now <= slot['open_time'] + timedelta(minutes=4):
            return slot
    return None


async def select_dropdown(page, index, answer, log):
    await page.evaluate(f'''() => {{
        const f = document.querySelectorAll('[data-testid="field-content"]');
        if (f[{index}]) f[{index}].parentElement.click();
    }}''')
    await page.wait_for_timeout(400)
    clicked = await page.evaluate(f'''() => {{
        for (const opt of document.querySelectorAll('[data-testid="dropdown-options"] div')) {{
            if (opt.textContent.trim() === "{answer}") {{ opt.click(); return true; }}
        }}
        return false;
    }}''')
    if clicked:
        log(f"✔ Pregunta {index+1}: {answer}", "ok")
    else:
        log(f"✘ Opción '{answer}' no encontrada", "err")
    await page.wait_for_timeout(300)


async def book_ticket(browser, slot, cfg, log):
    url       = f"{BASE_TICKETS_URL}?dateId={slot['date_id']}"
    open_time = slot['open_time']

    # Esperar hasta 5s antes
    pre_open  = open_time - timedelta(seconds=5)
    wait_secs = (pre_open - datetime.now()).total_seconds()
    if wait_secs > 0:
        log(f"⏳ Esperando hasta las {pre_open.strftime('%H:%M:%S')} ({wait_secs:.0f}s)…", "live")
        await asyncio.sleep(wait_secs)

    log(f"🚀 Abriendo página de tickets…", "live")
    page = await browser.new_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2000)

    # Bucle recarga
    btn = None
    for attempt in range(30):
        btn = await page.query_selector('[data-testid*="increment"]')
        if btn and await btn.get_attribute("data-disabled") == "false":
            log(f"✔ Botón +1 disponible (intento {attempt+1})", "ok")
            break
        log(f"… recargando ({attempt+1}/30)", "live")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(600)
    else:
        log("✘ Botón +1 no disponible tras 30 intentos", "err")
        return

    # +1
    await btn.click()
    await page.wait_for_timeout(600)
    log("✔ +1 pulsado", "ok")

    # Continue
    await page.evaluate('''() => {
        document.querySelector('[data-testid="checkout-btn"]')
            ?.dispatchEvent(new MouseEvent("click", {bubbles:true, cancelable:true}));
    }''')
    await page.wait_for_timeout(2000)
    log("✔ Continue", "ok")

    # Formulario
    async def fill(sel, val, label):
        try:
            el = await page.wait_for_selector(sel, timeout=5000)
            await el.click()
            await el.type(val, delay=50)
            log(f"✔ {label}", "ok")
        except Exception as e:
            log(f"✘ {label}: {e}", "err")

    await fill('input[autocomplete="given-name"]', cfg['first_name'], "Nombre")
    await fill('input[autocomplete="family-name"]', cfg['last_name'],  "Apellido")
    await fill('input[type="email"]',               cfg['email'],      "Email")
    await fill('input[type="tel"]',                 cfg['mobile'],     "Móvil")

    # Turnstile
    log("Esperando Cloudflare Turnstile…", "live")
    for i in range(20):
        await page.wait_for_timeout(1000)
        ready = await page.evaluate('''() => {
            const b = document.querySelector('[data-testid="buyer-info-submit"]');
            return b && b.getAttribute("aria-disabled") !== "true" && !b.disabled;
        }''')
        if ready:
            log(f"✔ Turnstile OK ({i+1}s)", "ok")
            break
    else:
        log("⚠ Turnstile no resuelto, intentando igual", "live")

    # Continue to Ticket info
    try:
        submit = await page.wait_for_selector('[data-testid="buyer-info-submit"]', timeout=5000)
        await submit.click()
        log("✔ Continue to Ticket info", "ok")
    except Exception as e:
        log(f"✘ buyer-info-submit: {e}", "err")
        return

    await page.wait_for_timeout(2000)

    # Dropdowns
    try:
        await page.wait_for_selector('[data-testid="field-content"]', timeout=8000)
    except:
        log("✘ Dropdowns no aparecieron", "err")
        return

    await select_dropdown(page, 0, cfg.get('student_type',  'International'), log)
    await select_dropdown(page, 1, cfg.get('student_level', 'Undergraduate'),  log)
    await select_dropdown(page, 2, cfg.get('usu_member',    'No'),             log)
    await page.wait_for_timeout(500)

    # Continue final
    try:
        final = await page.wait_for_selector('[data-testid="ticket-info-submit"]', timeout=5000)
        await final.click()
        log("✔ Continue final", "ok")
    except Exception as e:
        log(f"✘ ticket-info-submit: {e}", "err")
        return

    # Resultado
    try:
        await page.wait_for_url("**/complete**", timeout=15000)
        log(f"✅ ¡TICKET CONSEGUIDO! {page.url}", "ok")
    except:
        log(f"⚠ URL final: {page.url}", "err")
        await page.screenshot(path="resultado.png", full_page=True)
        log("📸 resultado.png guardado", "live")


async def run_bot(cfg, log):
    """Punto de entrada principal — llamado desde app.py o standalone."""
    now = datetime.now()
    log(f"🤖 Food Hub Bot — {now.strftime('%A %d/%m/%Y %H:%M:%S')}", "live")

    if now.weekday() > 4:
        log("Hoy es fin de semana. No hay tickets.", "err")
        return

    async with AsyncCamoufox(headless=False, geoip=True) as browser:
        slots = await fetch_today_slots(browser, log)
        if not slots:
            log("No se encontraron slots para hoy.", "err")
            return

        slot = get_next_slot(slots)
        if not slot:
            log("Todos los slots de hoy ya pasaron.", "err")
            return

        log(f"🎯 Próxima tanda: {slot['event_hour']:02d}:{slot['event_min']:02d} "
            f"(abre {slot['open_time'].strftime('%H:%M')})", "live")

        await book_ticket(browser, slot, cfg, log)


# Standalone (sin GUI)
if __name__ == "__main__":
    import json
    from pathlib import Path
    cfg_path = Path(__file__).parent / "config.json"
    if not cfg_path.exists():
        print("No hay config.json. Ejecuta app.py para configurar.")
        exit(1)
    with open(cfg_path) as f:
        cfg = json.load(f)

    def log(msg, tag=""):
        print(msg)

    asyncio.run(run_bot(cfg, log))
