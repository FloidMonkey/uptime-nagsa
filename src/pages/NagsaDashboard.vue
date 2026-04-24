<template>
    <div class="nagsa-prtg">
        <!-- ── Status bar ─────────────────────────────────────────── -->
        <div class="prtg-bar">
            <button class="prtg-stat" :class="['prtg-down', { active: statusFilter === 'down' }]" @click="toggleFilter('down')">
                <span class="prtg-stat-num">{{ countDown }}</span>
                <span class="prtg-stat-lbl">Down</span>
            </button>
            <button class="prtg-stat" :class="['prtg-warn', { active: statusFilter === 'warn' }]" @click="toggleFilter('warn')">
                <span class="prtg-stat-num">{{ countPending }}</span>
                <span class="prtg-stat-lbl">Warning</span>
            </button>
            <button class="prtg-stat" :class="['prtg-up', { active: statusFilter === 'up' }]" @click="toggleFilter('up')">
                <span class="prtg-stat-num">{{ countUp }}</span>
                <span class="prtg-stat-lbl">Up</span>
            </button>
            <button class="prtg-stat" :class="['prtg-pause', { active: statusFilter === 'paused' }]" @click="toggleFilter('paused')">
                <span class="prtg-stat-num">{{ countPaused }}</span>
                <span class="prtg-stat-lbl">Paused</span>
            </button>
            <div class="prtg-bar-right">
                <input v-model="globalSearch" type="text" class="prtg-search" placeholder="Search monitors…" />
                <span class="prtg-total">{{ totalMonitors }} sensors</span>
                <router-link to="/add" class="prtg-add-btn">+ Add</router-link>
            </div>
        </div>

        <!-- ── Split layout ──────────────────────────────────────── -->
        <div class="prtg-split">

            <!-- Left: device/group tree -->
            <div class="prtg-tree">
                <div class="tree-search-wrap">
                    <input v-model="treeSearch" type="text" class="tree-search-input" placeholder="Filter…" />
                </div>

                <div class="tree-body">
                    <!-- All root -->
                    <div class="tree-item tree-root" :class="{ selected: selectedId === '__all__' }" @click="selectAll">
                        <span class="tree-icon">◉</span>
                        <span class="tree-name">All Monitors</span>
                        <span class="tree-badge">{{ totalMonitors }}</span>
                    </div>

                    <!-- Groups -->
                    <template v-for="group in filteredTree" :key="group.id">
                        <div
                            class="tree-item tree-group"
                            :class="{ selected: selectedId === group.id }"
                            @click="selectGroup(group)"
                        >
                            <span class="tree-toggle" @click.stop="toggleExpand(group.id)">
                                {{ expanded[group.id] ? '▾' : '▸' }}
                            </span>
                            <span class="status-dot" :class="groupDotClass(group.id)"></span>
                            <span class="tree-name">{{ group.name }}</span>
                            <span class="tree-badge">{{ childCount(group.id) }}</span>
                        </div>

                        <template v-if="expanded[group.id]">
                            <div
                                v-for="child in filteredChildren(group.id)"
                                :key="child.id"
                                class="tree-item tree-sensor"
                                :class="{ selected: selectedId === child.id }"
                                @click="selectMonitor(child)"
                            >
                                <span class="status-dot" :class="monitorDotClass(child.id)"></span>
                                <span class="tree-name">{{ child.name }}</span>
                            </div>
                        </template>
                    </template>
                </div>
            </div>

            <!-- Right: content -->
            <div class="prtg-content">

                <!-- Breadcrumb + actions -->
                <div class="prtg-breadcrumb">
                    <nav class="breadcrumb-nav">
                        <span class="bc-root" @click="selectAll">Home</span>
                        <template v-if="selectedGroup">
                            <span class="bc-sep">›</span>
                            <span class="bc-current">{{ selectedGroup.name }}</span>
                        </template>
                        <template v-else-if="statusFilter">
                            <span class="bc-sep">›</span>
                            <span class="bc-current text-capitalize">{{ statusFilter }}</span>
                        </template>
                        <template v-else-if="globalSearch">
                            <span class="bc-sep">›</span>
                            <span class="bc-current">Search: "{{ globalSearch }}"</span>
                        </template>
                    </nav>
                    <div class="bc-actions">
                        <span class="bc-count">{{ displayedMonitors.length }} results</span>
                        <router-link v-if="selectedGroup" :to="'/dashboard/' + selectedGroup.id" class="bc-link-btn">
                            Open Detail ›
                        </router-link>
                    </div>
                </div>

                <!-- Summary pills -->
                <div class="prtg-summary">
                    <span class="sum-pill pill-down">{{ displayDown }} Down</span>
                    <span class="sum-pill pill-warn">{{ displayPending }} Warning</span>
                    <span class="sum-pill pill-up">{{ displayUp }} Up</span>
                    <span class="sum-pill pill-pause">{{ displayPaused }} Paused</span>
                </div>

                <!-- Sensor table -->
                <div class="prtg-table-wrap">
                    <table class="prtg-table">
                        <thead>
                            <tr>
                                <th class="col-st"></th>
                                <th class="col-name" @click="sortBy('name')">
                                    Sensor / Monitor {{ sortIcon('name') }}
                                </th>
                                <th class="col-type">Type</th>
                                <th class="col-val" @click="sortBy('msg')">
                                    Last Value {{ sortIcon('msg') }}
                                </th>
                                <th class="col-time" @click="sortBy('time')">
                                    Last Check {{ sortIcon('time') }}
                                </th>
                                <th class="col-act"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="displayedMonitors.length === 0">
                                <td colspan="6" class="empty-row">No monitors match the current filter</td>
                            </tr>
                            <tr
                                v-for="m in displayedMonitors"
                                :key="m.id"
                                class="sensor-row"
                                :class="rowClass(m.id)"
                                @dblclick="$router.push('/dashboard/' + m.id)"
                            >
                                <td class="col-st">
                                    <span class="status-circle" :class="monitorDotClass(m.id)"></span>
                                </td>
                                <td class="col-name">
                                    <router-link :to="'/dashboard/' + m.id" class="sensor-link">{{ m.name }}</router-link>
                                    <div v-if="m.hostname" class="sensor-host">{{ m.hostname }}</div>
                                </td>
                                <td class="col-type">
                                    <span class="type-tag">{{ m.type }}</span>
                                </td>
                                <td class="col-val">{{ lastMsg(m.id) }}</td>
                                <td class="col-time">{{ lastTime(m.id) }}</td>
                                <td class="col-act">
                                    <router-link :to="'/dashboard/' + m.id" class="row-btn">›</router-link>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);

