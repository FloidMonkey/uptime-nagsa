<template>
    <div class="nd-wrap">

        <!-- ── Status bar ── -->
        <div class="nd-bar">
            <div class="nd-stat nd-dn" :class="{ active: sf==='down' }" @click="toggleSf('down')">
                <span class="nd-num">{{ cDown }}</span><span class="nd-lbl">Down</span>
            </div>
            <div class="nd-stat nd-wn" :class="{ active: sf==='warn' }" @click="toggleSf('warn')">
                <span class="nd-num">{{ cPending }}</span><span class="nd-lbl">Warning</span>
            </div>
            <div class="nd-stat nd-up" :class="{ active: sf==='up' }" @click="toggleSf('up')">
                <span class="nd-num">{{ cUp }}</span><span class="nd-lbl">Up</span>
            </div>
            <div class="nd-stat nd-ps" :class="{ active: sf==='paused' }" @click="toggleSf('paused')">
                <span class="nd-num">{{ cPaused }}</span><span class="nd-lbl">Paused</span>
            </div>
            <div class="nd-bar-right">
                <span class="nd-total">{{ allMonitors.length }} sensores · {{ allDeviceMonitors.length }} equipos · {{ allLogicalGroups.length }} grupos</span>
            </div>
        </div>

        <!-- ── Panel ── -->
        <div class="nd-panel">
            <div class="tree-bar">
                <input v-model="q" class="tree-filter" placeholder="Filtrar grupos, equipos o sensores…" />
                <button class="tree-btn" title="Expandir todo" @click="expandAll">⊞</button>
                <button class="tree-btn" title="Colapsar todo" @click="collapseAll">⊟</button>
                <button class="tree-btn tree-btn-grp" @click="startAddGroup">+ Grupo</button>
                <button class="tree-btn tree-btn-dev" @click="openDeviceModal(null, null)">+ Equipo</button>
                <button class="tree-btn tree-btn-sensor" @click="openSensorModal(null, null)">+ Sensor</button>
                <router-link to="/nagsa-settings" class="tree-btn tree-btn-cfg" title="Configuración NAGSA">⚙</router-link>
            </div>

            <div class="tree-scroll">

                <!-- Root -->
                <div class="t-root">
                    <span class="t-root-ico">◉</span>
                    <span class="t-root-label">Uptime Nagsa</span>
                    <span v-if="cDown" class="root-pill root-dn">{{ cDown }} down</span>
                    <span v-if="cUp"   class="root-pill root-up">{{ cUp }} up</span>
                </div>

                <!-- New group inline row -->
                <div v-if="addingGroup" class="new-grp-row">
                    <span class="grp-icon-sm">📁</span>
                    <select v-model="newGroupParent" class="grp-parent-sel">
                        <option :value="null">Raíz (sin grupo padre)</option>
                        <option v-for="g in allLogicalGroupsFlat" :key="g.id" :value="g.id">{{ g.indentedName }}</option>
                    </select>
                    <input ref="newGroupInput" v-model="newGroupName" class="grp-inline-input"
                           placeholder="Nombre del grupo…"
                           @keyup.enter="confirmAddGroup" @keyup.esc="cancelAddGroup" />
                    <button class="grp-act-btn ok" @click="confirmAddGroup">✓</button>
                    <button class="grp-act-btn cancel" @click="cancelAddGroup">✕</button>
                </div>

                <div v-if="!allMonitors.length && !allDeviceMonitors.length" class="t-loading">Cargando monitores…</div>

                <!-- ── Flat render items ── -->
                <template v-for="item in renderItems" :key="item.key">

                    <!-- Logical group header -->
                    <div
                        v-if="item.type === 'group'"
                        class="grp-hdr"
                        :class="[grpStCls(item.data), 'depth-' + item.depth]"
                        @click="toggleGrp(item.data.key)">
                        <span class="nd-tracks" aria-hidden="true">
                            <span v-for="(cont, j) in item.tracks" :key="j" class="nd-track-base" :class="cont ? 'nd-track-v' : 'nd-track-e'"></span>
                            <span class="nd-conn" :class="item.isLast ? 'nd-conn-last' : 'nd-conn-mid'"></span>
                        </span>
                        <span class="grp-chevron">{{ expandedGrp[item.data.key] ? '▾' : '▸' }}</span>
                        <span class="grp-icon-sm">{{ item.data.id === null ? '📂' : (item.depth > 0 ? '📂' : '📁') }}</span>

                        <template v-if="renamingGroup === item.data.id">
                            <input ref="renameInput" v-model="renameValue" class="grp-inline-input"
                                   @keyup.enter="confirmRename(item.data)" @keyup.esc="cancelRename" @click.stop />
                            <button class="grp-act-btn ok" @click.stop="confirmRename(item.data)">✓</button>
                            <button class="grp-act-btn cancel" @click.stop="cancelRename">✕</button>
                        </template>
                        <template v-else>
                            <span class="grp-name"
                                  :title="item.data.id !== null ? 'Doble clic para renombrar' : ''"
                                  @dblclick.stop="item.data.id !== null && startRename(item.data)">{{ item.data.name }}</span>
                            <span class="grp-badge" :class="grpStCls(item.data)">{{ grpStLbl(item.data) }}</span>
                            <span class="grp-count">{{ item.data.totalSensors }} sens · {{ countDevicesInGroup(item.data) }} equipos</span>
                            <template v-if="item.data.id !== null">
                                <select class="dev-grp-sel" title="Mover grupo a…"
                                        @change="onMoveGroup(item.data, $event)" @click.stop>
                                    <option value="">🗂 Mover…</option>
                                    <optgroup label="Dentro de">
                                        <option v-for="g in groupMoveOptions(item.data)" :key="g.id" :value="g.id"
                                                :disabled="g.id === (item.data.raw.parent ?? null)">{{ g.indentedName }}</option>
                                    </optgroup>
                                    <option value="__none__" :disabled="(item.data.raw.parent ?? null) === null">A raíz</option>
                                </select>
                                <button class="grp-act-icon" title="Agregar equipo a este grupo"
                                        @click.stop="openDeviceModal(null, item.data.id)">+ Equipo</button>
                                <button class="grp-del-btn" title="Eliminar grupo"
                                        @click.stop="deleteGroup(item.data)">✕</button>
                            </template>
                        </template>
                    </div>

                    <!-- Device block (explicit or virtual) -->
                    <div
                        v-else-if="item.type === 'device'"
                        class="dev-block"
                        :style="{ marginRight: '10px' }">

                        <div class="dev-hdr" :class="devStCls(item.data)" @click="toggle(item.devKey)">
                            <span class="nd-tracks" aria-hidden="true">
                                <span v-for="(cont, j) in item.tracks" :key="j" class="nd-track-base" :class="cont ? 'nd-track-v' : 'nd-track-e'"></span>
                                <span class="nd-conn" :class="item.isLast ? 'nd-conn-last' : 'nd-conn-mid'"></span>
                            </span>
                            <span class="dev-chevron">{{ expanded[item.devKey] ? '▾' : '▸' }}</span>
                            <img v-if="item.data.icon && getDeviceIcon(item.data.icon)" :src="getDeviceIcon(item.data.icon)" class="dev-icon-img" />
                            <span v-else class="dev-icon">🖥</span>
                            <div class="dev-info">
                                <span class="dev-name">{{ item.data.name }}</span>
                                <span v-if="item.data.brand || item.data.model" class="dev-meta">{{ [item.data.brand, item.data.model].filter(Boolean).join(' · ') }}</span>
                            </div>
                            <span v-if="item.data.hostname" class="dev-ip">{{ item.data.hostname }}</span>
                            <span class="dev-status-badge" :class="devStCls(item.data)">{{ devStLbl(item.data) }}</span>
                            <span class="dev-count">{{ item.data.sensors.length }} sens</span>
                            <button class="dev-add-btn" title="Agregar sensor"
                                    @click.stop="openSensorModal(item.data, item.groupId)">+</button>
                            <template v-if="item.data.explicit">
                                <select class="dev-grp-sel"
                                        @change="onMoveDevice(item.data, item.groupId, $event)" @click.stop>
                                    <option value="">📦 Mover…</option>
                                    <optgroup label="Grupos">
                                        <option v-for="g in allLogicalGroupsFlat" :key="g.id" :value="g.id"
                                                :disabled="g.id === item.groupId">{{ g.indentedName }}</option>
                                    </optgroup>
                                    <option value="__none__" :disabled="item.groupId === null">Sin grupo</option>
                                </select>
                                <button class="dev-edit-btn" title="Editar equipo"
                                        @click.stop="openDeviceModal(item.data, item.groupId)">✎</button>
                                <button class="dev-del-btn" title="Eliminar equipo"
                                        @click.stop="deleteDevice(item.data)">✕</button>
                            </template>
                            <template v-else>
                                <button class="dev-upgrade-btn" title="Convertir en equipo explícito"
                                        @click.stop="openDeviceModal(item.data, item.groupId)">+ Definir equipo</button>
                            </template>
                        </div>

                        <div v-if="expanded[item.devKey]" class="dev-cards" :style="{ paddingLeft: ((item.tracks.length + 1) * 16 + 4) + 'px' }">
                            <template v-for="s in item.data.sensors" :key="s.id">
                                <div v-if="cardVisible(s)" class="s-card" :class="scCls(s)">
                                    <span class="sc-dot" :class="dotCls(s)"></span>
                                    <div class="sc-body" @click="$router.push('/dashboard/' + s.id)">
                                        <span class="sc-name">{{ s.label }}</span>
                                        <span class="sc-val">{{ lastVal(s.id, s.label) }}</span>
                                    </div>
                                    <div class="sc-actions">
                                        <button class="sc-act" :title="s.active ? 'Pausar' : 'Reanudar'"
                                                @click.stop="togglePauseSensor(s)">{{ s.active ? '⏸' : '▶' }}</button>
                                        <button class="sc-act" title="Editar"
                                                @click.stop="openSensorModal(null, null, s)">✎</button>
                                        <button class="sc-act sc-act-del" title="Eliminar"
                                                @click.stop="deleteSensor(s)">✕</button>
                                    </div>
                                </div>
                            </template>
                            <div v-if="item.data.sensors.every(s => !cardVisible(s))" class="no-match">
                                Sin sensores que coincidan
                            </div>
                        </div>

                    </div>

                </template>

            </div>
        </div>

        <!-- ── Device Modal ── -->
        <div v-if="devModal.show" class="nd-overlay" @click.self="devModal.show = false">
            <div class="nd-modal">
                <div class="nd-modal-hdr">
                    <span>{{ devModal.mode === 'add' ? 'Nuevo equipo' : 'Editar equipo' }}</span>
                    <button class="nd-modal-close" @click="devModal.show = false">✕</button>
                </div>
                <div class="nd-modal-body">
                    <div class="mf-row">
                        <label class="mf-label">Nombre del equipo</label>
                        <input v-model="devForm.name" class="mf-input" placeholder="Fortigate-Duran" />
                    </div>
                    <div class="mf-row-2">
                        <div>
                            <label class="mf-label">Marca / Fabricante</label>
                            <input v-model="devForm.brand" class="mf-input" placeholder="Fortinet"
                                   list="nagsa-brand-list" autocomplete="off" />
                            <datalist id="nagsa-brand-list">
                                <option v-for="b in knownBrands" :key="b" :value="b" />
                            </datalist>
                        </div>
                        <div>
                            <label class="mf-label">Modelo</label>
                            <input v-model="devForm.model" class="mf-input" placeholder="FortiGate 60F" />
                        </div>
                    </div>
                    <div class="mf-row">
                        <label class="mf-label">IP / Hostname</label>
                        <input v-model="devForm.hostname" class="mf-input" placeholder="10.1.1.1" />
                    </div>
                    <div class="mf-row">
                        <label class="mf-label">Grupo</label>
                        <select v-model="devForm.parent" class="mf-input">
                            <option :value="null">Sin grupo</option>
                            <option v-for="g in allLogicalGroupsFlat" :key="g.id" :value="g.id">{{ g.indentedName }}</option>
                        </select>
                    </div>
                    <div class="mf-row">
                        <label class="mf-label">Notas (opcional)</label>
                        <textarea v-model="devForm.notes" class="mf-input mf-textarea" rows="2" placeholder="Descripción, ubicación, etc."></textarea>
                    </div>
                    <div class="mf-row">
                        <label class="mf-label">Icono</label>
                        <!-- tabs -->
                        <div class="dip-tabs">
                            <button class="dip-tab" :class="{ 'dip-tab-sel': dipTab === 'builtin' }"  @click="dipTab = 'builtin'">Dispositivos</button>
                            <button class="dip-tab" :class="{ 'dip-tab-sel': dipTab === 'vendors' }"  @click="dipTab = 'vendors'">Fabricantes</button>
                            <button class="dip-tab" :class="{ 'dip-tab-sel': dipTab === 'uploads' }"  @click="dipTab = 'uploads'">Cargados</button>
                        </div>
                        <!-- default + device icons -->
                        <div v-if="dipTab === 'builtin'" class="dip-wrap">
                            <div class="dip-item" :class="{ 'dip-sel': devForm.icon === null }" @click="devForm.icon = null">
                                <span style="font-size:20px;line-height:1">🖥</span>
                                <span class="dip-lbl">Default</span>
                            </div>
                            <div v-for="ic in deviceIcons" :key="ic.file"
                                 class="dip-item" :class="{ 'dip-sel': devForm.icon === '/nagsa/icons/devices/' + ic.file }"
                                 @click="devForm.icon = '/nagsa/icons/devices/' + ic.file">
                                <img :src="'/nagsa/icons/devices/' + ic.file" class="dip-ico-img" :alt="ic.label" />
                                <span class="dip-lbl">{{ ic.label }}</span>
                            </div>
                        </div>
                        <!-- vendor logos -->
                        <div v-if="dipTab === 'vendors'" class="dip-wrap">
                            <div class="dip-item" :class="{ 'dip-sel': devForm.icon === null }" @click="devForm.icon = null">
                                <span style="font-size:20px;line-height:1">🖥</span>
                                <span class="dip-lbl">Default</span>
                            </div>
                            <div v-for="ic in vendorIcons" :key="ic.file"
                                 class="dip-item" :class="{ 'dip-sel': devForm.icon === '/nagsa/icons/vendors/' + ic.file }"
                                 @click="devForm.icon = '/nagsa/icons/vendors/' + ic.file">
                                <img :src="'/nagsa/icons/vendors/' + ic.file" class="dip-ico-img" :alt="ic.label" />
                                <span class="dip-lbl">{{ ic.label }}</span>
                            </div>
                        </div>
                        <!-- uploaded icons -->
                        <div v-if="dipTab === 'uploads'">
                            <div v-if="knownIcons.length" class="dip-wrap">
                                <div class="dip-item" :class="{ 'dip-sel': devForm.icon === null }" @click="devForm.icon = null">
                                    <span style="font-size:20px;line-height:1">🖥</span>
                                    <span class="dip-lbl">Default</span>
                                </div>
                                <div v-for="ic in knownIcons" :key="ic.id"
                                     class="dip-item" :class="{ 'dip-sel': devForm.icon === ic.id }"
                                     @click="devForm.icon = ic.id">
                                    <img :src="ic.data" class="dip-ico-img" :alt="ic.name" />
                                    <span class="dip-lbl">{{ ic.name }}</span>
                                </div>
                            </div>
                            <span v-else class="dip-empty">
                                Sin iconos propios —
                                <router-link to="/nagsa-settings" @click.native="devModal.show = false">cargar en Configuración ⚙</router-link>
                            </span>
                        </div>
                    </div>
                </div>
                <div class="nd-modal-footer">
                    <button class="btn-secondary" @click="devModal.show = false">Cancelar</button>
                    <button class="btn-primary" @click="saveDevice">{{ devModal.mode === 'add' ? 'Crear equipo' : 'Guardar' }}</button>
                </div>
            </div>
        </div>

        <!-- ── Sensor Modal ── -->
        <div v-if="sensorModal.show" class="nd-overlay" @click.self="sensorModal.show = false">
            <div class="nd-modal">
                <div class="nd-modal-hdr">
                    <span>{{ sensorModal.mode === 'add' ? 'Nuevo sensor' : 'Editar sensor' }}</span>
                    <button class="nd-modal-close" @click="sensorModal.show = false">✕</button>
                </div>
                <div class="nd-modal-body">
                    <div class="mf-row">
                        <label class="mf-label">Nombre</label>
                        <input v-model="sForm.name" class="mf-input" placeholder='Equipo - Sensor (ej. "Fortigate - CPU %")' />
                    </div>
                    <div class="mf-row">
                        <label class="mf-label">Tipo</label>
                        <select v-model="sForm.type" class="mf-input">
                            <option value="ping">Ping (ICMP)</option>
                            <option value="http">HTTP / HTTPS</option>
                            <option value="port">TCP Puerto</option>
                            <option value="dns">DNS</option>
                            <option value="snmp">SNMP</option>
                            <option value="keyword">HTTP Keyword</option>
                            <option value="push">Push</option>
                            <option value="docker">Docker</option>
                        </select>
                    </div>

                    <!-- Hostname -->
                    <div v-if="!['http','keyword','push'].includes(sForm.type)" class="mf-row">
                        <label class="mf-label">Hostname / IP</label>
                        <input v-model="sForm.hostname" class="mf-input" placeholder="10.1.1.1" />
                    </div>
                    <!-- URL -->
                    <div v-if="['http','keyword'].includes(sForm.type)" class="mf-row">
                        <label class="mf-label">URL</label>
                        <input v-model="sForm.url" class="mf-input" placeholder="https://..." />
                    </div>
                    <!-- Puerto TCP -->
                    <div v-if="sForm.type === 'port'" class="mf-row">
                        <label class="mf-label">Puerto</label>
                        <input v-model.number="sForm.port" type="number" class="mf-input mf-short" placeholder="80" />
                    </div>
                    <!-- Keyword -->
                    <div v-if="sForm.type === 'keyword'" class="mf-row">
                        <label class="mf-label">Keyword</label>
                        <input v-model="sForm.keyword" class="mf-input" placeholder="texto a buscar" />
                        <label class="mf-checkbox"><input v-model="sForm.invertKeyword" type="checkbox" /> Invertir</label>
                    </div>
                    <!-- DNS -->
                    <div v-if="sForm.type === 'dns'" class="mf-row-2">
                        <div>
                            <label class="mf-label">Servidor DNS</label>
                            <input v-model="sForm.dns_resolve_server" class="mf-input" placeholder="1.1.1.1" />
                        </div>
                        <div>
                            <label class="mf-label">Tipo registro</label>
                            <select v-model="sForm.dns_resolve_type" class="mf-input">
                                <option>A</option><option>AAAA</option><option>CNAME</option>
                                <option>MX</option><option>NS</option><option>TXT</option>
                            </select>
                        </div>
                    </div>
                    <!-- SNMP -->
                    <template v-if="sForm.type === 'snmp'">
                        <div class="mf-row-2">
                            <div>
                                <label class="mf-label">Community</label>
                                <input v-model="sForm.snmpCommunity" class="mf-input" placeholder="public" />
                            </div>
                            <div>
                                <label class="mf-label">Versión</label>
                                <select v-model="sForm.snmpVersion" class="mf-input">
                                    <option value="1">v1</option>
                                    <option value="2c">v2c</option>
                                    <option value="3">v3</option>
                                </select>
                            </div>
                        </div>
                        <div class="mf-row">
                            <label class="mf-label">OID</label>
                            <input v-model="sForm.snmpOid" class="mf-input" placeholder="1.3.6.1.2.1.1.3.0" />
                        </div>
                    </template>
                    <!-- HTTP TLS -->
                    <div v-if="['http','keyword'].includes(sForm.type)" class="mf-row">
                        <label class="mf-checkbox">
                            <input v-model="sForm.ignoreTls" type="checkbox" /> Ignorar error TLS/SSL
                        </label>
                    </div>

                    <div class="mf-divider"></div>

                    <!-- Equipo padre -->
                    <div class="mf-row">
                        <label class="mf-label">Equipo / Grupo</label>
                        <select v-model="sForm.parent" class="mf-input">
                            <option :value="null">Sin asignar</option>
                            <optgroup v-if="allDevicesForSelect.length" label="── Equipos ──">
                                <option v-for="d in allDevicesForSelect" :key="d.id" :value="d.id">{{ d.groupPrefix }}{{ d.name }}</option>
                            </optgroup>
                            <optgroup v-if="allLogicalGroupsFlat.length" label="── Grupos ──">
                                <option v-for="g in allLogicalGroupsFlat" :key="g.id" :value="g.id">{{ g.indentedName }}</option>
                            </optgroup>
                        </select>
                    </div>

                    <div class="mf-row-2">
                        <div>
                            <label class="mf-label">Intervalo (seg)</label>
                            <input v-model.number="sForm.interval" type="number" class="mf-input mf-short" min="20" />
                        </div>
                        <div>
                            <label class="mf-label">Máx. reintentos</label>
                            <input v-model.number="sForm.maxretries" type="number" class="mf-input mf-short" min="0" max="10" />
                        </div>
                    </div>
                </div>
                <div class="nd-modal-footer">
                    <button class="btn-secondary" @click="sensorModal.show = false">Cancelar</button>
                    <button class="btn-primary" @click="saveSensor">{{ sensorModal.mode === 'add' ? 'Crear sensor' : 'Guardar' }}</button>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import { DEVICE_ICONS, VENDOR_ICONS } from "../nagsa-icon-library.js";

