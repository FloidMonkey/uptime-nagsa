---
name: uptime-nagsa deployment
description: Proyecto de monitoreo de red NAGSA — servidor lab, stack Docker, arquitectura Uptime Kuma + MySQL + Grafana
type: project
originSessionId: 6cc70a32-39ef-4f02-a317-2763e564e812
---
Servidor de laboratorio en Proxmox con Ubuntu 26.04. Stack: Uptime Kuma 2.2.1 (fork: uptime-nagsa) + MySQL 8.0 en Docker Compose. Grafana en servidor separado conecta directo a MySQL como data source nativo (sin Prometheus).

**Why:** Uptime Kuma se usa solo para sensing/monitoreo. La visualización avanzada va en Grafana. Se eligió MySQL directo para evitar la complejidad de Prometheus.

**How to apply:** Conexión MySQL: host 10.20.29.5:3306, DB uptime_nagsa, user uptime, pw uptime2026*. Puerto 3306 aún no expuesto externamente (pendiente). Para cambios en el frontend: build local → pscp → restart contenedor. Para cambios en el backend (server/): montar via volumen en docker-compose.yml.

Servidor: IP 10.20.29.5, usuario jperez, pw Danilo2909, tmux session "uptime", proyecto en ~/uptime-nagsa/.
UI Uptime Kuma: http://10.20.29.5:3001
GitHub: https://github.com/FloidMonkey/uptime-nagsa
