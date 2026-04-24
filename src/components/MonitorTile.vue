<template>
    <div class="monitor-tile card h-100" :class="statusClass">
        <div class="card-body p-2">
            <div class="d-flex justify-content-between align-items-start mb-1">
                <span class="badge rounded-pill" :class="badgeClass">{{ statusLabel }}</span>
                <small class="text-muted monitor-type-badge">{{ monitor.type }}</small>
            </div>
            <div class="monitor-name fw-semibold text-truncate" :title="monitor.name">{{ monitor.name }}</div>
            <div v-if="lastHeartbeat" class="monitor-msg text-muted small text-truncate mt-1" :title="lastHeartbeat.msg">
                {{ lastHeartbeat.msg }}
            </div>
            <div class="d-flex justify-content-between align-items-center mt-1">
                <small class="text-muted">{{ lastCheckTime }}</small>
                <span v-if="latency !== null" class="badge bg-light text-dark border">{{ latency }} ms</span>
            </div>
        </div>
    </div>
</template>

<script>
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);

export default {
    name: "MonitorTile",
    props: {
        monitor: { type: Object, required: true },
    },
    computed: {
        lastHeartbeat() {
            return this.$root.lastHeartbeatList?.[this.monitor.id] || null;
        },
        status() {
            if (!this.monitor.active) return "paused";
            return this.lastHeartbeat?.status ?? -1;
        },
        statusLabel() {
            if (!this.monitor.active) return "PAUSED";
            const s = this.status;
            if (s === 1) return "UP";
            if (s === 0) return "DOWN";
            if (s === 2) return "PENDING";
            if (s === 3) return "MAINTENANCE";
            return "UNKNOWN";
        },
        statusClass() {
            if (!this.monitor.active) return "border-secondary";
            const s = this.status;
            if (s === 1) return "border-success border-start border-4";
            if (s === 0) return "border-danger border-start border-4";
            if (s === 3) return "border-info border-start border-4";
            return "border-warning border-start border-4";
        },
        badgeClass() {
            if (!this.monitor.active) return "bg-secondary";
            const s = this.status;
            if (s === 1) return "bg-success";
            if (s === 0) return "bg-danger";
            if (s === 3) return "bg-info text-dark";
            return "bg-warning text-dark";
        },
        latency() {
            const ping = this.lastHeartbeat?.ping;
            return ping != null ? ping : null;
        },
        lastCheckTime() {
            const time = this.lastHeartbeat?.time;
            if (!time) return "—";
            return dayjs(time).fromNow();
        },
    },
};
</script>

<style scoped>
.monitor-tile {
    border-left-width: 4px !important;
    transition: box-shadow 0.15s;
    cursor: default;
}
.monitor-tile:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.monitor-name {
    font-size: 0.88rem;
}
.monitor-msg {
    font-size: 0.78rem;
}
.monitor-type-badge {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
</style>