const UP = 1, DOWN = 0, PENDING = 2, MAINTENANCE = 3;
const LS_KEY = "nagsa-expand-v1";
const DEVICE_FLAG = "_nd";

const SFORM_DEFAULTS = {
    id: null, name: "", type: "ping",
    hostname: "", url: "", port: null,
    keyword: "", invertKeyword: false,
    snmpCommunity: "public", snmpVersion: "2c", snmpOid: "",
    dns_resolve_server: "1.1.1.1", dns_resolve_type: "A",
    ignoreTls: false, interval: 60, maxretries: 1, parent: null,
};

export default {
    name: "NagsaDashboard",

    data() {
        return {
            q:              "",
            sf:             null,
            expanded:       {},
            expandedGrp:    {},
            _expandLoaded:  false,
            addingGroup:    false,
            newGroupName:   "",
            newGroupParent: null,
            renamingGroup:  null,
            renameValue:    "",
            devModal:   { show: false, mode: "add", virtualSensors: [] },
            devForm:    { id: null, name: "", brand: "", model: "", hostname: "", parent: null, notes: "", icon: null },
            knownBrands:  [],
            knownIcons:   [],
            deviceIcons:  DEVICE_ICONS,
            vendorIcons:  VENDOR_ICONS,
            dipTab:       "builtin",
            sensorModal: { show: false, mode: "add" },
            sForm:      { ...SFORM_DEFAULTS },
        };
    },

    computed: {
        hb() { return this.$root.lastHeartbeatList || {}; },

        allMonitors() {
            return Object.values(this.$root.monitorList || {}).filter(m => m.type !== "group");
        },

        allLogicalGroups() {
            return Object.values(this.$root.monitorList || {})
                .filter(m => m.type === "group" && !this.parseDeviceMeta(m.description));
        },

        allDeviceMonitors() {
            return Object.values(this.$root.monitorList || {})
                .filter(m => m.type === "group" && !!this.parseDeviceMeta(m.description));
        },

        /* Full recursive tree: logical groups → devices + virtual devices → sensors */
        groupedTree() {
            const lgMap = new Map();
            for (const g of this.allLogicalGroups) {
                lgMap.set(g.id, { raw: g, id: g.id, name: g.name, key: String(g.id), childLgIds: [], explicitDeviceIds: [], legacySensorHostMap: new Map() });
            }

            const dgMap = new Map();
            for (const d of this.allDeviceMonitors) {
                const meta = this.parseDeviceMeta(d.description);
                dgMap.set(d.id, { raw: d, id: d.id, name: d.name, key: "dev-" + d.id, hostname: d.hostname || "", brand: meta.brand || "", model: meta.model || "", icon: meta.icon || null, explicit: true, sensors: [] });
            }

            // Sensors → explicit device OR legacy host-grouping
            const ungroupedHostMap = new Map();
            for (const m of this.allMonitors) {
                const pid = m.parent ?? null;
                if (pid !== null && dgMap.has(pid)) {
                    dgMap.get(pid).sensors.push(this.sensorWithLabel(m));
                } else if (pid !== null && lgMap.has(pid)) {
                    const host = (m.hostname || "").trim() || m.name;
                    const bkt = lgMap.get(pid).legacySensorHostMap;
                    if (!bkt.has(host)) bkt.set(host, []);
                    bkt.get(host).push(m);
                } else {
                    const host = (m.hostname || "").trim() || m.name;
                    if (!ungroupedHostMap.has(host)) ungroupedHostMap.set(host, []);
                    ungroupedHostMap.get(host).push(m);
                }
            }

            for (const [, d] of dgMap) d.sensors.sort((a, b) => a.label.localeCompare(b.label));

            // Logical group parent-child
            const topLgIds = [];
            for (const g of this.allLogicalGroups) {
                const pid = g.parent ?? null;
                if (pid !== null && lgMap.has(pid)) lgMap.get(pid).childLgIds.push(g.id);
                else topLgIds.push(g.id);
            }

            // Explicit devices → their logical group parent (or top-level)
            const topDgIds = [];
            for (const d of this.allDeviceMonitors) {
                const pid = d.parent ?? null;
                if (pid !== null && lgMap.has(pid)) lgMap.get(pid).explicitDeviceIds.push(d.id);
                else topDgIds.push(d.id);
            }

            const buildLgNode = (id) => {
                const b = lgMap.get(id);
                const children = b.childLgIds.map(cid => buildLgNode(cid)).sort((a, b) => a.name.localeCompare(b.name));
                const explicitDevices = b.explicitDeviceIds.map(did => dgMap.get(did));
                const virtualDevices  = this.buildVirtualDevices(b.legacySensorHostMap);
                const devices = [...explicitDevices, ...virtualDevices].sort((a, bv) => {
                    const sa = this.devStOrd(a), sb = this.devStOrd(bv);
                    return sa !== sb ? sa - sb : a.name.localeCompare(bv.name);
                });
                const totalSensors = devices.reduce((s, d) => s + d.sensors.length, 0) + children.reduce((s, c) => s + c.totalSensors, 0);
                return { id: b.id, name: b.name, key: b.key, raw: b.raw, children, devices, totalSensors };
            };

            const tree = topLgIds.map(id => buildLgNode(id)).sort((a, b) => a.name.localeCompare(b.name));

            // Top-level devices (not in any logical group)
            const topDevices = [
                ...topDgIds.map(did => dgMap.get(did)),
                ...this.buildVirtualDevices(ungroupedHostMap),
            ].sort((a, b) => {
                const sa = this.devStOrd(a), sb = this.devStOrd(b);
                return sa !== sb ? sa - sb : a.name.localeCompare(b.name);
            });

            if (topDevices.length > 0) {
                tree.push({ id: null, name: "Sin grupo", key: "__none__", raw: null, children: [], devices: topDevices, totalSensors: topDevices.reduce((s, d) => s + d.sensors.length, 0) });
            }

            return tree;
        },

        renderItems() {
            const items = [];
            const lq = this.q.toLowerCase();
            const forceExpand = lq.length > 0;

            const devMatches = (d) =>
                d.name.toLowerCase().includes(lq) ||
                (d.hostname || "").toLowerCase().includes(lq) ||
                d.sensors.some(s => s.label.toLowerCase().includes(lq));

            const walk = (groups, depth) => {
                for (const g of groups) {
                    if (lq && !this.groupHasMatch(g, lq)) continue;
                    items.push({ type: "group", data: g, depth, key: "g-" + g.key });
                    const open = forceExpand || this.expandedGrp[g.key];
                    if (!open) continue;
                    walk(g.children, depth + 1);
                    const devs = lq ? g.devices.filter(devMatches) : g.devices;
                    for (const dev of devs) {
                        const devKey = g.key + "|" + (dev.id ?? dev.key ?? dev.hostname);
                        items.push({ type: "device", data: dev, depth: depth + 1, groupId: g.id, devKey, key: "d-" + devKey });
                    }
                }
            };

            walk(this.groupedTree, 0);

            // Compute isLast + ancestor continuation tracks for each item
            const isLastArr = items.map((_, i) => {
                const d = items[i].depth;
                for (let j = i + 1; j < items.length; j++) {
                    if (items[j].depth === d) return false;
                    if (items[j].depth < d) return true;
                }
                return true;
            });
            const ancestorIsLast = [];
            for (let i = 0; i < items.length; i++) {
                const d = items[i].depth;
                ancestorIsLast[d] = isLastArr[i];
                items[i].isLast = isLastArr[i];
                items[i].tracks = Array.from({ length: d }, (_, j) => !ancestorIsLast[j]);
            }

            return items;
        },

        allLogicalGroupsFlat() {
            const result = [];
            const walk = (groups, depth) => {
                for (const g of groups) {
                    if (g.id === null) continue;
                    result.push({ ...g, indentedName: "—".repeat(depth) + (depth > 0 ? " " : "") + g.name });
                    walk(g.children, depth + 1);
                }
            };
            walk(this.groupedTree.filter(g => g.id !== null), 0);
            return result;
        },

        allDevicesForSelect() {
            const result = [];
            const walk = (groups, prefix) => {
                for (const g of groups) {
                    if (g.id === null) continue;
                    const grpPrefix = prefix + g.name + " / ";
                    for (const d of g.devices) {
                        if (d.explicit) result.push({ id: d.id, name: d.name, groupPrefix: grpPrefix });
                    }
                    walk(g.children, grpPrefix);
                }
                for (const g of groups) {
                    if (g.id === null) {
                        for (const d of g.devices) {
                            if (d.explicit) result.push({ id: d.id, name: d.name, groupPrefix: "" });
                        }
                    }
                }
            };
            walk(this.groupedTree, "");
            return result;
        },

        cUp()      { return this.allMonitors.filter(m => m.active && this.st(m.id) === UP).length; },
        cDown()    { return this.allMonitors.filter(m => m.active && this.st(m.id) === DOWN).length; },
        cPending() { return this.allMonitors.filter(m => m.active && this.st(m.id) === PENDING).length; },
        cPaused()  { return this.allMonitors.filter(m => !m.active).length; },
    },

    watch: {
        "allMonitors.length"(n) {
            if (n > 0 && !this._expandLoaded) { this._expandLoaded = true; this.loadExpandState(); }
        },
    },

    mounted() {
        if (this.allMonitors.length > 0) { this._expandLoaded = true; this.loadExpandState(); }
        this.$root.getSocket().emit("nagsa:settings:get", (res) => {
            if (res.ok) { this.knownBrands = res.brands || []; this.knownIcons = res.icons || []; }
        });
    },

    methods: {
        st(id) { return this.hb[id]?.status ?? -1; },

        // ── Value formatting ─────────────────────────────────
        formatSensorValue(label, raw) {
            const lbl = (label || "").toLowerCase();
            const num = parseFloat(raw);
            if (isNaN(num)) return raw;

            if (/traffic|bytes|octets/i.test(lbl)) {
                if (num === 0) return "0 B";
                const units = ["B", "KB", "MB", "GB", "TB"];
                let v = num, i = 0;
                while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
                return v.toFixed(i === 0 ? 0 : 2) + " " + units[i];
            }
            if (/uptime|ticks/i.test(lbl)) {
                const sec = Math.floor(num / (/ticks/i.test(lbl) ? 100 : 1));
                const d = Math.floor(sec / 86400), h = Math.floor((sec % 86400) / 3600), m = Math.floor((sec % 3600) / 60);
                if (d > 0) return `${d}d ${h}h ${m}m`;
                if (h > 0) return `${h}h ${m}m`;
                return `${m}m ${sec % 60}s`;
            }
            return raw;
        },

        lastVal(id, label) {
            const hb = this.hb[id];
            if (!hb) return "—";
            if (hb.status === DOWN) return "↓ Down";
            const m = (hb.msg || "").match(/SNMP OK:\s*(.+)/);
            if (m) return this.formatSensorValue(label, m[1].trim());
            if (hb.ping != null) return hb.ping + " ms";
            return hb.msg || "—";
        },

        // ── Expand / collapse ─────────────────────────────────
        toggle(key) { this.expanded[key] = !this.expanded[key]; this.saveExpandState(); },
        toggleGrp(key) { this.expandedGrp[key] = !this.expandedGrp[key]; this.saveExpandState(); },
        toggleSf(f) { this.sf = this.sf === f ? null : f; },

        expandAll() {
            const walk = (groups) => {
                for (const g of groups) {
                    this.expandedGrp[g.key] = true;
                    g.devices.forEach(d => { this.expanded[g.key + "|" + (d.id ?? d.key ?? d.hostname)] = true; });
                    walk(g.children);
                }
            };
            walk(this.groupedTree);
            this.saveExpandState();
        },
        collapseAll() {
            Object.keys(this.expanded).forEach(k => { this.expanded[k] = false; });
            Object.keys(this.expandedGrp).forEach(k => { this.expandedGrp[k] = false; });
            this.saveExpandState();
        },
        expandAllGrp() {
            const walk = (groups) => { for (const g of groups) { this.expandedGrp[g.key] = true; walk(g.children); } };
            walk(this.groupedTree);
        },

        saveExpandState() {
            try { localStorage.setItem(LS_KEY, JSON.stringify({ grp: this.expandedGrp, dev: this.expanded })); } catch {}
        },
        loadExpandState() {
            try {
                const raw = localStorage.getItem(LS_KEY);
                if (raw) {
                    const s = JSON.parse(raw);
                    if (s.grp) Object.keys(s.grp).forEach(k => { this.expandedGrp[k] = s.grp[k]; });
                    if (s.dev) Object.keys(s.dev).forEach(k => { this.expanded[k] = s.dev[k]; });
                } else { this.expandAllGrp(); this.saveExpandState(); }
            } catch { this.expandAllGrp(); }
        },

        // ── Tree helpers ──────────────────────────────────────
        parseDeviceMeta(description) {
            try { const d = JSON.parse(description || "{}"); return d[DEVICE_FLAG] === 1 ? d : null; } catch { return null; }
        },
        sensorWithLabel(m) {
            const i = m.name.indexOf(" - ");
            return { ...m, label: i > -1 ? m.name.substring(i + 3).trim() : m.name };
        },
        buildVirtualDevices(hostMap) {
            return [...hostMap.entries()].map(([host, monitors]) => {
                const prefixes = monitors.map(m => { const i = m.name.indexOf(" - "); return i > -1 ? m.name.substring(0, i).trim() : null; }).filter(Boolean);
                const unique = [...new Set(prefixes)];
                const name = unique.length === 1 ? unique[0] : host;
                const sensors = monitors.map(m => this.sensorWithLabel(m)).sort((a, b) => a.label.localeCompare(b.label));
                return { id: null, key: "virt-" + host, name, hostname: host, brand: "", model: "", explicit: false, sensors };
            });
        },
        groupHasMatch(g, lq) {
            if (g.name.toLowerCase().includes(lq)) return true;
            if (g.devices.some(d => d.name.toLowerCase().includes(lq) || (d.hostname || "").toLowerCase().includes(lq) || d.sensors.some(s => s.label.toLowerCase().includes(lq)))) return true;
            return g.children.some(c => this.groupHasMatch(c, lq));
        },
        countDevicesInGroup(g) {
            return g.devices.length + g.children.reduce((s, c) => s + this.countDevicesInGroup(c), 0);
        },
        groupMoveOptions(grp) {
            const excluded = new Set();
            const mark = (g) => { excluded.add(g.id); g.children.forEach(c => mark(c)); };
            mark(grp);
            const result = [];
            const walk = (groups, depth) => {
                for (const g of groups) {
                    if (g.id === null || excluded.has(g.id)) { walk(g.children, depth + 1); continue; }
                    result.push({ ...g, indentedName: "—".repeat(depth) + (depth > 0 ? " " : "") + g.name });
                    walk(g.children, depth + 1);
                }
            };
            walk(this.groupedTree, 0);
            return result;
        },

        // ── Logical group CRUD ────────────────────────────────
        startAddGroup() { this.addingGroup = true; this.newGroupName = ""; this.newGroupParent = null; this.$nextTick(() => this.$refs.newGroupInput?.focus()); },
        cancelAddGroup() { this.addingGroup = false; },
        confirmAddGroup() {
            const name = this.newGroupName.trim();
            if (!name) return;
            this.$root.getSocket().emit("add", { type: "group", name, interval: 60, accepted_statuscodes: [], parent: this.newGroupParent }, (res) => {
                if (res.ok) { this.addingGroup = false; this.newGroupName = ""; this.$nextTick(() => { this.expandedGrp[String(res.monitorID)] = true; this.saveExpandState(); }); }
                else alert("Error al crear grupo: " + res.msg);
            });
        },
        startRename(grp) { this.renamingGroup = grp.id; this.renameValue = grp.name; this.$nextTick(() => { const el = Array.isArray(this.$refs.renameInput) ? this.$refs.renameInput[0] : this.$refs.renameInput; el?.focus(); el?.select(); }); },
        cancelRename() { this.renamingGroup = null; },
        confirmRename(grp) {
            const name = this.renameValue.trim();
            if (!name || name === grp.name) { this.cancelRename(); return; }
            this.$root.getSocket().emit("editMonitor", { ...grp.raw, name, accepted_statuscodes: [] }, (res) => { if (res.ok) this.cancelRename(); else alert("Error: " + res.msg); });
        },
        deleteGroup(grp) {
            if (!confirm(`¿Eliminar grupo "${grp.name}"?\nLos equipos y sensores quedarán sin grupo.`)) return;
            this.$root.getSocket().emit("deleteMonitor", grp.id, false, (res) => { if (!res.ok) alert("Error: " + res.msg); });
        },
        onMoveGroup(grp, event) {
            const val = event.target.value; event.target.value = "";
            if (!val) return;
            const newParent = val === "__none__" ? null : parseInt(val);
            this.$root.getSocket().emit("editMonitor", { ...grp.raw, parent: newParent, accepted_statuscodes: [] }, (res) => { if (!res.ok) alert("Error: " + res.msg); });
        },

        // ── Device CRUD ───────────────────────────────────────
        openDeviceModal(dev, groupId) {
            if (dev && dev.explicit) {
                // Edit existing explicit device
                const meta = this.parseDeviceMeta(dev.raw.description) || {};
                this.devForm = { id: dev.id, name: dev.name, brand: dev.brand, model: dev.model, hostname: dev.hostname, parent: dev.raw.parent ?? null, notes: meta.notes || "", icon: meta.icon || null };
                this.devModal = { show: true, mode: "edit" };
            } else if (dev && !dev.explicit) {
                // Convert virtual device to explicit — capture sensor IDs to adopt
                this.devForm = { id: null, name: dev.name, brand: "", model: "", hostname: dev.hostname, parent: groupId ?? null, notes: "", icon: null };
                this.devModal = { show: true, mode: "add", virtualSensors: dev.sensors.map(s => s.id) };
            } else {
                this.devForm = { id: null, name: "", brand: "", model: "", hostname: "", parent: groupId ?? null, notes: "", icon: null };
                this.devModal = { show: true, mode: "add", virtualSensors: [] };
            }
        },
        saveDevice() {
            const f = this.devForm;
            if (!f.name.trim()) { alert("El nombre es obligatorio"); return; }
            const description = JSON.stringify({ [DEVICE_FLAG]: 1, brand: f.brand, model: f.model, notes: f.notes, icon: f.icon || null });
            if (f.brand && !this.knownBrands.includes(f.brand)) {
                this.knownBrands.push(f.brand);
                this.knownBrands.sort((a, b) => a.localeCompare(b));
                this.$root.getSocket().emit("nagsa:settings:save", { brands: this.knownBrands }, () => {});
            }
            const payload = { type: "group", name: f.name.trim(), hostname: f.hostname || null, description, interval: 60, retryInterval: 60, accepted_statuscodes: [], parent: f.parent };
            if (this.devModal.mode === "edit") {
                const existing = this.$root.monitorList[f.id];
                this.$root.getSocket().emit("editMonitor", { ...existing, ...payload, id: f.id }, (res) => { if (res.ok) this.devModal.show = false; else alert("Error: " + res.msg); });
            } else {
                this.$root.getSocket().emit("add", payload, (res) => {
                    if (res.ok) {
                        const newId = res.monitorID;
                        const toAdopt = this.devModal.virtualSensors || [];
                        if (toAdopt.length) {
                            const socket = this.$root.getSocket();
                            toAdopt.forEach(sensorId => {
                                const m = this.$root.monitorList[sensorId];
                                if (m) socket.emit("editMonitor", { ...m, parent: newId, accepted_statuscodes: m.accepted_statuscodes || [] }, () => {});
                            });
                        }
                        this.devModal.show = false;
                        this.$nextTick(() => { this.expanded["dev-" + newId] = true; this.saveExpandState(); });
                    } else {
                        alert("Error: " + res.msg);
                    }
                });
            }
        },
        deleteDevice(dev) {
            if (!confirm(`¿Eliminar equipo "${dev.name}"?\nLos sensores del equipo quedarán sin asignar.`)) return;
            this.$root.getSocket().emit("deleteMonitor", dev.id, false, (res) => { if (!res.ok) alert("Error: " + res.msg); });
        },
        onMoveDevice(dev, currentGrpId, event) {
            const val = event.target.value; event.target.value = "";
            if (!val || val === String(currentGrpId)) return;
            const newParent = val === "__none__" ? null : parseInt(val);
            if (dev.explicit) {
                const existing = this.$root.monitorList[dev.id];
                this.$root.getSocket().emit("editMonitor", { ...existing, parent: newParent, accepted_statuscodes: [] }, () => {});
            } else {
                dev.sensors.forEach(s => {
                    this.$root.getSocket().emit("editMonitor", { ...this.$root.monitorList[s.id], parent: newParent, accepted_statuscodes: [] }, () => {});
                });
            }
        },

        // ── Sensor CRUD ───────────────────────────────────────
        openSensorModal(dev, groupId, existingSensor) {
            if (existingSensor) {
                const m = this.$root.monitorList[existingSensor.id] || existingSensor;
                this.sForm = { id: m.id, name: m.name, type: m.type || "ping", hostname: m.hostname || "", url: m.url || "", port: m.port || null, keyword: m.keyword || "", invertKeyword: m.invertKeyword || false, snmpCommunity: m.snmpCommunity || "public", snmpVersion: m.snmpVersion || "2c", snmpOid: m.snmpOid || "", dns_resolve_server: m.dns_resolve_server || "1.1.1.1", dns_resolve_type: m.dns_resolve_type || "A", ignoreTls: m.ignoreTls || false, interval: m.interval || 60, maxretries: m.maxretries ?? 1, parent: m.parent ?? null };
                this.sensorModal = { show: true, mode: "edit" };
            } else {
                const parentId = dev && dev.explicit ? dev.id : (groupId ?? null);
                this.sForm = { ...SFORM_DEFAULTS, hostname: dev ? dev.hostname : "", name: dev ? dev.name + " - " : "", parent: parentId };
                this.sensorModal = { show: true, mode: "add" };
            }
        },
        saveSensor() {
            const f = this.sForm;
            if (!f.name.trim()) { alert("El nombre es obligatorio"); return; }
            const isHttp = ["http", "keyword"].includes(f.type);
            const isPort = f.type === "port";
            const isSnmp = f.type === "snmp";
            const existing = f.id ? { ...(this.$root.monitorList[f.id] || {}) } : {};
            const payload = {
                maxredirects: 10, notificationIDList: {}, retryInterval: f.interval, resendInterval: 0,
                upsideDown: false, packetSize: 56, expiryNotification: false,
                mqtt_username: "", mqtt_password: "", mqtt_topic: "", mqtt_successMessage: "",
                kafkaProducerBrokers: [], kafkaProducerSaslOptions: { mechanism: "none" },
                ...existing,
                name: f.name.trim(), type: f.type, interval: f.interval, maxretries: f.maxretries,
                parent: f.parent, active: existing.active ?? true,
                accepted_statuscodes: existing.accepted_statuscodes || (isHttp ? ["200-299"] : []),
                hostname: !isHttp ? (f.hostname || null) : null,
                url: isHttp ? (f.url || null) : null,
                port: isPort ? (f.port || null) : (isSnmp ? 161 : null),
                ignoreTls: isHttp ? f.ignoreTls : false,
                keyword: f.type === "keyword" ? (f.keyword || null) : null,
                invertKeyword: f.invertKeyword || false,
                snmpCommunity: f.snmpCommunity || "public",
                snmpVersion: f.snmpVersion || "2c",
                snmpOid: isSnmp ? (f.snmpOid || "") : "",
                dns_resolve_server: f.dns_resolve_server || "1.1.1.1",
                dns_resolve_type: f.dns_resolve_type || "A",
                dns_last_result: existing.dns_last_result || "",
                ...(f.id ? { id: f.id } : {}),
            };
            const event = this.sensorModal.mode === "add" ? "add" : "editMonitor";
            this.$root.getSocket().emit(event, payload, (res) => {
                if (res.ok) this.sensorModal.show = false;
                else alert("Error: " + res.msg);
            });
        },
        deleteSensor(sensor) {
            if (!confirm(`¿Eliminar sensor "${sensor.label}"?`)) return;
            this.$root.getSocket().emit("deleteMonitor", sensor.id, false, (res) => { if (!res.ok) alert("Error: " + res.msg); });
        },
        getDeviceIcon(iconId) {
            if (!iconId) return null;
            if (iconId.startsWith("/")) return iconId;          // built-in static path
            const ic = this.knownIcons.find(i => i.id === iconId);
            return ic ? ic.data : null;                         // uploaded base64
        },
        togglePauseSensor(sensor) {
            const m = { ...this.$root.monitorList[sensor.id], active: !sensor.active };
            this.$root.getSocket().emit("editMonitor", m, (res) => { if (!res.ok) alert("Error: " + res.msg); });
        },

        // ── Status helpers ────────────────────────────────────
        devStOrd(dev) { return { "sb-dn": 0, "sb-wn": 1, "sb-uk": 2, "sb-up": 3, "sb-ps": 4 }[this.devStCls(dev)] ?? 5; },
        devStCls(dev) {
            const s = dev.sensors;
            if (!s.length) return "sb-uk";
            if (s.some(x => x.active && this.st(x.id) === DOWN)) return "sb-dn";
            if (s.some(x => x.active && this.st(x.id) === PENDING)) return "sb-wn";
            if (s.every(x => !x.active)) return "sb-ps";
            if (s.some(x => x.active && this.st(x.id) === UP)) return "sb-up";
            return "sb-uk";
        },
        devStLbl(dev) { return { "sb-dn": "Down", "sb-wn": "Warn", "sb-ps": "Paused", "sb-up": "OK", "sb-uk": "?" }[this.devStCls(dev)] ?? "?"; },
        allDevicesInGroup(g) { const d = [...g.devices]; for (const c of g.children) d.push(...this.allDevicesInGroup(c)); return d; },
        grpStCls(grp) {
            const devs = this.allDevicesInGroup(grp);
            if (!devs.length) return "sb-uk";
            if (devs.some(d => this.devStCls(d) === "sb-dn")) return "sb-dn";
            if (devs.some(d => this.devStCls(d) === "sb-wn")) return "sb-wn";
            if (devs.every(d => this.devStCls(d) === "sb-ps")) return "sb-ps";
            if (devs.some(d => this.devStCls(d) === "sb-up")) return "sb-up";
            return "sb-uk";
        },
        grpStLbl(grp) { return { "sb-dn": "Down", "sb-wn": "Warn", "sb-ps": "Paused", "sb-up": "OK", "sb-uk": "?" }[this.grpStCls(grp)] ?? "?"; },
        dotCls(s) {
            if (!s.active) return "dot-ps";
            const x = this.st(s.id);
            if (x === DOWN) return "dot-dn"; if (x === PENDING) return "dot-wn";
            if (x === MAINTENANCE) return "dot-mt"; if (x === UP) return "dot-up";
            return "dot-uk";
        },
        scCls(s) {
            if (!s.active) return "sc-ps";
            const x = this.st(s.id);
            if (x === DOWN) return "sc-dn"; if (x === PENDING) return "sc-wn";
            if (x === MAINTENANCE) return "sc-mt"; if (x === UP) return "sc-ok";
            return "sc-uk";
        },
        cardVisible(s) {
            if (!this.sf) return true;
            const x = this.st(s.id);
            if (this.sf === "down")   return s.active && x === DOWN;
            if (this.sf === "warn")   return s.active && x === PENDING;
            if (this.sf === "up")     return s.active && x === UP;
            if (this.sf === "paused") return !s.active;
            return true;
        },
    },
};
</script>

