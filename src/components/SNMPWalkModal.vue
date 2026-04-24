<template>
    <div ref="modal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">SNMP OID Browser</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row g-2 mb-3">
                        <div class="col-sm-4">
                            <label class="form-label form-label-sm">Start OID</label>
                            <input v-model="startOid" type="text" class="form-control form-control-sm" placeholder="1.3.6.1" />
                        </div>
                        <div class="col-sm-2 d-flex align-items-end">
                            <button class="btn btn-primary btn-sm w-100" :disabled="loading" @click="walk">
                                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                                {{ loading ? "Walking..." : "Walk" }}
                            </button>
                        </div>
                    </div>

                    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

                    <div v-if="oids.length > 0">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <small class="text-muted">{{ oids.length }} OIDs found</small>
                            <input v-model="filter" type="text" class="form-control form-control-sm w-auto" placeholder="Filter..." style="min-width: 200px" />
                        </div>
                        <div style="max-height: 400px; overflow-y: auto">
                            <table class="table table-sm table-hover mb-0">
                                <thead class="table-dark sticky-top">
                                    <tr>
                                        <th>OID</th>
                                        <th>Type</th>
                                        <th>Value</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="row in filteredOids" :key="row.oid">
                                        <td class="font-monospace small">{{ row.oid }}</td>
                                        <td><span class="badge bg-secondary">{{ row.typeName }}</span></td>
                                        <td class="small text-break" style="max-width: 300px">{{ row.value }}</td>
                                        <td>
                                            <button class="btn btn-outline-primary btn-sm py-0 px-2" @click="selectOid(row.oid)">
                                                Use
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { Modal } from "bootstrap";

export default {
    name: "SNMPWalkModal",
    emits: ["select-oid"],
    data() {
        return {
            modal: null,
            loading: false,
            error: null,
            oids: [],
            filter: "",
            startOid: "1.3.6.1",
            connectionParams: {},
        };
    },
    computed: {
        filteredOids() {
            if (!this.filter) return this.oids;
            const q = this.filter.toLowerCase();
            return this.oids.filter(r => r.oid.includes(q) || r.typeName.toLowerCase().includes(q) || r.value.toLowerCase().includes(q));
        },
    },
    mounted() {
        this.modal = new Modal(this.$refs.modal);
    },
    methods: {
        show(params) {
            this.connectionParams = params || {};
            this.startOid = "1.3.6.1";
            this.oids = [];
            this.error = null;
            this.filter = "";
            this.modal.show();
        },
        walk() {
            this.loading = true;
            this.error = null;
            this.oids = [];
            const payload = { ...this.connectionParams, startOid: this.startOid };
            this.$root.getSocket().emit("snmpWalk", payload, (res) => {
                this.loading = false;
                if (res.ok) {
                    this.oids = res.oids;
                } else {
                    this.error = res.msg;
                }
            });
        },
        selectOid(oid) {
            this.$emit("select-oid", oid);
            this.modal.hide();
        },
    },
};
</script>
