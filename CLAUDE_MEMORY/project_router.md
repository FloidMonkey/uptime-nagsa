---
name: Cambios críticos en router y Entry.vue
description: Correcciones de routing para que NagsaDashboard sea la página principal
type: project
originSessionId: 6cc70a32-39ef-4f02-a317-2763e564e812
---
## src/router.js — posición de /nagsa-dashboard

NagsaDashboard DEBE ser hijo directo de `Layout`, NO hijo de `Dashboard`.

`Dashboard` tiene un MonitorList sidebar en la columna izquierda + `<router-view>` en la derecha. Si NagsaDashboard se anida dentro de Dashboard, aparece el sidebar de Uptime Kuma a la izquierda.

```javascript
// CORRECTO — en src/router.js:
{
    path: "/empty",
    component: Layout,
    children: [
        { path: "", component: Dashboard, children: [...] },
        { path: "/nagsa-dashboard", component: NagsaDashboard },  // ← aquí, hermano de Dashboard
    ]
}
```

## src/pages/Entry.vue — redirect al login

Ambas ocurrencias de `this.$router.push("/dashboard")` cambiadas a `this.$router.push("/nagsa-dashboard")`.

**Why:** Sin este cambio, al hacer login redirigía a /dashboard (UI original de Uptime Kuma con sidebar). La ruta /nagsa-dashboard da pantalla completa sin sidebar.

**How to apply:** Si en el futuro se mueven rutas, verificar siempre que /nagsa-dashboard esté al nivel de sibling de Dashboard bajo Layout.