<style>
.nd-wrap  { display:flex; flex-direction:column; height:calc(100vh - 80px); font-family:"Segoe UI",Arial,sans-serif; font-size:13px; background:#eef0f5; overflow:hidden; }
.nd-panel { display:flex; flex-direction:column; flex:1; overflow:hidden; }

/* ── Status bar ── */
.nd-bar { display:flex; align-items:center; gap:3px; padding:5px 12px; background:#1e2130; flex-shrink:0; }
.nd-stat { display:flex; flex-direction:column; align-items:center; border:2px solid transparent; border-radius:5px; padding:4px 18px; cursor:pointer; color:#fff; min-width:72px; user-select:none; transition:filter .15s, border-color .15s; }
.nd-stat:hover { filter:brightness(1.18); } .nd-stat.active { border-color:#fff; }
.nd-num { font-size:20px; font-weight:700; line-height:1.1; }
.nd-lbl { font-size:10px; text-transform:uppercase; letter-spacing:.05em; }
.nd-dn { background:#b03030; } .nd-wn { background:#c87020; }
.nd-up { background:#228845; } .nd-ps { background:#4a5a78; }
.nd-bar-right { margin-left:auto; } .nd-total { color:#778; font-size:11px; }

/* ── Toolbar ── */
.tree-bar { display:flex; gap:4px; align-items:center; padding:6px 12px; border-bottom:2px solid #d0d5e0; flex-shrink:0; background:#f0f3fb; }
.tree-filter { flex:1; padding:5px 10px; border:1px solid #c8cfe0; border-radius:4px; font-size:12px; }
.tree-filter:focus { outline:none; border-color:#5a8fd0; }
.tree-btn { background:#e8ecf5; border:1px solid #c8cfe0; border-radius:4px; padding:4px 10px; cursor:pointer; font-size:14px; color:#556; line-height:1; }
.tree-btn:hover { background:#d0d8f0; }
.tree-btn-grp    { background:#4a7ad8; color:#fff; border-color:#3a6ab8; font-size:11px; font-weight:600; }
.tree-btn-grp:hover { background:#3a6ab8; }
.tree-btn-dev    { background:#6a48c8; color:#fff; border-color:#5038a8; font-size:11px; font-weight:600; }
.tree-btn-dev:hover { background:#5038a8; }
.tree-btn-sensor { background:#228845; color:#fff; border-color:#1a6633; font-size:11px; font-weight:600; }
.tree-btn-sensor:hover { background:#1a6633; }

/* ── Scroll ── */
.tree-scroll { flex:1; overflow-y:auto; background:#eef0f5; padding-bottom:12px; }

/* ── Root ── */
.t-root { display:flex; align-items:center; gap:8px; padding:10px 16px; font-weight:700; font-size:13px; color:#1a1e2e; background:#dce6f8; border-bottom:2px solid #b8c8e8; user-select:none; }
.t-root-ico { color:#2e6fc4; font-size:16px; } .t-root-label { flex:1; }
.root-pill { font-size:10px; font-weight:700; border-radius:10px; padding:2px 8px; color:#fff; }
.root-dn { background:#b03030; } .root-up { background:#228845; }
.t-loading { padding:16px 20px; color:#aaa; font-size:12px; font-style:italic; }

/* ── New group row ── */
.new-grp-row { display:flex; align-items:center; gap:6px; padding:8px 16px; background:#e4ecfb; border-bottom:1px solid #c8d4ee; }
.grp-parent-sel { padding:4px 6px; border:1px solid #7a9ce0; border-radius:4px; font-size:12px; color:#334; background:#fff; max-width:200px; }
.grp-inline-input { flex:1; padding:4px 8px; border:1px solid #7a9ce0; border-radius:4px; font-size:13px; font-weight:700; color:#1a1e3a; background:#fff; outline:none; }
.grp-inline-input:focus { border-color:#4070c0; box-shadow:0 0 0 2px rgba(64,112,192,.2); }
.grp-act-btn { background:none; border:none; cursor:pointer; font-size:14px; padding:2px 7px; border-radius:3px; line-height:1; font-weight:700; }
.grp-act-btn.ok { color:#228845; } .grp-act-btn.ok:hover { background:#d0f0d8; }
.grp-act-btn.cancel { color:#b03030; } .grp-act-btn.cancel:hover { background:#fcd8d8; }

/* ── Logical group header ── */
.grp-hdr { display:flex; align-items:center; gap:8px; padding:9px 14px 9px 0; cursor:pointer; user-select:none; background:#d4ddf5; border-left:none; transition:background .1s; margin-top:6px; }
.grp-hdr:hover { background:#c8d4f0; }
.grp-hdr.depth-1 { font-size:12.5px; background:#dce4f2; }
.grp-hdr.depth-2 { font-size:12px; background:#e4eaf5; }
.grp-hdr.sb-up { background:#ddf0e5; }
.grp-hdr.sb-dn { background:#fce8e8; }
.grp-hdr.sb-wn { background:#fdf5e0; }
.grp-hdr.sb-ps { background:#e8ecf5; }
.grp-hdr.sb-uk { background:#e8ecf5; }
/* connector accent on group status */
.grp-hdr.sb-up .nd-conn::before, .grp-hdr.sb-up .nd-conn::after { background:#228845; }
.grp-hdr.sb-dn .nd-conn::before, .grp-hdr.sb-dn .nd-conn::after { background:#b03030; }
.grp-hdr.sb-wn .nd-conn::before, .grp-hdr.sb-wn .nd-conn::after { background:#c87020; }
.grp-hdr.sb-ps .nd-conn::before, .grp-hdr.sb-ps .nd-conn::after { background:#4a5a78; }
.grp-chevron { font-size:13px; color:#445; width:14px; flex-shrink:0; }
.grp-icon-sm { font-size:15px; flex-shrink:0; }
.grp-name  { font-weight:700; color:#1a1e3a; flex:1; cursor:default; }
.grp-badge { font-size:9.5px; font-weight:700; border-radius:4px; padding:2px 7px; color:#fff; flex-shrink:0; }
.grp-badge.sb-up { background:#228845; } .grp-badge.sb-dn { background:#b03030; }
.grp-badge.sb-wn { background:#c87020; } .grp-badge.sb-ps { background:#4a5a78; }
.grp-badge.sb-uk { background:#9a9fa8; }
.grp-count { font-size:11px; color:#557; flex-shrink:0; }
.grp-act-icon { background:#e4ecff; border:1px solid #a0b8e0; border-radius:3px; cursor:pointer; color:#3050a0; font-size:10px; font-weight:700; padding:2px 6px; line-height:1; opacity:.8; transition:opacity .15s; flex-shrink:0; }
.grp-act-icon:hover { opacity:1; background:#cddeff; }
.grp-del-btn { background:none; border:none; cursor:pointer; color:#c55; font-size:13px; padding:2px 5px; border-radius:3px; line-height:1; opacity:.5; transition:opacity .15s; }
.grp-del-btn:hover { opacity:1; background:#fcc; }

/* ── Device block ── */
.dev-block { margin-top:4px; border-radius:6px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.07); }
.dev-hdr { display:flex; align-items:center; gap:7px; padding:7px 10px 7px 0; cursor:pointer; user-select:none; background:#fff; border-left:none; transition:background .1s; }
.dev-hdr:hover { background:#f4f7ff; }
.dev-hdr.sb-dn { background:#fff8f8; }
.dev-hdr.sb-wn { background:#fffdf5; }
/* connector accent colors per status */
.dev-hdr.sb-up .nd-conn::before, .dev-hdr.sb-up .nd-conn::after,
.dev-hdr.sb-up .nd-track-v::before { background:#228845; }
.dev-hdr.sb-dn .nd-conn::before, .dev-hdr.sb-dn .nd-conn::after,
.dev-hdr.sb-dn .nd-track-v::before { background:#b03030; }
.dev-hdr.sb-wn .nd-conn::before, .dev-hdr.sb-wn .nd-conn::after,
.dev-hdr.sb-wn .nd-track-v::before { background:#c87020; }
.dev-hdr.sb-ps .nd-conn::before, .dev-hdr.sb-ps .nd-conn::after { background:#4a5a78; }
.dev-chevron { font-size:13px; color:#778; width:14px; flex-shrink:0; }
.dev-icon { font-size:14px; flex-shrink:0; }
.dev-info { flex:1; min-width:0; }
.dev-name { font-weight:700; font-size:12px; color:#1a1e2e; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block; }
.dev-meta { font-size:10px; color:#8899bb; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.dev-ip   { font-size:11px; color:#8899aa; font-family:monospace; flex-shrink:0; }
.dev-count { font-size:11px; color:#778; flex-shrink:0; }
.dev-status-badge { font-size:9px; font-weight:700; border-radius:4px; padding:2px 6px; color:#fff; flex-shrink:0; }
.dev-status-badge.sb-up { background:#228845; } .dev-status-badge.sb-dn { background:#b03030; }
.dev-status-badge.sb-wn { background:#c87020; } .dev-status-badge.sb-ps { background:#4a5a78; }
.dev-status-badge.sb-uk { background:#9a9fa8; }
.dev-add-btn  { background:#e4ecff; border:1px solid #a0b8e0; border-radius:3px; cursor:pointer; color:#3050a0; font-size:14px; font-weight:700; padding:1px 6px; line-height:1; opacity:.7; flex-shrink:0; transition:opacity .15s; }
.dev-add-btn:hover { opacity:1; background:#cddeff; }
.dev-edit-btn { background:none; border:1px solid #bbc; border-radius:3px; cursor:pointer; color:#556; font-size:12px; padding:1px 5px; line-height:1; opacity:.6; flex-shrink:0; transition:opacity .15s; }
.dev-edit-btn:hover { opacity:1; background:#e8ecf5; }
.dev-del-btn  { background:none; border:none; cursor:pointer; color:#c55; font-size:12px; padding:2px 5px; border-radius:3px; line-height:1; opacity:.5; flex-shrink:0; transition:opacity .15s; }
.dev-del-btn:hover { opacity:1; background:#fcc; }
.dev-upgrade-btn { background:#f0eefc; border:1px dashed #a090d0; border-radius:3px; cursor:pointer; color:#6048a0; font-size:10px; padding:2px 6px; line-height:1; flex-shrink:0; }
.dev-upgrade-btn:hover { background:#e0dcf8; }
.dev-grp-sel { font-size:10px; padding:2px 3px; border:1px solid #c8cfe0; border-radius:3px; background:#f0f3fb; color:#446; cursor:pointer; max-width:80px; flex-shrink:0; }

/* ── Sensor cards ── */
.dev-cards { display:flex; flex-wrap:wrap; gap:5px; padding:8px 10px 10px 14px; background:#f5f7fc; border-top:1px solid #e4e8f4; }
.no-match { font-size:11px; color:#aaa; font-style:italic; padding:4px 2px; }
.s-card { display:flex; align-items:flex-start; gap:6px; background:#fff; border-radius:5px; padding:6px 7px 6px 9px; width:155px; border-left:3px solid #ccc; box-shadow:0 1px 2px rgba(0,0,0,.06); transition:box-shadow .12s; flex-shrink:0; }
.s-card:hover { box-shadow:0 3px 8px rgba(0,0,0,.14); }
.sc-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; margin-top:3px; }
.dot-up { background:#228845; } .dot-dn { background:#b03030; }
.dot-wn { background:#c87020; } .dot-ps { background:#4a5a78; }
.dot-mt { background:#2874a6; } .dot-uk { background:#9a9fa8; }
.sc-body { flex:1; min-width:0; cursor:pointer; }
.sc-name { display:block; font-size:11px; font-weight:600; color:#1a2050; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sc-val  { display:block; font-size:10px; color:#667; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:2px; font-variant-numeric:tabular-nums; }
.sc-actions { display:flex; flex-direction:column; gap:2px; opacity:0; transition:opacity .15s; flex-shrink:0; }
.s-card:hover .sc-actions { opacity:1; }
.sc-act { background:none; border:none; cursor:pointer; font-size:11px; padding:1px 3px; border-radius:2px; color:#556; line-height:1.3; }
.sc-act:hover { background:#e8ecf5; }
.sc-act-del:hover { background:#fcd8d8; color:#b03030; }
.sc-ok { border-left-color:#228845; } .sc-dn { border-left-color:#b03030; background:#fff5f5; }
.sc-dn .sc-name { color:#8a1010; } .sc-wn { border-left-color:#c87020; background:#fffbf0; }
.sc-ps { border-left-color:#4a5a78; background:#f5f5fa; }
.sc-ps .sc-name, .sc-ps .sc-val { color:#aaa; }
.sc-mt { border-left-color:#2874a6; } .sc-uk { border-left-color:#9a9fa8; }

/* ── Modal ── */
.nd-overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index:9999; }
.nd-modal   { background:#fff; border-radius:10px; width:480px; max-width:96vw; max-height:90vh; display:flex; flex-direction:column; box-shadow:0 8px 32px rgba(0,0,0,.25); }
.nd-modal-hdr { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; background:#1e2130; border-radius:10px 10px 0 0; color:#fff; font-weight:700; font-size:14px; }
.nd-modal-close { background:none; border:none; color:#aab; cursor:pointer; font-size:18px; line-height:1; }
.nd-modal-close:hover { color:#fff; }
.nd-modal-body { flex:1; overflow-y:auto; padding:18px; display:flex; flex-direction:column; gap:12px; }
.nd-modal-footer { display:flex; justify-content:flex-end; gap:8px; padding:12px 18px; border-top:1px solid #e4e8f0; }
.mf-row   { display:flex; flex-direction:column; gap:4px; }
.mf-row-2 { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.mf-label { font-size:11px; font-weight:600; color:#556; text-transform:uppercase; letter-spacing:.04em; }
.mf-input { padding:6px 10px; border:1px solid #c8cfe0; border-radius:5px; font-size:13px; color:#1a1e2e; background:#fff; outline:none; }
.mf-input:focus { border-color:#5a8fd0; box-shadow:0 0 0 2px rgba(90,143,208,.18); }
.mf-short { max-width:120px; }
.mf-textarea { resize:vertical; }
.mf-checkbox { display:flex; align-items:center; gap:6px; font-size:12px; color:#445; cursor:pointer; }
.mf-divider { border:none; border-top:1px solid #e8ecf4; margin:2px 0; }
.btn-primary   { background:#4a7ad8; color:#fff; border:none; border-radius:5px; padding:7px 18px; font-size:13px; font-weight:600; cursor:pointer; }
.btn-primary:hover { background:#3a6ab8; }
.btn-secondary { background:#e8ecf5; color:#334; border:1px solid #c8cfe0; border-radius:5px; padding:7px 14px; font-size:13px; cursor:pointer; }
.btn-secondary:hover { background:#d0d8f0; }

/* ── Settings button ── */
.tree-btn-cfg { background:#2e3a58; color:#a0b0d8; border-color:#2e3a58; font-size:14px; padding:4px 9px; text-decoration:none; display:inline-flex; align-items:center; }
.tree-btn-cfg:hover { background:#4a5a78; color:#fff; }
/* ── Device icon image ── */
.dev-icon-img { width:18px; height:18px; object-fit:contain; flex-shrink:0; }
/* ── Icon picker in device modal ── */
.dip-tabs    { display:flex; gap:2px; margin-bottom:8px; }
.dip-tab     { background:#e8ecf5; border:1px solid #c8cfe0; border-radius:4px 4px 0 0; padding:4px 10px; font-size:11px; font-weight:600; cursor:pointer; color:#445; }
.dip-tab:hover   { background:#d0d8f0; }
.dip-tab-sel { background:#fff; border-bottom-color:#fff; color:#1a4ac8; }
.dip-wrap    { display:flex; flex-wrap:wrap; gap:6px; max-height:180px; overflow-y:auto; border:1px solid #e0e4f0; border-radius:0 4px 4px 4px; padding:8px; }
.dip-item    { display:flex; flex-direction:column; align-items:center; gap:3px; padding:6px 8px; border:2px solid #e0e4f0; border-radius:6px; cursor:pointer; min-width:54px; max-width:72px; transition:border-color .12s,background .12s; }
.dip-item:hover { border-color:#6a8ad8; background:#f0f4ff; }
.dip-sel     { border-color:#4a7ad8 !important; background:#eaf0ff !important; }
.dip-lbl     { font-size:9px; color:#556; text-align:center; max-width:60px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.dip-ico-img { width:24px; height:24px; object-fit:contain; }
.dip-empty   { font-size:11px; color:#889; font-style:italic; }
.dip-empty a { color:#4a7ad8; }
/* ── Tree connector lines ── */
.nd-tracks { display:inline-flex; align-items:center; align-self:stretch; flex-shrink:0; }
.nd-track-base { display:block; width:16px; position:relative; align-self:stretch; flex-shrink:0; }
.nd-track-v::before { content:''; position:absolute; left:7px; top:0; bottom:0; width:1px; background:#b0bcd4; }
.nd-track-e { /* empty column */ }
.nd-conn { display:block; width:16px; position:relative; align-self:stretch; flex-shrink:0; }
.nd-conn::before { content:''; position:absolute; left:7px; top:0; bottom:50%; width:1px; background:#b0bcd4; }
.nd-conn::after  { content:''; position:absolute; left:7px; top:calc(50% - 1px); right:-2px; height:1px; background:#b0bcd4; }
.nd-conn-mid::before { bottom:0; }
</style>