const STATUS_UP = 1;
const STATUS_DOWN = 0;
const STATUS_PENDING = 2;
const STATUS_MAINTENANCE = 3;

export default {
    name: "NagsaDashboard",

    data() {
        return {
            selectedId: "__all__",
            treeSearch: "",
            globalSearch: "",
            statusFilter: null,
            expanded: {},
            sortField: "name",
            sortAsc: true,
        };
    },

    computed: {
        allGroups() {
            return Object.values(this.$root.monitorList || {}).filter(m => m.type === "group");
        },
        allSensors() {
            return Object.values(this.$root.monitorList || {}).filter(m => m.type !== "group");
        },
        totalMonitors() {
            return this.allSensors.length;
        },

        // Root-level groups (no parent, or parent is not a group)
        rootGroups() {
            const groupIds = new Set(this.allGroups.map(g => g.id));
            return this.allGroups.filter(g => !g.parent || !groupIds.has(g.parent))
                .sort((a, b) => a.name.localeCompare(b.name));
        },

        filteredTree() {
            if (!this.treeSearch) return this.rootGroups;
            const q = this.treeSearch.toLowerCase();
            return this.rootGroups.filter(g =>
                g.name.toLowerCase().includes(q) ||
                this.childrenOf(g.id).some(c => c.name.toLowerCase().includes(q))
            );
        },

        selectedGroup() {
            if (!this.selectedId || this.selectedId === "__all__") return null;
            return this.$root.monitorList?.[this.selectedId] ?? null;
        },

        // Global status counts (all sensors)
        countUp() {
            return this.allSensors.filter(m => m.active && this.getStatus(m.id) === STATUS_UP).length;
        },
        countDown() {
            return this.allSensors.filter(m => m.active && this.getStatus(m.id) === STATUS_DOWN).length;
        },
        countPending() {
            return this.allSensors.filter(m => m.active && this.getStatus(m.id) === STATUS_PENDING).length;
        },
        countPaused() {
            return this.allSensors.filter(m => !m.active).length;
        },

        // Displayed monitors (right panel)
        displayedMonitors() {
            let list;

            if (this.globalSearch) {
                const q = this.globalSearch.toLowerCase();
                list = this.allSensors.filter(m =>
                    m.name.toLowerCase().includes(q) ||
                    (m.hostname || "").toLowerCase().includes(q) ||
                    m.type.toLowerCase().includes(q)
                );
            } else if (this.statusFilter) {
                list = this.allSensors.filter(m => {
                    const s = this.getStatus(m.id);
                    if (this.statusFilter === "down") return m.active && s === STATUS_DOWN;
                    if (this.statusFilter === "warn") return m.active && s === STATUS_PENDING;
                    if (this.statusFilter === "up") return m.active && s === STATUS_UP;
                    if (this.statusFilter === "paused") return !m.active;
                    return true;
                });
            } else if (this.selectedId && this.selectedId !== "__all__") {
                const sel = this.$root.monitorList?.[this.selectedId];
                if (sel && sel.type === "group") {
                    list = this.sensorsInGroup(this.selectedId);
                } else {
                    list = sel ? [sel] : [];
                }
            } else {
                list = this.allSensors;
            }

            return this.sortList(list);
        },

        // Summary counts for the current view
        displayDown() {
            return this.displayedMonitors.filter(m => m.active && this.getStatus(m.id) === STATUS_DOWN).length;
        },
        displayUp() {
            return this.displayedMonitors.filter(m => m.active && this.getStatus(m.id) === STATUS_UP).length;
        },
        displayPending() {
            return this.displayedMonitors.filter(m => m.active && this.getStatus(m.id) === STATUS_PENDING).length;
        },
        displayPaused() {
            return this.displayedMonitors.filter(m => !m.active).length;
        },
    },

    mounted() {
        // Auto-expand groups that have down monitors
        for (const group of this.rootGroups) {
            if (this.sensorsInGroup(group.id).some(m => m.active && this.getStatus(m.id) === STATUS_DOWN)) {
                this.expanded[group.id] = true;
            }
        }
    },

    methods: {
        getStatus(monitorId) {
            return this.$root.lastHeartbeatList?.[monitorId]?.status ?? -1;
        },

        childrenOf(groupId) {
            return this.allSensors.filter(m => m.parent === groupId);
        },

        sensorsInGroup(groupId) {
            // Direct children (sensors + sub-group sensors)
            const direct = this.allSensors.filter(m => m.parent === groupId);
            const subGroups = this.allGroups.filter(g => g.parent === groupId);
            const sub = subGroups.flatMap(g => this.sensorsInGroup(g.id));
            return [...direct, ...sub];
        },

        childCount(groupId) {
            return this.sensorsInGroup(groupId).length;
        },

        filteredChildren(groupId) {
            const children = this.childrenOf(groupId);
            if (!this.treeSearch) return children;
            const q = this.treeSearch.toLowerCase();
            return children.filter(c => c.name.toLowerCase().includes(q));
        },

        groupDotClass(groupId) {
            const sensors = this.sensorsInGroup(groupId);
            if (sensors.some(m => m.active && this.getStatus(m.id) === STATUS_DOWN)) return "dot-down";
            if (sensors.some(m => m.active && this.getStatus(m.id) === STATUS_PENDING)) return "dot-warn";
            if (sensors.every(m => !m.active)) return "dot-pause";
            return "dot-up";
        },

        monitorDotClass(monitorId) {
            const m = this.$root.monitorList?.[monitorId];
            if (!m || !m.active) return "dot-pause";
            const s = this.getStatus(monitorId);
            if (s === STATUS_DOWN) return "dot-down";
            if (s === STATUS_PENDING) return "dot-warn";
            if (s === STATUS_MAINTENANCE) return "dot-maint";
            if (s === STATUS_UP) return "dot-up";
            return "dot-unknown";
        },

        rowClass(monitorId) {
            const cls = this.monitorDotClass(monitorId);
            return {
                "row-down": cls === "dot-down",
                "row-warn": cls === "dot-warn",
                "row-pause": cls === "dot-pause",
            };
        },

        lastMsg(monitorId) {
            return this.$root.lastHeartbeatList?.[monitorId]?.msg || "—";
        },

        lastTime(monitorId) {
            const t = this.$root.lastHeartbeatList?.[monitorId]?.time;
            return t ? dayjs(t).fromNow() : "—";
        },

        selectAll() {
            this.selectedId = "__all__";
            this.statusFilter = null;
            this.globalSearch = "";
        },

        selectGroup(group) {
            this.selectedId = group.id;
            this.statusFilter = null;
            this.globalSearch = "";
            if (!this.expanded[group.id]) {
                this.expanded[group.id] = true;
            }
        },

        selectMonitor(monitor) {
            this.$router.push("/dashboard/" + monitor.id);
        },

        toggleExpand(groupId) {
            this.expanded[groupId] = !this.expanded[groupId];
        },

        toggleFilter(filter) {
            this.statusFilter = this.statusFilter === filter ? null : filter;
            this.selectedId = "__all__";
            this.globalSearch = "";
        },

        sortBy(field) {
            if (this.sortField === field) {
                this.sortAsc = !this.sortAsc;
            } else {
                this.sortField = field;
                this.sortAsc = true;
            }
        },

        sortIcon(field) {
            if (this.sortField !== field) return "";
            return this.sortAsc ? "↑" : "↓";
        },

        sortList(list) {
            return [...list].sort((a, b) => {
                let va, vb;
                if (this.sortField === "name") {
                    va = a.name; vb = b.name;
                } else if (this.sortField === "msg") {
                    va = this.lastMsg(a.id); vb = this.lastMsg(b.id);
                } else if (this.sortField === "time") {
                    va = this.$root.lastHeartbeatList?.[a.id]?.time || "";
                    vb = this.$root.lastHeartbeatList?.[b.id]?.time || "";
                } else {
                    va = a.name; vb = b.name;
                }
                const cmp = String(va).localeCompare(String(vb));
                return this.sortAsc ? cmp : -cmp;
            });
        },
    },
};
</script>

