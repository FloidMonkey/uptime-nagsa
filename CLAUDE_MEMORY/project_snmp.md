---
name: SNMP features implementadas
description: Funcionalidades SNMP agregadas al fork uptime-nagsa
type: project
originSessionId: 6cc70a32-39ef-4f02-a317-2763e564e812
---
## Archivos modificados/creados para SNMP

### Backend
- `server/monitor-types/snmp.js` — Agrega campo `snmpUnit` al heartbeat msg: `SNMP OK: {valor} {unidad}`
- `server/socket-handlers/snmp-socket-handler.js` — Nuevo handler con eventos:
  - `snmpWalk`: walk de subtree SNMP, devuelve hasta 500 OIDs
  - `getSnmpTemplates`: lee JSONs de `server/snmp-templates/`
  - `applySnmpTemplate`: crea monitores desde template JSON
- `server/model/monitor.js` — Agrega `snmpUnit` al modelo serializado
- `server/server.js` — Registra `snmpSocketHandler(socket, server)`
- `db/knex_migrations/2026-04-24-0001-snmp-unit.js` — Migración que agrega columna `snmp_unit` a tabla `monitor`

### Templates SNMP (server/snmp-templates/)
- `linux-server.json` — Ping + Uptime + CPU load 1min + RAM available (SNMPv2c)
- `cisco-switch.json` — Ping + Uptime + CPU 5s + Free RAM (SNMPv2c)
- `generic-switch.json` — Ping + Uptime + Traffic In/Out port 1 (SNMPv2c)
- `fortigate.json` — Ping + Uptime + CPU% + RAM% (SNMPv3)

### Frontend
- `src/pages/EditMonitor.vue` — Browse OIDs button, Unit field, Apply Device Template button
- `src/icon.js` — `faNetworkWired` agregado

**Why:** El usuario monitorea dispositivos de red NAGSA via SNMP. Se necesitaba OID browser, templates de dispositivos por fabricante, y unidades en los mensajes de heartbeat.

**How to apply:** Al editar monitores SNMP, los campos `snmpOid`, `snmpUnit`, `snmpVersion` están disponibles. net-snmp v3.26.1 requiere `NODE_OPTIONS=--openssl-legacy-provider` para DES.
