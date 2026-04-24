<template>
    <div ref="modal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <span v-if="step === 1">Device Templates</span>
                        <span v-else>Configure — {{ selectedTemplate && selectedTemplate.name }}</span>
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- Step 1: pick template -->
                    <div v-if="step === 1">
                        <div v-if="loadError" class="alert alert-danger py-2">{{ loadError }}</div>
                        <div v-else-if="templates.length === 0" class="text-center py-4 text-muted">
                            <span class="spinner-border spinner-border-sm me-2"></span>Loading templates...
                        </div>
                        <div v-else class="list-group">
                            <button
                                v-for="t in templates"
                                :key="t.id"
                                class="list-group-item list-group-item-action"
                                @click="pickTemplate(t)"
                            >
                                <div class="d-flex justify-content-between">
                                    <strong>{{ t.name }}</strong>
                                    <span class="badge bg-info text-dark">SNMPv{{ t.snmpVersion }}</span>
                                </div>
                                <small class="text-muted">{{ t.description }}</small>
                                <div class="mt-1">
                                    <span v-for="m in t.monitors" :key="m.name" class="badge bg-secondary me-1">{{ m.type }}</span>
                                    <small class="text-muted ms-1">{{ t.monitors.length }} monitors</small>
                                </div>
                            </button>
                        </div>
                    </div>

                    <!-- Step 2: fill params -->
                    <div v-if="step === 2">
                        <div class="row g-3">
                            <div class="col-sm-6">
                                <label class="form-label">Hostname / IP <span class="text-danger">*</span></label>
                                <input v-model="form.hostname" type="text" class="form-control" placeholder="10.0.0.1" required />
                            </div>
                            <div class="col-sm-6">
                                <label class="form-label">Device Name</label>
                                <input v-model="form.deviceName" type="text" class="form-control" placeholder="Router-Core" />
                                <div class="form-text">Used in monitor names — defaults to hostname</div>
                            </div>
                            <div class="col-sm-6">
                                <label class="form-label">Interval (s)</label>
                                <input v-model.number="form.interval" type="number" class="form-control" min="30" />
                            </div>
                            <div class="col-sm-6">
                                <label class="form-label">Group (optional)</label>
                                <select v-model="form.groupId" class="form-select">
                                    <option :value="null">— none —</option>
                                    <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
                                </select>
                            </div>

                            <template v-if="selectedTemplate && selectedTemplate.snmpVersion === '3'">
                                <div class="col-12"><hr class="my-1" /><strong>SNMPv3 Credentials</strong></div>
                                <div class="col-sm-6">
                                    <label class="form-label">Username <span class="text-danger">*</span></label>
                                    <input v-model="form.snmpV3Username" type="text" class="form-control" />
                                </div>
                                <div class="col-sm-3">
                                    <label class="form-label">Auth Protocol</label>
                                    <select v-model="form.snmpAuthProtocol" class="form-select">
                                        <option>MD5</option>
                                        <option>SHA</option>
                                        <option>SHA256</option>
                                    </select>
                                </div>
                                <div class="col-sm-3">
                                    <label class="form-label">Priv Protocol</label>
                                    <select v-model="form.snmpPrivProtocol" class="form-select">
                                        <option>DES</option>
                                        <option>AES</option>
                                    </select>
                                </div>
                                <div class="col-sm-6">
                                    <label class="form-label">Auth Password</label>
                                    <input v-model="form.snmpAuthPass" type="password" class="form-control" />
                                </div>
                                <div class="col-sm-6">
                                    <label class="form-label">Priv Password</label>
                                    <input v-model="form.snmpPrivPass" type="password" class="form-control" />
                                </div>
                            </template>
                        </div>

                        <div v-if="applyError" class="alert alert-danger py-2 mt-3">{{ applyError }}</div>
                        <div v-if="applyResult" class="alert alert-success py-2 mt-3">
                            {{ applyResult.created }} monitors created successfully.
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <button v-if="step === 2 && !applyResult" type="button" class="btn btn-secondary" @click="step = 1">Back</button>
                    <button v-if="applyResult" type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button
                        v-if="step === 2 && !applyResult"
                        type="button"
                        class="btn btn-primary"
                        :disabled="applying || !form.hostname"
                        @click="apply"
                    >
                        <span v-if="applying" class="spinner-border spinner-border-sm me-1"></span>
                        Create Monitors
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { Modal } from "bootstrap";

export default {
    name: "DeviceTemplateModal",
    data() {
        return {
            modal: null,
            step: 1,
            templates: [],
            loadError: null,
            selectedTemplate: null,
            applying: false,
            applyError: null,
            applyResult: null,
            form: {
                hostname: "",
                deviceName: "",
                interval: 60,
                groupId: null,
                snmpV3Username: "",
                snmpAuthProtocol: "MD5",
                snmpPrivProtocol: "DES",
                snmpAuthPass: "",
                snmpPrivPass: "",
            },
        };
    },
    computed: {
        groups() {
            return Object.values(this.$root.monitorList || {}).filter(m => m.type === "group");
        },
    },
    mounted() {
        this.modal = new Modal(this.$refs.modal);
    },
    methods: {
        show() {
            this.step = 1;
            this.applyResult = null;
            this.applyError = null;
            this.loadError = null;
            this.modal.show();
            this.loadTemplates();
        },
        loadTemplates() {
            this.$root.getSocket().emit("getSnmpTemplates", (res) => {
                if (res.ok) {
                    this.templates = res.templates;
                } else {
                    this.loadError = res.msg;
                }
            });
        },
        pickTemplate(t) {
            this.selectedTemplate = t;
            this.form.hostname = "";
            this.form.deviceName = "";
            this.form.interval = 60;
            this.form.groupId = null;
            this.applyError = null;
            this.applyResult = null;
            this.step = 2;
        },
        apply() {
            this.applying = true;
            this.applyError = null;
            const payload = {
                templateId: this.selectedTemplate.id,
                ...this.form,
            };
            this.$root.getSocket().emit("applySnmpTemplate", payload, (res) => {
                this.applying = false;
                if (res.ok) {
                    this.applyResult = res;
                } else {
                    this.applyError = res.msg;
                }
            });
        },
    },
};
</script>
