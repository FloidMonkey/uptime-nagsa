<template>
    <div class="nagsa-prtg">

        <!-- ── Status bar ──────────────────────────────────────── -->
        <div class="prtg-bar">
            <button class="prtg-stat prtg-down" :class="{ active: statusFilter === 'down' }" @click="toggleFilter('down')">
                <span class="prtg-stat-num">{{ countDown }}</span>
                <span class="prtg-stat-lbl">Down</span>
            </button>
            <button class="prtg-stat prtg-warn" :class="{ active: statusFilter === 'warn' }" @click="toggleFilter('warn')">
                <span class="prtg-stat-num">{{ countPending }}</span>
                <span class="prtg-stat-lbl">Warning</span>
            </button>
            <button class="prtg-stat prtg-up" :class="{ active: statusFilter === 'up' }" @click="toggleFilter('up')">
                <span class="prtg-stat-num">{{ countUp }}</span>
                <span class="prtg-stat-lbl">Up</span>
            </button>
            <button class="prtg-stat prtg-pause" :class="{ active: statusFilter === 'paused' }" @click="toggleFilter('paused')">
                <span class="prtg-stat-num">{{ countPaused }}</span>
                <span class="prtg-stat-lbl">Paused</span>
            </button>
            <div class="prtg-bar-right">
                <input v-model="globalSearch" type="text" class="prtg-search" placeholder="Search monitors…" @input="onGlobalSearch" />
                <span class="prtg-total">{{ totalMonitors }} sensors</span>
                <router-link to="/add" class="prtg-add-btn">+ Add Monitor</router-link>
            </div>
        </div>

        <!-- ── Main split ─────────────────────────────────────── -->
        <div class="prtg-split">

            <!-- ── Left: tree ─────────────────────────────────── -->
            <div class="prtg-tree">
                <div class="tree-toolbar">
                    <input v-model="treeSearch" type="text" class="tree-search-input" placeholder="Filter tree…" />
                    <button class="tree-expand-all" title="Expand all" @click="expandAll">⊞</button>
                    <button class="tree-expand-all" title="Collapse all" @click="collapseAll">⊟</button>
                </div>

                <div class="tree-scroll">
                    <!-- Root "All" node -->
                    <div class="tree-root-node" :class="{ 'tree-selected': selectedId === '__all__' }" @click="selectAll">
                        <span class="tree-root-icon">◉</span>
                        <span class="tree-root-label">All Monitors</span>
                        <span class="tree-root-counts">
                            <span v-if="countDown > 0" class="root-badge root-badge-down">{{ countDown }} ↓</span>
                            <span class="root-badge root-badge-up">{{ countUp }} ↑</span>
                        </span>
                    </div>

                    <!-- Groups -->
                    <div v-for="group in filteredTree" :key="group.id" class="tree-group-block">

                        <!-- Group header row -->
                        <div
                            class="tree-node tree-group-node"
                            :class="{ 'tree-selected': selectedId === group.id }"
                            @click="selectGroup(group)"
                        >
                            <button class="tree-toggler" @click.stop="toggleExpand(group.id)">
                                {{ expanded[group.id] ? '▾' : '▸' }}
                            </button>
                            <span class="status-box" :class="groupBoxClass(group.id)">
                                {{ groupBoxLabel(group.id) }}
                            </span>
                            <span class="tree-node-name">{{ group.name }}</span>
                            <span class="group-summary">
                                <span v-if="groupDown(group.id) > 0" class="gsummary-down">{{ groupDown(group.id) }} ↓</span>
                                <span class="gsummary-total">{{ childCount(group.id) }}</span>
                            </span>
                        </div>

                        <!-- Children -->
                        <div v-if="expanded[group.id]" class="tree-children">
                            <div
                                v-for="(child, idx) in filteredChildren(group.id)"
                                :key="child.id"
                                class="tree-node tree-leaf-node"
                                :class="{ 'tree-selected': selectedId === child.id, 'tree-last-leaf': idx === filteredChildren(group.id).length - 1 }"
                                @click="selectMonitor(child)"
                            >
                                <span class="leaf-connector"></span>
                                <span class="status-box status-box-sm" :class="monitorBoxClass(child.id)">
                                    {{ monitorBoxLabel(child.id) }}
                                </span>
                                <span class="tree-node-name leaf-name">{{ child.name }}</span>
                                <span class="leaf-value">{{ leafValue(child.id) }}</span>
                            </div>
                        </div>

                    </div>
                </div>
            </div>

            <!-- ── Right: content ─────────────────────────────── -->
            <div class="prtg-content">

                <!-- Breadcrumb -->
                <div class="prtg-breadcrumb">
                    <div class="bc-left">
                        <span class="bc-home" @click="selectAll">Home</span>
                        <template v-if="selectedGroup">
                            <span class="bc-sep">›</span>
                            <span class="bc-page">{{ selectedGroup.name }}</span>
                        </template>
                        <template v-else-if="statusFilter">
                            <span class="bc-sep">›</span>
                            <span class="bc-page text-capitalize">{{ statusFilter }}</span>
                        </template>
                        <template v-else-if="globalSearch">
                            <span class="bc-sep">›</span>
                            <span class="bc-page">Search: "{{ globalSearch }}"</span>
                        </template>
                        <template v-else>
                            <span class="bc-sep">›</span>
                            <span class="bc-page">All Monitors</span>
                        </template>
                    </div>
                    <div class="bc-right">
                        <span class="bc-info">{{ displayedMonitors.length }} sensors</span>
                        <router-link v-if="selectedGroup" :to="'/dashboard/' + selectedGroup.id" class="bc-detail-btn">
                            Open in Kuma ›
                        </router-link>
                    </div>
                </div>

                <!-- Summary row -->
                <div class="prtg-summary-row">
                    <div class="sum-card sum-card-down">
                        <span class="sum-num">{{ displayDown }}</span>
                        <span class="sum-lbl">Down</span>
                    </div>
                    <div class="sum-card sum-card-warn">
                        <span class="sum-num">{{ displayPending }}</span>
                        <span class="sum-lbl">Warning</span>
                    </div>
                    <div class="sum-card sum-card-up">
                        <span class="sum-num">{{ displayUp }}</span>
                        <span class="sum-lbl">Up</span>
                    </div>
                    <div class="sum-card sum-card-pause">
                        <span class="sum-num">{{ displayPaused }}</span>
                        <span class="sum-lbl">Paused</span>
                    </div>
                </div>

                <!-- Sensor table -->
                <div class="prtg-table-wrap">
                    <table class="prtg-table">
                        <thead>
                            <tr>
                                <th class="th-status" @click="sortBy('status')">Status {{ sortIcon('status') }}</th>
                                <th class="th-name" @click="sortBy('name')">Sensor / Monitor {{ sortIcon('name') }}</th>
                                <th class="th-type">Type</th>
                                <th class="th-val" @click="sortBy('msg')">Last Value {{ sortIcon('msg') }}</th>
                                <th class="th-time" @click="sortBy('time')">Last Check {{ sortIcon('time') }}</th>
                                <th class="th-act"></th>
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
                                :class="tableRowClass(m.id)"
                                @dblclick="$router.push('/dashboard/' + m.id)"
                            >
                                <td class="td-status">
                                    <span class="status-box status-box-sm" :class="monitorBoxClass(m.id)">
                                        {{ monitorBoxLabel(m.id) }}
                                    </span>
                                </td>
                                <td class="td-name">
                                    <router-link :to="'/dashboard/' + m.id" class="sensor-link">{{ m.name }}</router-link>
                                    <div v-if="m.hostname" class="sensor-host">{{ m.hostname }}</div>
                                </td>
                                <td class="td-type">
                                    <span class="type-tag">{{ m.type }}</span>
                                </td>
                                <td class="td-val">{{ lastMsg(m.id) }}</td>
                                <td class="td-time">{{ lastTime(m.id) }}</td>
                                <td class="td-act">
                                    <router-link :to="'/dashboard/' + m.id" class="row-go-btn" title="Open detail">›</router-link>
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

