<template>
    <div class="nagsa-dashboard p-3">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="mb-0">
                <i class="bi bi-graph-up me-2"></i>Network Overview
            </h4>
            <div class="dashboard-stats d-flex gap-3">
                <span class="badge bg-success fs-6">UP {{ countUp }}</span>
                <span class="badge bg-danger fs-6">DOWN {{ countDown }}</span>
                <span class="badge bg-secondary fs-6">PAUSED {{ countPaused }}</span>
            </div>
        </div>

        <ul class="nav nav-tabs mb-3">
            <li class="nav-item">
                <a class="nav-link" :class="{ active: tab === 'summary' }" href="#" @click.prevent="tab = 'summary'">Summary</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" :class="{ active: tab === 'by-group' }" href="#" @click.prevent="tab = 'by-group'">By Group</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" :class="{ active: tab === 'all' }" href="#" @click.prevent="tab = 'all'">All Monitors</a>
            </li>
        </ul>

        <!-- Summary tab -->
        <div v-if="tab === 'summary'">
            <div class="row g-3 mb-4">
                <div class="col-md-3 col-sm-6">
                    <div class="card text-center border-success">
                        <div class="card-body py-3">
                            <div class="display-5 text-success fw-bold">{{ countUp }}</div>
                            <div class="text-muted small">UP</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="card text-center border-danger">
                        <div class="card-body py-3">
                            <div class="display-5 text-danger fw-bold">{{ countDown }}</div>
                            <div class="text-muted small">DOWN</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="card text-center border-warning">
                        <div class="card-body py-3">
                            <div class="display-5 text-warning fw-bold">{{ countPending }}</div>
                            <div class="text-muted small">PENDING</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="card text-center border-secondary">
                        <div class="card-body py-3">
                            <div class="display-5 text-secondary fw-bold">{{ countPaused }}</div>
                            <div class="text-muted small">PAUSED</div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="downMonitors.length > 0" class="mb-4">
                <h6 class="text-danger mb-2"><i class="bi bi-exclamation-triangle-fill me-1"></i>Down Monitors</h6>
                <div class="row g-2">
                    <div v-for="m in downMonitors" :key="m.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                        <router-link :to="'/dashboard/' + m.id" class="text-decoration-none">
                            <MonitorTile :monitor="m" />
                        </router-link>
                    </div>
                </div>
            </div>
        </div>

        <!-- By Group tab -->
        <div v-if="tab === 'by-group'">
            <div v-for="group in groupedMonitors" :key="group.id" class="mb-4">
                <div class="d-flex align-items-center mb-2">
                    <h6 class="mb-0 me-2">{{ group.name }}</h6>
                    <span class="badge bg-success me-1">{{ group.up }} up</span>
                    <span v-if="group.down > 0" class="badge bg-danger me-1">{{ group.down }} down</span>
                </div>
                <div class="row g-2">
                    <div v-for="m in group.monitors" :key="m.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                        <router-link :to="'/dashboard/' + m.id" class="text-decoration-none">
                            <MonitorTile :monitor="m" />
                        </router-link>
                    </div>
                </div>
            </div>
            <div v-if="ungroupedMonitors.length > 0" class="mb-4">
                <h6 class="text-muted mb-2">Ungrouped</h6>
                <div class="row g-2">
                    <div v-for="m in ungroupedMonitors" :key="m.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                        <router-link :to="'/dashboard/' + m.id" class="text-decoration-none">
                            <MonitorTile :monitor="m" />
                        </router-link>
                    </div>
                </div>
            </div>
        </div>

        <!-- All Monitors tab -->
        <div v-if="tab === 'all'">
            <div class="mb-2">
                <input v-model="searchAll" type="text" class="form-control" placeholder="Filter monitors..." />
            </div>
            <div class="row g-2">
                <div v-for="m in filteredAllMonitors" :key="m.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                    <router-link :to="'/dashboard/' + m.id" class="text-decoration-none">
                        <MonitorTile :monitor="m" />
                    </router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import MonitorTile from "../components/MonitorTile.vue";

export default {
    name: "NagsaDashboard",
    components: { MonitorTile },
    data() {
        return {
            tab: "summary",
            searchAll: "",
        };
    },
    computed: {
        allMonitors() {
            return Object.values(this.$root.monitorList || {}).filter(m => m.type !== "group");
        },
        countUp() {
            return this.allMonitors.filter(m => m.active && this.getStatus(m) === 1).length;
        },
        countDown() {
            return this.allMonitors.filter(m => m.active && this.getStatus(m) === 0).length;
        },
        countPending() {
            return this.allMonitors.filter(m => m.active && this.getStatus(m) === 2).length;
        },
        countPaused() {
            return this.allMonitors.filter(m => !m.active).length;
        },
        downMonitors() {
            return this.allMonitors.filter(m => m.active && this.getStatus(m) === 0);
        },
        groups() {
            return Object.values(this.$root.monitorList || {}).filter(m => m.type === "group");
        },
        groupedMonitors() {
            return this.groups.map(g => {
                const monitors = this.allMonitors.filter(m => m.parent === g.id);
                return {
                    id: g.id,
                    name: g.name,
                    monitors,
                    up: monitors.filter(m => m.active && this.getStatus(m) === 1).length,
                    down: monitors.filter(m => m.active && this.getStatus(m) === 0).length,
                };
            }).filter(g => g.monitors.length > 0);
        },
        ungroupedMonitors() {
            const groupIds = new Set(this.groups.map(g => g.id));
            return this.allMonitors.filter(m => !m.parent || !groupIds.has(m.parent));
        },
        filteredAllMonitors() {
            if (!this.searchAll) return this.allMonitors;
            const q = this.searchAll.toLowerCase();
            return this.allMonitors.filter(m => m.name.toLowerCase().includes(q) || (m.hostname || "").toLowerCase().includes(q));
        },
    },
    methods: {
        getStatus(monitor) {
            return this.$root.lastHeartbeatList?.[monitor.id]?.status ?? -1;
        },
    },
};
</script>

<style scoped>
.nagsa-dashboard {
    min-height: 100vh;
}
</style>