<style scoped>
/* ── Layout ───────────────────────────────────────────────── */
.nagsa-prtg {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 80px);
    font-size: 13px;
    background: #f0f2f5;
}

.prtg-split {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* ── Status bar ───────────────────────────────────────────── */
.prtg-bar {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    background: #2b2b3b;
    color: #fff;
    flex-shrink: 0;
}

.prtg-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    border: none;
    border-radius: 4px;
    padding: 4px 14px;
    cursor: pointer;
    transition: opacity 0.15s, transform 0.1s;
    min-width: 64px;
    color: #fff;
    font-size: 11px;
}
.prtg-stat:hover { opacity: 0.85; transform: translateY(-1px); }
.prtg-stat.active { outline: 2px solid #fff; outline-offset: 1px; }

.prtg-stat-num { font-size: 18px; font-weight: 700; line-height: 1; }
.prtg-stat-lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 1px; }

.prtg-down  { background: #c0392b; }
.prtg-warn  { background: #e67e22; }
.prtg-up    { background: #27ae60; }
.prtg-pause { background: #5b6c85; }

.prtg-bar-right {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-left: auto;
}

.prtg-search {
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid #555;
    background: #3a3a4d;
    color: #fff;
    font-size: 12px;
    width: 210px;
}
.prtg-search::placeholder { color: #aaa; }
.prtg-search:focus { outline: none; border-color: #7eb3f5; background: #2b2b3b; }

.prtg-total { color: #aaa; font-size: 11px; white-space: nowrap; }

.prtg-add-btn {
    background: #3a7bd5;
    color: #fff;
    border: none;
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 12px;
    text-decoration: none;
    white-space: nowrap;
}
.prtg-add-btn:hover { background: #2f6bc4; color: #fff; }

/* ── Tree panel ───────────────────────────────────────────── */
.prtg-tree {
    width: 270px;
    min-width: 200px;
    max-width: 270px;
    flex-shrink: 0;
    background: #fff;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border-right: 1px solid #dde0e7;
}

.tree-search-wrap {
    padding: 8px;
    border-bottom: 1px solid #eee;
    flex-shrink: 0;
}

.tree-search-input {
    width: 100%;
    padding: 5px 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 12px;
}
.tree-search-input:focus { outline: none; border-color: #7eb3f5; }

.tree-body {
    flex: 1;
    overflow-y: auto;
    padding: 4px 0;
}

.tree-item {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 10px;
    cursor: pointer;
    border-left: 3px solid transparent;
    user-select: none;
    transition: background 0.1s;
}
.tree-item:hover { background: #f0f4ff; }
.tree-item.selected {
    background: #e8f0fe;
    border-left-color: #3a7bd5;
}

.tree-root { font-weight: 600; color: #2b2b3b; }
.tree-icon { font-size: 10px; color: #3a7bd5; }

.tree-group { font-weight: 600; color: #2b2b3b; }
.tree-toggle { font-size: 11px; color: #888; width: 12px; flex-shrink: 0; text-align: center; }

.tree-sensor {
    padding-left: 26px;
    color: #444;
    font-weight: 400;
}

.tree-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; }
.tree-badge {
    font-size: 10px;
    background: #e0e5f0;
    color: #555;
    border-radius: 10px;
    padding: 1px 7px;
    flex-shrink: 0;
}

/* ── Status dots ──────────────────────────────────────────── */
.status-dot, .status-circle {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
    display: inline-block;
}
.status-circle { width: 12px; height: 12px; }

.dot-up      { background: #27ae60; }
.dot-down    { background: #c0392b; box-shadow: 0 0 4px rgba(192,57,43,0.5); }
.dot-warn    { background: #e67e22; }
.dot-pause   { background: #95a5a6; }
.dot-maint   { background: #3498db; }
.dot-unknown { background: #bdc3c7; }

/* ── Content panel ────────────────────────────────────────── */
.prtg-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #f0f2f5;
}

/* Breadcrumb */
.prtg-breadcrumb {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 7px 14px;
    background: #fff;
    border-bottom: 1px solid #dde0e7;
    flex-shrink: 0;
}

.breadcrumb-nav { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.bc-root { color: #3a7bd5; cursor: pointer; }
.bc-root:hover { text-decoration: underline; }
.bc-sep { color: #aaa; }
.bc-current { font-weight: 600; color: #2b2b3b; }

.bc-actions { display: flex; align-items: center; gap: 10px; }
.bc-count { font-size: 11px; color: #888; }
.bc-link-btn {
    font-size: 11px;
    color: #3a7bd5;
    text-decoration: none;
    padding: 2px 8px;
    border: 1px solid #3a7bd5;
    border-radius: 4px;
}
.bc-link-btn:hover { background: #3a7bd5; color: #fff; }

/* Summary pills */
.prtg-summary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: #fff;
    border-bottom: 1px solid #dde0e7;
    flex-shrink: 0;
}

.sum-pill {
    font-size: 11px;
    font-weight: 600;
    color: #fff;
    border-radius: 20px;
    padding: 2px 10px;
}
.pill-down  { background: #c0392b; }
.pill-warn  { background: #e67e22; }
.pill-up    { background: #27ae60; }
.pill-pause { background: #95a5a6; }

/* Table */
.prtg-table-wrap {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
}

.prtg-table {
    width: 100%;
    border-collapse: collapse;
    background: #fff;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    font-size: 12px;
}

.prtg-table thead {
    background: #2b2b3b;
    color: #e0e5f0;
    position: sticky;
    top: 0;
    z-index: 2;
}

.prtg-table th {
    padding: 8px 10px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
}
.prtg-table th:hover { background: #3a3a55; }

.prtg-table td {
    padding: 7px 10px;
    border-bottom: 1px solid #f0f2f5;
    vertical-align: middle;
}

.sensor-row { transition: background 0.1s; }
.sensor-row:hover { background: #f5f7ff !important; }
.sensor-row:last-child td { border-bottom: none; }

.row-down { background: #fff5f5; }
.row-warn { background: #fffaf0; }
.row-pause { background: #fafafa; color: #999; }

.col-st   { width: 32px; text-align: center; }
.col-name { min-width: 180px; }
.col-type { width: 90px; }
.col-val  { min-width: 140px; color: #444; }
.col-time { width: 110px; color: #888; }
.col-act  { width: 40px; text-align: center; }

.sensor-link {
    color: #1a1a2e;
    text-decoration: none;
    font-weight: 600;
}
.sensor-link:hover { color: #3a7bd5; text-decoration: underline; }

.sensor-host { color: #999; font-size: 11px; margin-top: 1px; }

.type-tag {
    background: #e8ecf5;
    color: #445;
    border-radius: 3px;
    padding: 1px 6px;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    font-weight: 600;
}

.row-btn {
    display: inline-block;
    text-decoration: none;
    color: #3a7bd5;
    font-size: 16px;
    font-weight: bold;
    padding: 0 4px;
}
.row-btn:hover { color: #1a5bc4; }

.empty-row {
    text-align: center;
    padding: 32px;
    color: #aaa;
    font-style: italic;
}
</style>