const UP = 1, DOWN = 0, PENDING = 2, MAINTENANCE = 3;

export default {
    name: "NagsaDashboard",

    data() {
        return {
            selectedId: "__all__",
            treeSearch: "",
            globalSearch: "",
            statusFilter: null,
            expanded: {},
            sortField: "status",
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
        rootGroups() {
            const groupIds = new Set(this.allGroups.map(g => g.id));
            return this.allGroups
                .filter(g => !g.parent || !groupIds.has(g.parent))
                .sort((a, b) => a.name.localeCompare(b.name));
        },
        filteredTree() {
            if (!this.treeSearch) return this.rootGroups;
            const q = this.treeSearch.toLowerCase();
            return this.rootGroups.filter(g =>
                g.name.toLowerCase().includes(q) ||
                this.sensorsInGroup(g.id).some(c => c.name.toLowerCase().includes(q))
            );
        },
        selectedGroup() {
            if (!this.selectedId || this.selectedId === "__all__") return null;
            const m = this.$root.monitorList?.[this.selectedId];
            return m?.type === "group" ? m : null;
        },

        // Global counts
        countDown()    { return this.allSensors.filter(m => m.active && this.getStatus(m.id) === DOWN).length; },
        countPending() { return this.allSensors.filter(m => m.active && this.getStatus(m.id) === PENDING).length; },
        countUp()      { return this.allSensors.filter(m => m.active && this.getStatus(m.id) === UP).length; },
        countPaused()  { return this.allSensors.filter(m => !m.active).length; },

        displayedMonitors() {
            let list;
            if (this.globalSearch) {
                const q = this.globalSearch.toLowerCase();
                list = this.allSensors.filter(m =>
                    m.name.toLowerCase().includes(q) || (m.hostname || "").toLowerCase().includes(q)
                );
            } else if (this.statusFilter) {
                list = this.allSensors.filter(m => {
                    const s = this.getStatus(m.id);
                    if (this.statusFilter === "down")   return m.active && s === DOWN;
                    if (this.statusFilter === "warn")   return m.active && s === PENDING;
                    if (this.statusFilter === "up")     return m.active && s === UP;
                    if (this.statusFilter === "paused") return !m.active;
                    return true;
                });
            } else if (this.selectedId && this.selectedId !== "__all__") {
                const sel = this.$root.monitorList?.[this.selectedId];
                list = sel?.type === "group" ? this.sensorsInGroup(this.selectedId) : (sel ? [sel] : []);
            } else {
                list = this.allSensors;
            }
            return this.sortedList(list);
        },

        displayDown()    { return this.displayedMonitors.filter(m => m.active && this.getStatus(m.id) === DOWN).length; },
        displayUp()      { return this.displayedMonitors.filter(m => m.active && this.getStatus(m.id) === UP).length; },
        displayPending() { return this.displayedMonitors.filter(m => m.active && this.getStatus(m.id) === PENDING).length; },
        displayPaused()  { return this.displayedMonitors.filter(m => !m.active).length; },
    },

    mounted() {
        for (const g of this.rootGroups) {
            const hasDown = this.sensorsInGroup(g.id).some(m => m.active && this.getStatus(m.id) === DOWN);
            this.expanded[g.id] = hasDown;
        }
    },

    methods: {
        getStatus(id) {
            return this.$root.lastHeartbeatList?.[id]?.status ?? -1;
        },
        sensorsInGroup(groupId) {
            const direct = this.allSensors.filter(m => m.parent === groupId);
            const subs = this.allGroups.filter(g => g.parent === groupId);
            return [...direct, ...subs.flatMap(g => this.sensorsInGroup(g.id))];
        },
        childrenOf(groupId) {
            return this.allSensors.filter(m => m.parent === groupId);
        },
        filteredChildren(groupId) {
            const kids = this.childrenOf(groupId);
            if (!this.treeSearch) return kids;
            const q = this.treeSearch.toLowerCase();
            return kids.filter(c => c.name.toLowerCase().includes(q));
        },
        childCount(groupId) { return this.sensorsInGroup(groupId).length; },
        groupDown(groupId)  { return this.sensorsInGroup(groupId).filter(m => m.active && this.getStatus(m.id) === DOWN).length; },

        // Status box class/label for groups
        groupBoxClass(groupId) {
            const sensors = this.sensorsInGroup(groupId);
            if (!sensors.length) return "box-unknown";
            if (sensors.some(m => m.active && this.getStatus(m.id) === DOWN))    return "box-down";
            if (sensors.some(m => m.active && this.getStatus(m.id) === PENDING)) return "box-warn";
            if (sensors.every(m => !m.active))                                   return "box-pause";
            return "box-up";
        },
        groupBoxLabel(groupId) {
            const cls = this.groupBoxClass(groupId);
            return { "box-down": "Down", "box-warn": "Warn", "box-pause": "Pause", "box-up": "OK", "box-unknown": "?" }[cls];
        },

        // Status box class/label for individual monitors
        monitorBoxClass(id) {
            const m = this.$root.monitorList?.[id];
            if (!m || !m.active) return "box-pause";
            const s = this.getStatus(id);
            if (s === DOWN)        return "box-down";
            if (s === PENDING)     return "box-warn";
            if (s === MAINTENANCE) return "box-maint";
            if (s === UP)          return "box-up";
            return "box-unknown";
        },
        monitorBoxLabel(id) {
            const cls = this.monitorBoxClass(id);
            return { "box-down": "Down", "box-warn": "Warn", "box-pause": "Pause", "box-maint": "Maint", "box-up": "OK", "box-unknown": "?" }[cls];
        },

        tableRowClass(id) {
            const cls = this.monitorBoxClass(id);
            return { "row-down": cls === "box-down", "row-warn": cls === "box-warn", "row-pause": cls === "box-pause" };
        },

        // Value to show in tree leaf
        leafValue(id) {
            const hb = this.$root.lastHeartbeatList?.[id];
            if (!hb) return "";
            if (hb.status === DOWN) return "⚠ Down";
            const msg = hb.msg || "";
            const match = msg.match(/SNMP OK:\s*(.+)/);
            if (match) return match[1].trim();
            if (hb.ping != null) return hb.ping + " ms";
            return "";
        },

        lastMsg(id) {
            return this.$root.lastHeartbeatList?.[id]?.msg || "—";
        },
        lastTime(id) {
            const t = this.$root.lastHeartbeatList?.[id]?.time;
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
            this.expanded[group.id] = true;
        },
        selectMonitor(m) {
            this.$router.push("/dashboard/" + m.id);
        },
        toggleExpand(id) {
            this.expanded[id] = !this.expanded[id];
        },
        expandAll()   { for (const g of this.rootGroups) this.expanded[g.id] = true; },
        collapseAll() { for (const g of this.rootGroups) this.expanded[g.id] = false; },

        toggleFilter(f) {
            this.statusFilter = this.statusFilter === f ? null : f;
            this.selectedId = "__all__";
            this.globalSearch = "";
        },
        onGlobalSearch() {
            if (this.globalSearch) {
                this.selectedId = "__all__";
                this.statusFilter = null;
            }
        },

        sortBy(field) {
            this.sortAsc = this.sortField === field ? !this.sortAsc : true;
            this.sortField = field;
        },
        sortIcon(field) {
            return this.sortField === field ? (this.sortAsc ? " ↑" : " ↓") : "";
        },
        sortedList(list) {
            const statusOrder = { [DOWN]: 0, [PENDING]: 1, [-1]: 2, [MAINTENANCE]: 3, [UP]: 4 };
            return [...list].sort((a, b) => {
                let va, vb;
                if (this.sortField === "status") {
                    const sa = this.$root.monitorList?.[a.id]?.active ? (this.getStatus(a.id)) : 99;
                    const sb = this.$root.monitorList?.[b.id]?.active ? (this.getStatus(b.id)) : 99;
                    va = statusOrder[sa] ?? 5;
                    vb = statusOrder[sb] ?? 5;
                    if (va !== vb) return this.sortAsc ? va - vb : vb - va;
                    return a.name.localeCompare(b.name);
                }
                if (this.sortField === "name") { va = a.name; vb = b.name; }
                else if (this.sortField === "msg") { va = this.lastMsg(a.id); vb = this.lastMsg(b.id); }
                else if (this.sortField === "time") {
                    va = this.$root.lastHeartbeatList?.[a.id]?.time || "";
                    vb = this.$root.lastHeartbeatList?.[b.id]?.time || "";
                } else { va = a.name; vb = b.name; }
                const c = String(va).localeCompare(String(vb));
                return this.sortAsc ? c : -c;
            });
        },
    },
};
</script>

<style scoped>
/* ── Base layout ───────────────────────────────────────── */
.nagsa-prtg {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 80px);
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
    background: #eef0f5;
}
.prtg-split { display: flex; flex: 1; overflow: hidden; }

