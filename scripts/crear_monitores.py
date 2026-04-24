from uptime_kuma_api import UptimeKumaApi
import time

api = UptimeKumaApi("http://localhost:3001")
api.login("jperez", "Danilo2909")

SNMP_V3 = {
    "snmpVersion": "3",
    "snmpUsername": "SNMP_Nagsa",
    "snmpAuthProtocol": "MD5",
    "snmpAuthPass": "N@gS@2k26",
    "snmpPrivProtocol": "DES",
    "snmpPrivPass": "N@gS@2k26",
}

def create_group(name):
    res = api.add_monitor(type="group", name=name)
    time.sleep(0.5)
    return res["monitorID"]

def create_ping(name, hostname, parent=None):
    params = dict(type="ping", name=name, hostname=hostname, interval=60, maxretries=3)
    if parent:
        params["parent"] = parent
    api.add_monitor(**params)
    time.sleep(0.5)

def create_snmp(name, hostname, oid, condition=">=", value="0", parent=None):
    params = dict(
        type="snmp",
        name=name,
        hostname=hostname,
        port=161,
        snmpOid=oid,
        snmpCondition=condition,
        snmpControlValue=value,
        interval=60,
        maxretries=3,
        **SNMP_V3
    )
    if parent:
        params["parent"] = parent
    api.add_monitor(**params)
    time.sleep(0.5)

# ── GRUPOS ──────────────────────────────────────────────────────────────
print("Creando grupos...")
g_fortigates   = create_group("Fortigates")
g_switch_corp  = create_group("Switch-Corporativo")
g_switches     = create_group("Switches-Acceso")
g_impresoras   = create_group("Impresoras-Terminales")
g_otros        = create_group("Otros")

# ── FORTIGATES ──────────────────────────────────────────────────────────
print("Creando monitores Fortigates...")
create_ping("Fortigate-Duran - Ping",          "192.168.104.254", g_fortigates)
create_snmp("Fortigate-Duran - Uptime",        "192.168.104.254", ".1.3.6.1.2.1.1.3.0",            ">=", "0",   g_fortigates)
create_snmp("Fortigate-Duran - CPU %",         "192.168.104.254", ".1.3.6.1.4.1.12356.101.4.1.3.0","<=", "100", g_fortigates)
create_snmp("Fortigate-Duran - RAM %",         "192.168.104.254", ".1.3.6.1.4.1.12356.101.4.1.4.0","<=", "100", g_fortigates)

create_ping("Fortigate-Manta - Ping",          "10.23.1.1",       g_fortigates)
create_snmp("Fortigate-Manta - Uptime",        "10.23.1.1",       ".1.3.6.1.2.1.1.3.0",            ">=", "0",   g_fortigates)
create_snmp("Fortigate-Manta - RAM %",         "10.23.1.1",       ".1.3.6.1.4.1.12356.101.4.1.4.0","<=", "100", g_fortigates)

create_ping("Fortigate-Miami - Ping",          "10.24.0.1",       g_fortigates)
create_ping("Fortigate-Quito - Ping",          "192.168.148.1",   g_fortigates)

create_ping("Fortigate-Plaza_Proyecto - Ping", "192.168.112.1",   g_fortigates)
create_snmp("Fortigate-Plaza_Proyecto - Uptime","192.168.112.1",  ".1.3.6.1.2.1.1.3.0",            ">=", "0",   g_fortigates)
create_snmp("Fortigate-Plaza_Proyecto - RAM %", "192.168.112.1",  ".1.3.6.1.4.1.12356.101.4.1.4.0","<=", "100", g_fortigates)

# ── SWITCH CORPORATIVO ──────────────────────────────────────────────────
print("Creando monitores Switch Corporativo...")
create_ping("Switch-Corporativo - Ping",   "192.168.106.219", g_switch_corp)
create_snmp("Switch-Corporativo - Uptime", "192.168.106.219", ".1.3.6.1.2.1.1.3.0", ">=", "0", g_switch_corp)

