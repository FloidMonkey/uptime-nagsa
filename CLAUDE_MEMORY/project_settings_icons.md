---
name: NagsaSettings - iconos y marcas
description: Página de configuración /nagsa-settings con upload de iconos y gestión de marcas
type: project
---
## Archivos

- `src/pages/NagsaSettings.vue` — página de configuración
- `src/nagsa-icon-library.js` — exports DEVICE_ICONS + VENDOR_ICONS (arrays de { file, label })
- `public/nagsa/icons/devices/` — 32 SVGs dispositivos (A_Server_*, Switch_*, Device_*, etc.)
- `public/nagsa/icons/vendors/` — 61 SVGs fabricantes (Cisco, Fortinet, MikroTik, etc.)

## Persistencia MySQL (no localStorage)

```js
// Server: server.js
socket.on("nagsa:settings:get", async (cb) => {
    const icons  = JSON.parse((await Settings.get("nagsa_icons"))  || "[]");
    const brands = JSON.parse((await Settings.get("nagsa_brands")) || "[]");
    cb({ ok: true, icons, brands });
});
socket.on("nagsa:settings:save", async (data, cb) => {
    if (data.icons  !== undefined) await Settings.set("nagsa_icons",  JSON.stringify(data.icons),  "nagsa");
    if (data.brands !== undefined) await Settings.set("nagsa_brands", JSON.stringify(data.brands), "nagsa");
    cb({ ok: true });
});
```

## Iconos cargados (estructura)

```js
{ id: "ico-<timestamp>-<random>", name: "nombre-archivo", data: "data:image/png;base64,..." }
```

Límite: 256 KB por archivo. Acepta PNG, SVG, JPG, GIF.

## Marcas

Array de strings ordenado alfabéticamente. Se añaden automáticamente al guardar equipo con marca nueva.
Usadas via `<datalist id="nagsa-brand-list">` en el modal de equipo (autocomplete nativo HTML5).

**Why:** Iconos y marcas deben ser accesibles desde cualquier navegador/equipo, no por-browser.
**How to apply:** Siempre usar socket events para leer/guardar, nunca localStorage para estos datos.