/* ── Status bar ────────────────────────────────────────── */
.prtg-bar {
    display: flex;
    align-items: center;
    gap: 3px;
    padding: 5px 12px;
    background: #23253a;
    flex-shrink: 0;
}
.prtg-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    border: 2px solid transparent;
    border-radius: 5px;
    padding: 4px 16px;
    cursor: pointer;
    color: #fff;
    min-width: 70px;
    transition: filter 0.15s, border-color 0.15s;
}
.prtg-stat:hover  { filter: brightness(1.15); }
.prtg-stat.active { border-color: #fff; }
.prtg-stat-num  { font-size: 20px; font-weight: 700; line-height: 1.1; }
.prtg-stat-lbl  { font-size: 10px; text-transform: uppercase; letter-spacing: .05em; }
.prtg-down  { background: #b03030; }
.prtg-warn  { background: #c87020; }
.prtg-up    { background: #258a45; }
.prtg-pause { background: #4a5a78; }

.prtg-bar-right { display: flex; align-items: center; gap: 10px; margin-left: auto; }
.prtg-search {
    padding: 5px 10px; border-radius: 4px;
    border: 1px solid #444; background: #32344a; color: #e8e8f0;
    font-size: 12px; width: 220px;
}
.prtg-search::placeholder { color: #888; }
.prtg-search:focus { outline: none; border-color: #6a9fd8; }
.prtg-total { color: #888; font-size: 11px; }
.prtg-add-btn {
    background: #2e6fc4; color: #fff; border-radius: 4px;
    padding: 5px 12px; font-size: 12px; text-decoration: none; white-space: nowrap;
}
.prtg-add-btn:hover { background: #2460b0; color: #fff; }

/* ── Tree panel ────────────────────────────────────────── */
.prtg-tree {
    width: 290px; min-width: 220px; max-width: 290px;
    background: #fff; display: flex; flex-direction: column;
    overflow: hidden; border-right: 1px solid #d0d5e0; flex-shrink: 0;
}

.tree-toolbar {
    display: flex; gap: 4px; align-items: center;
    padding: 7px 8px; border-bottom: 1px solid #e4e8f0; flex-shrink: 0;
    background: #f7f8fc;
}
.tree-search-input {
    flex: 1; padding: 4px 8px; border: 1px solid #c8cfe0;
    border-radius: 3px; font-size: 12px;
}
.tree-search-input:focus { outline: none; border-color: #6a9fd8; }
.tree-expand-all {
    background: #e8ecf5; border: 1px solid #c8cfe0; border-radius: 3px;
    padding: 3px 6px; cursor: pointer; font-size: 14px; color: #556;
}
.tree-expand-all:hover { background: #d8dff0; }

.tree-scroll { flex: 1; overflow-y: auto; padding-bottom: 12px; }

/* Root node */
.tree-root-node {
    display: flex; align-items: center; gap: 7px;
    padding: 8px 10px; cursor: pointer; font-weight: 700;
    border-bottom: 1px solid #e4e8f0; color: #1a1e2e;
    background: #f0f3fb;
}
.tree-root-node:hover { background: #e4e8f5; }
.tree-root-node.tree-selected { background: #dae4f8; border-left: 3px solid #2e6fc4; }
.tree-root-icon { color: #2e6fc4; font-size: 14px; }
.tree-root-label { flex: 1; font-size: 12px; }
.tree-root-counts { display: flex; gap: 4px; }
.root-badge {
    font-size: 10px; font-weight: 700; border-radius: 10px;
    padding: 1px 7px; color: #fff;
}
.root-badge-down  { background: #b03030; }
.root-badge-up    { background: #258a45; }

/* Group block */
.tree-group-block { border-bottom: 1px solid #ebebf0; }

/* Tree node (group and leaf share base) */
.tree-node {
    display: flex; align-items: center; gap: 5px;
    padding: 6px 8px; cursor: pointer; transition: background .1s;
    border-left: 3px solid transparent;
}
.tree-node:hover { background: #f2f5fc; }
.tree-node.tree-selected { background: #dae4f8; border-left-color: #2e6fc4; }

.tree-group-node { font-weight: 600; color: #1a1e2e; background: #fafbfd; }

.tree-toggler {
    background: none; border: none; padding: 0; cursor: pointer;
    color: #778; font-size: 12px; width: 14px; flex-shrink: 0;
    line-height: 1;
}
.tree-toggler:hover { color: #2e6fc4; }

.tree-node-name { flex: 1; font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.group-summary { display: flex; align-items: center; gap: 3px; flex-shrink: 0; }
.gsummary-down  { font-size: 10px; font-weight: 700; color: #b03030; }
.gsummary-total { font-size: 10px; color: #888; background: #e4e8f0; border-radius: 10px; padding: 0 6px; }

/* Children / leaf nodes */
.tree-children { position: relative; padding-left: 0; }
.tree-children::before {
    content: ''; position: absolute;
    left: 22px; top: 0; bottom: 14px;
    width: 1px; background: #c8d0e0;
    pointer-events: none;
}

.tree-leaf-node {
    padding-left: 12px;
    color: #344; font-weight: 400;
    background: #fff;
    position: relative;
}

.leaf-connector {
    display: inline-block; position: relative;
    width: 18px; flex-shrink: 0; height: 1px;
    margin-right: 2px;
}
.leaf-connector::before {
    content: ''; position: absolute;
    top: 0; left: 10px; width: 8px; height: 1px;
    background: #c8d0e0;
}

.leaf-name { font-size: 11.5px; }

.leaf-value {
    font-size: 11px; color: #667;
    margin-left: auto; white-space: nowrap; padding-left: 6px;
    font-variant-numeric: tabular-nums;
    flex-shrink: 0;
}

/* ── Status boxes ──────────────────────────────────────── */
.status-box {
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700; border-radius: 3px;
    padding: 2px 6px; color: #fff; white-space: nowrap; flex-shrink: 0;
    min-width: 38px; letter-spacing: .03em;
}
.status-box-sm { min-width: 32px; padding: 1px 5px; font-size: 9.5px; }

.box-up      { background: #258a45; }
.box-down    { background: #b03030; }
.box-warn    { background: #c87020; }
.box-pause   { background: #4a5a78; }
.box-maint   { background: #2874a6; }
.box-unknown { background: #8a8fa0; }

/* ── Content panel ─────────────────────────────────────── */
.prtg-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* Breadcrumb */
.prtg-breadcrumb {
    display: flex; align-items: center; justify-content: space-between;
    padding: 7px 14px; background: #fff;
    border-bottom: 2px solid #d0d5e0; flex-shrink: 0;
}
.bc-left  { display: flex; align-items: center; gap: 5px; font-size: 12px; }
.bc-home  { color: #2e6fc4; cursor: pointer; font-weight: 600; }
.bc-home:hover { text-decoration: underline; }
.bc-sep   { color: #aaa; font-size: 14px; }
.bc-page  { color: #1a1e2e; font-weight: 600; }
.bc-right { display: flex; align-items: center; gap: 10px; }
.bc-info  { font-size: 11px; color: #888; }
.bc-detail-btn {
    font-size: 11px; color: #2e6fc4; text-decoration: none;
    padding: 2px 8px; border: 1px solid #2e6fc4; border-radius: 3px;
}
.bc-detail-btn:hover { background: #2e6fc4; color: #fff; }

/* Summary cards */
.prtg-summary-row {
    display: flex; gap: 1px; background: #d0d5e0;
    flex-shrink: 0; border-bottom: 1px solid #d0d5e0;
}
.sum-card {
    flex: 1; display: flex; align-items: center; gap: 8px;
    padding: 7px 14px; color: #fff;
}
.sum-card-down  { background: #b03030; }
.sum-card-warn  { background: #c87020; }
.sum-card-up    { background: #258a45; }
.sum-card-pause { background: #4a5a78; }
.sum-num { font-size: 20px; font-weight: 700; line-height: 1; }
.sum-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: .04em; opacity: .9; }

/* Table */
.prtg-table-wrap { flex: 1; overflow-y: auto; }

.prtg-table {
    width: 100%; border-collapse: collapse;
    background: #fff; font-size: 12px;
}
.prtg-table thead {
    background: #2c2f4a; color: #c8d0e8;
    position: sticky; top: 0; z-index: 2;
}
.prtg-table th {
    padding: 8px 12px; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .05em;
    white-space: nowrap; cursor: pointer; user-select: none;
    border-right: 1px solid #3c3f5a;
}
.prtg-table th:hover { background: #3c3f5a; }
.prtg-table th:last-child { border-right: none; }

.prtg-table td {
    padding: 6px 12px; border-bottom: 1px solid #eef0f5;
    vertical-align: middle; border-right: 1px solid #f0f2f8;
}
.prtg-table td:last-child { border-right: none; }

.sensor-row { transition: background .1s; }
.sensor-row:hover td { background: #f0f5ff; }
.row-down td { background: #fff0f0; }
.row-warn td { background: #fffbf0; }
.row-pause td { background: #f8f8fa; color: #888; }
.row-down:hover td { background: #ffe8e8; }
.row-warn:hover td { background: #fff5e0; }

.th-status { width: 70px; }
.th-name   { min-width: 180px; }
.th-type   { width: 80px; }
.th-val    { min-width: 150px; }
.th-time   { width: 110px; }
.th-act    { width: 36px; }

.td-status { text-align: center; }
.td-name   { }
.td-type   { }
.td-val    { color: #334; }
.td-time   { color: #778; }
.td-act    { text-align: center; padding: 4px; }

.sensor-link { color: #1a2050; font-weight: 600; text-decoration: none; }
.sensor-link:hover { color: #2e6fc4; text-decoration: underline; }
.sensor-host { font-size: 11px; color: #99a; margin-top: 1px; }

.type-tag {
    background: #e8ecf5; color: #445; border-radius: 3px;
    padding: 1px 6px; font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .03em;
}

.row-go-btn {
    display: inline-block; color: #2e6fc4;
    text-decoration: none; font-size: 18px; font-weight: bold;
    line-height: 1; padding: 0 4px;
}
.row-go-btn:hover { color: #1a4a9a; }

.empty-row { text-align: center; padding: 40px; color: #aaa; font-style: italic; }
</style>