interfaces = [
    ("CNT_Duralum",          ".1.3.6.1.2.1.31.1.1.1.6.49162",  ".1.3.6.1.2.1.31.1.1.1.10.49162"),
    ("gigabitEthernet 1/0/14",".1.3.6.1.2.1.31.1.1.1.6.49166", ".1.3.6.1.2.1.31.1.1.1.10.49166"),
    ("gigabitEthernet 1/0/18",".1.3.6.1.2.1.31.1.1.1.6.49170", ".1.3.6.1.2.1.31.1.1.1.10.49170"),
    ("gigabitEthernet 1/0/19",".1.3.6.1.2.1.31.1.1.1.6.49171", ".1.3.6.1.2.1.31.1.1.1.10.49171"),
    ("gigabitEthernet 1/0/20",".1.3.6.1.2.1.31.1.1.1.6.49172", ".1.3.6.1.2.1.31.1.1.1.10.49172"),
    ("gigabitEthernet 1/0/21",".1.3.6.1.2.1.31.1.1.1.6.49173", ".1.3.6.1.2.1.31.1.1.1.10.49173"),
    ("gigabitEthernet 1/0/22",".1.3.6.1.2.1.31.1.1.1.6.49174", ".1.3.6.1.2.1.31.1.1.1.10.49174"),
    ("gigabitEthernet 1/0/23",".1.3.6.1.2.1.31.1.1.1.6.49175", ".1.3.6.1.2.1.31.1.1.1.10.49175"),
    ("gigabitEthernet 1/0/24",".1.3.6.1.2.1.31.1.1.1.6.49176", ".1.3.6.1.2.1.31.1.1.1.10.49176"),
    ("gigabitEthernet 1/0/26",".1.3.6.1.2.1.31.1.1.1.6.49178", ".1.3.6.1.2.1.31.1.1.1.10.49178"),
    ("gigabitEthernet 1/0/27",".1.3.6.1.2.1.31.1.1.1.6.49179", ".1.3.6.1.2.1.31.1.1.1.10.49179"),
    ("gigabitEthernet 1/0/28",".1.3.6.1.2.1.31.1.1.1.6.49180", ".1.3.6.1.2.1.31.1.1.1.10.49180"),
    ("HV01-MAC",             ".1.3.6.1.2.1.31.1.1.1.6.49155",  ".1.3.6.1.2.1.31.1.1.1.10.49155"),
    ("Nas116",               ".1.3.6.1.2.1.31.1.1.1.6.49163",  ".1.3.6.1.2.1.31.1.1.1.10.49163"),
    ("NVR",                  ".1.3.6.1.2.1.31.1.1.1.6.49160",  ".1.3.6.1.2.1.31.1.1.1.10.49160"),
    ("NVR_SISTEMAS",         ".1.3.6.1.2.1.31.1.1.1.6.49157",  ".1.3.6.1.2.1.31.1.1.1.10.49157"),
    ("NVR2",                 ".1.3.6.1.2.1.31.1.1.1.6.49161",  ".1.3.6.1.2.1.31.1.1.1.10.49161"),
    ("PROXMOX",              ".1.3.6.1.2.1.31.1.1.1.6.49159",  ".1.3.6.1.2.1.31.1.1.1.10.49159"),
    ("proxmox2",             ".1.3.6.1.2.1.31.1.1.1.6.49156",  ".1.3.6.1.2.1.31.1.1.1.10.49156"),
    ("Proxmoxlab",           ".1.3.6.1.2.1.31.1.1.1.6.49153",  ".1.3.6.1.2.1.31.1.1.1.10.49153"),
    ("serverdesconocido",    ".1.3.6.1.2.1.31.1.1.1.6.49164",  ".1.3.6.1.2.1.31.1.1.1.10.49164"),
    ("SRV_MODULA",           ".1.3.6.1.2.1.31.1.1.1.6.49158",  ".1.3.6.1.2.1.31.1.1.1.10.49158"),
    ("SRV203-P1",            ".1.3.6.1.2.1.31.1.1.1.6.49165",  ".1.3.6.1.2.1.31.1.1.1.10.49165"),
    ("SRV203-P2",            ".1.3.6.1.2.1.31.1.1.1.6.49167",  ".1.3.6.1.2.1.31.1.1.1.10.49167"),
    ("SRV203-P3",            ".1.3.6.1.2.1.31.1.1.1.6.49169",  ".1.3.6.1.2.1.31.1.1.1.10.49169"),
    ("srvhv01-02",           ".1.3.6.1.2.1.31.1.1.1.6.49154",  ".1.3.6.1.2.1.31.1.1.1.10.49154"),
    ("SWITCH-SERVERS",       ".1.3.6.1.2.1.31.1.1.1.6.49168",  ".1.3.6.1.2.1.31.1.1.1.10.49168"),
    ("UPLINK",               ".1.3.6.1.2.1.31.1.1.1.6.49177",  ".1.3.6.1.2.1.31.1.1.1.10.49177"),
    ("Vlan-interface1",      ".1.3.6.1.2.1.31.1.1.1.6.1",      ".1.3.6.1.2.1.31.1.1.1.10.1"),
    ("Vlan-interface10",     ".1.3.6.1.2.1.31.1.1.1.6.10",     ".1.3.6.1.2.1.31.1.1.1.10.10"),
]

for name, oid_in, oid_out in interfaces:
    create_snmp(f"{name} - Traffic In",  "192.168.106.219", oid_in,  ">=", "0", g_switch_corp)
    create_snmp(f"{name} - Traffic Out", "192.168.106.219", oid_out, ">=", "0", g_switch_corp)

# ── SWITCHES DE ACCESO ──────────────────────────────────────────────────
print("Creando monitores Switches Acceso...")
switches_acceso = [
    ("SW_PINTURA",        "192.168.104.61"),
    ("SW_LABORATORIO",    "192.168.104.51"),
    ("SW_RACK_PRINCIPAL", "192.168.104.145"),
    ("SW_BODEGA_ACC",     "192.168.104.147"),
    ("SW_SCHIRMER",       "192.168.105.125"),
    ("SW_SITE_48P",       "192.168.107.21"),
    ("SW_ARIEL",          "192.168.107.182"),
]
for name, ip in switches_acceso:
    create_ping(f"{name} - Ping",   ip, g_switches)
    create_snmp(f"{name} - Uptime", ip, ".1.3.6.1.2.1.1.3.0", ">=", "0", g_switches)

# ── IMPRESORAS Y TERMINALES ─────────────────────────────────────────────
print("Creando monitores Impresoras y Terminales...")
impresoras = [
    ("Zebra-DURALUM",    "192.168.104.125"),
    ("BROTHER_DURALUM",  "192.168.104.74"),
    ("Zebra-PROALUM",    "192.168.105.200"),
    ("BROTHER_PROALUM",  "192.168.106.128"),
    ("Zebra-SISTEMAS",   "192.168.106.89"),
    ("Zebra-107",        "192.168.107.216"),
]
for name, ip in impresoras:
    create_ping(f"{name} - Ping", ip, g_impresoras)

# ── OTROS ───────────────────────────────────────────────────────────────
print("Creando monitores Otros...")
create_ping("Gateway - Ping",          "10.20.29.1",      g_otros)
create_ping("KRAMER_GERENCIA - Ping",  "192.168.107.156", g_otros)
create_ping("RAD_UNIFI_CLIENT - Ping", "192.178.107.150", g_otros)

api.disconnect()
print("✅ Todos los monitores creados exitosamente")
