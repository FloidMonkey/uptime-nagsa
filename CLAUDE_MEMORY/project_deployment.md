---
name: uptime-nagsa deployment pipeline
description: Cómo desplegar cambios del frontend y backend al servidor de laboratorio
type: project
originSessionId: 6cc70a32-39ef-4f02-a317-2763e564e812
---
## Estrategia de despliegue

El contenedor usa imagen upstream `louislam/uptime-kuma:2` sin git. Los cambios se despliegan montando volúmenes en `~/uptime-nagsa/docker-compose.yml`.

### Frontend (Vue)
1. `npm run build` en `D:\OneDrive - Corporativo\CLAUDE\UPTIME`
2. `plink -pw "Danilo2909" jperez@10.20.29.5 "rm -rf ~/uptime-nagsa/dist && mkdir -p ~/uptime-nagsa/dist"`
3. `pscp -r -pw "Danilo2909" "D:\...\dist\assets" jperez@10.20.29.5:/home/jperez/uptime-nagsa/dist/`
4. `pscp -pw "Danilo2909" dist\index.html dist\manifest.json dist\icon.svg dist\serviceWorker.js jperez@10.20.29.5:/home/jperez/uptime-nagsa/dist/`
5. `plink -pw "Danilo2909" jperez@10.20.29.5 "cd ~/uptime-nagsa && docker compose restart uptime-kuma"`

El volumen `./dist:/app/dist` en docker-compose.yml hace que el contenedor sirva el build local.

### Backend (server/)
Los archivos JS del servidor se montan como volúmenes individuales en docker-compose.yml:
```yaml
- ./server/monitor-types/snmp.js:/app/server/monitor-types/snmp.js
- ./server/socket-handlers/snmp-socket-handler.js:/app/server/socket-handlers/snmp-socket-handler.js
- ./server/model/monitor.js:/app/server/model/monitor.js
- ./server/server.js:/app/server/server.js
- ./db/knex_migrations/...
```
Copiar con pscp + restart contenedor.

**Why:** No hay git en el servidor ni en el contenedor. La imagen upstream no se puede modificar directamente, por eso se montan volúmenes.

**How to apply:** Siempre que se edite un archivo frontend → rebuild + pscp + restart. Siempre que se edite un archivo backend → pscp del archivo específico + restart.
