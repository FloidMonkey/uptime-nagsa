# uptime-nagsa — Contexto del Proyecto

## Descripción
Fork de Uptime Kuma 2.2.1 personalizado para NAGSA (Monitoreo de Red).
Repositorio: https://github.com/FloidMonkey/uptime-nagsa

## Servidor de Despliegue (Laboratorio)

| Campo | Valor |
|-------|-------|
| **Hostname** | uptimenagsa |
| **IP** | 10.20.29.5 |
| **OS** | Ubuntu 26.04 LTS (Resolute) |
| **Kernel** | 7.0.0-14-generic |
| **CPU** | 4 vCPU |
| **RAM** | 3.3 GB |
| **Disco** | 40 GB (LVM, 24 GB montados en /) |
| **Usuario** | jperez |
| **Proxmox VM ID** | — |

## Stack de Servicios

| Servicio | Imagen | Puerto | Rol |
|---------|--------|--------|-----|
| uptime-nagsa | louislam/uptime-kuma:2 | 3001 | Monitoreo / UI |
| uptime-mysql | mysql:8.0 | 3306 (interno) | Base de datos |

## Arquitectura de Datos

```
Uptime Kuma (sensing)
       ↓
   MySQL 8.0
       ↓
   Grafana (servidor separado) — conexión directa a MySQL
```

Grafana se conecta directamente a MySQL como data source nativo (no usa Prometheus).

## Rutas en el Servidor

```
~/uptime-nagsa/
├── docker-compose.yml
└── data/
    ├── uptime/     # datos de Uptime Kuma
    └── mysql/      # datos de MySQL
```

## Credenciales MySQL

| Campo | Valor |
|-------|-------|
| **Host** (desde contenedores) | `mysql` |
| **Host** (desde Grafana externo) | `10.20.29.5` |
| **Port** | `3306` |
| **Database** | `uptime_nagsa` |
| **Username** | `uptime` |
| **Password** | `uptime2026*` |
| **Root Password** | `root2026*` |

## Acceso a Uptime Kuma

- **UI Web**: http://10.20.29.5:3001
- **Métricas Prometheus**: http://10.20.29.5:3001/metrics (Basic Auth)

## Docker Compose

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: uptime-mysql
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: uptime_nagsa
      MYSQL_USER: uptime
      MYSQL_PASSWORD: uptime2026*
      MYSQL_ROOT_PASSWORD: root2026*
    volumes:
      - ./data/mysql:/var/lib/mysql
    networks:
      - uptime-net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "uptime", "-puptime2026*"]
      interval: 15s
      timeout: 10s
      retries: 10
      start_period: 120s

  uptime-kuma:
    image: louislam/uptime-kuma:2
    container_name: uptime-nagsa
    restart: unless-stopped
    depends_on:
      mysql:
        condition: service_healthy
    volumes:
      - ./data/uptime:/app/data
    ports:
      - "3001:3001"
    networks:
      - uptime-net

networks:
  uptime-net:
    driver: bridge
```

## Comandos Útiles

```bash
# Ver estado de contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Reiniciar servicios
docker compose restart

# Parar todo
docker compose down

# Levantar todo
docker compose up -d

# Conectarse a MySQL
docker exec -it uptime-mysql mysql -u uptime -puptime2026* uptime_nagsa

# Sesión tmux
tmux attach -t uptime
```

## Tipos de Monitores Disponibles (31)

HTTP/HTTPS, Keyword, JSON Query, Real Browser, TCP/Port, Ping (ICMP),
DNS, WebSocket, MQTT, Kafka, RabbitMQ, SMTP, gRPC, SIP, MySQL, PostgreSQL,
SQL Server, Oracle, MongoDB, Redis, Docker, SNMP, RADIUS, System Service,
Tailscale Ping, GameDig, Steam, Push, Manual, Globalping, Group.

## Pendientes

- [ ] Exponer puerto 3306 de MySQL hacia Grafana externo
- [ ] Configurar data source MySQL en Grafana
- [ ] Crear dashboard Grafana para uptime y latencia
- [ ] Expandir LVM del disco (24 GB → 40 GB)
- [ ] Configurar IP fija (actualmente por DHCP)
- [ ] Agregar monitores iniciales de red NAGSA
