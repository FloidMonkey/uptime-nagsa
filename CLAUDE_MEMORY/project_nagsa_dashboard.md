---
name: NagsaDashboard - dashboard PRTG-style
description: Estado actual y lógica del dashboard principal estilo PRTG en src/pages/NagsaDashboard.vue
type: project
---
## Estado actual (funciona)

Archivo: `src/pages/NagsaDashboard.vue`
Ruta: `/nagsa-dashboard` (redirige desde Entry.vue al login)
Ruta settings: `/nagsa-settings` → `src/pages/NagsaSettings.vue`

## Árbol jerárquico: Grupos → Equipos → Sensores

**3 niveles:**
1. **Grupos lógicos** — monitores `type:"group"` SIN `_nd:1` en description
2. **Equipos explícitos** — monitores `type:"group"` CON `description: '{"_nd":1,...}'`
3. **Equipos virtuales** — agrupación automática por hostname de sensores sin equipo explícito
4. **Sensores** — monitores non-group, hijos de un equipo o con mismo hostname

**Connector lines jerárquicos** — líneas ├─ └─ │ estilo árbol generadas con `tracks[]` y `isLast` por ítem.

## Lógica de grupos y equipos

```javascript
// Equipo explícito = grupo con flag _nd
parseDeviceMeta(description) {
    const d = JSON.parse(description || "{}");
    return d["_nd"] === 1 ? d : null;
}
// description almacena: { _nd:1, brand, model, notes, icon }
```

**Equipo virtual:** Si sensores sin equipo explícito comparten hostname → se agrupan en equipo virtual.

**Adopción automática:** Al convertir equipo virtual → explícito, sus sensores se re-parentan al nuevo ID via `editMonitor`.

## Iconos de dispositivos

- **Built-in:** rutas estáticas `/nagsa/icons/devices/` y `/nagsa/icons/vendors/` (SVGs en `public/`)
- **Cargados:** base64 con ID `ico-xxx`, almacenados en MySQL via `nagsa:settings:save`
- **Resolución:** `getDeviceIcon(iconId)` → si inicia con `/` usa path directo, si no busca en `knownIcons`

```javascript
// En description del equipo:
icon: "/nagsa/icons/vendors/Cisco.svg"  // built-in
icon: "ico-1234-abc"                     // uploaded
```

## Iconos y marcas (persistencia MySQL)

Socket events: `nagsa:settings:get` / `nagsa:settings:save`
Server keys: `nagsa_icons` (JSON array) / `nagsa_brands` (JSON array)
Cargados en `mounted()` y al abrir modal de equipo.

## Fixes aplicados en esta sesión

- **Redirect:** `server.js` línea ~267 → `/nagsa-dashboard`; `uptime-kuma-server.js` → `entryPage = "nagsa-dashboard"`
- **Title link:** `Layout.vue` dos `router-link` cambiados a `/nagsa-dashboard`
- **Grupo incorrecto:** bug `d.raw` undefined en `groupedTree` → corregido a `d.parent ?? null`
- **retryInterval error:** payload `saveDevice` ahora incluye `retryInterval: 60` explícitamente para evitar heredar 0 del grupo existente
- **accepted_statuscodes crash:** server.js null check antes de `.every()`

## Pendiente / mejoras futuras

- Vista tabla de sensores al seleccionar equipo (estilo PRTG)
- Notificaciones por equipo
- Historial de uptime por equipo

**Why:** UI estilo PRTG Network Monitor para NAGSA.
**How to apply:** Respetar jerarquía Grupos → Equipos → Sensores. Equipo = group monitor con `_nd:1`.
