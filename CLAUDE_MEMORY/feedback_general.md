---
name: Preferencias y feedback del usuario
description: Comportamientos y preferencias de trabajo aprendidos en este proyecto
type: feedback
originSessionId: 6cc70a32-39ef-4f02-a317-2763e564e812
---
**Autorización para cambios profundos:** El usuario indicó explícitamente "si necesitas modificar la base de datos o el core del programa o la lógica, hazlo". No pedir confirmación para cambios en DB, server/, o lógica de negocio en este proyecto.
**Why:** El usuario confía en que se tomen decisiones técnicas sin aprobación por cada cambio menor.
**How to apply:** Modificar server/, DB migrations, y lógica del frontend directamente sin preguntar permiso.

---

**UI minimalista:** El usuario prefiere interfaces limpias y simples. Rechazó tablas complejas con muchas columnas, paneles de resumen con contadores duplicados, y breadcrumbs.
**Why:** Quiere que la pantalla sea utilizable para monitoreo en tiempo real, no una herramienta de análisis.
**How to apply:** Priorizar claridad y densidad de información útil. Evitar elementos decorativos o redundantes.

---

**Build y deploy inmediatos:** El usuario espera que después de cada cambio de código se haga `npm run build` y se despliegue al servidor sin que él tenga que pedirlo.
**Why:** Flujo de trabajo práctico — ver resultados inmediatamente.
**How to apply:** Siempre terminar con build → pscp → docker compose restart.

---

**Patrón de nombres de monitores:** Los monitores siguen el patrón `"{DeviceName} - {SensorName}"` (ej. "Fortigate-Duran - CPU %"). La parte antes de " - " es el equipo, la parte después es el sensor.
**Why:** Es la convención establecida para el proyecto NAGSA.
**How to apply:** Al parsear nombres de monitores, usar `indexOf(" - ")` como separador.
