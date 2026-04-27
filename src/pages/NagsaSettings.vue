<template>
    <div class="nsc-wrap">
        <div class="nsc-topbar">
            <router-link to="/nagsa-dashboard" class="nsc-back">← Dashboard</router-link>
            <span class="nsc-title">Configuración NAGSA</span>
        </div>

        <div class="nsc-body">

            <!-- ── Iconos ── -->
            <div class="nsc-section">
                <div class="nsc-sec-hdr">
                    <span class="nsc-sec-title">Iconos de Dispositivos</span>
                    <span class="nsc-sec-count">{{ icons.length }} {{ icons.length === 1 ? 'icono' : 'iconos' }}</span>
                </div>
                <p class="nsc-sec-desc">Sube imágenes para usar como iconos en los equipos. PNG · SVG · JPG · GIF — máx. 256 KB por archivo. El nombre del archivo se usa como nombre del icono.</p>

                <div class="nsc-drop-zone"
                     :class="{ dragging }"
                     @click="$refs.fileInput.click()"
                     @dragover.prevent="dragging = true"
                     @dragleave.prevent="dragging = false"
                     @drop.prevent="onDrop">
                    <input ref="fileInput" type="file" multiple accept="image/*" hidden @change="onFileChange" />
                    <div class="nsc-drop-inner">
                        <span class="nsc-drop-ico">⬆</span>
                        <span class="nsc-drop-text">Arrastra imágenes aquí o haz clic para seleccionar</span>
                    </div>
                </div>

                <div v-if="icons.length" class="nsc-icon-grid">
                    <div v-for="ic in icons" :key="ic.id" class="nsc-icon-card">
                        <img :src="ic.data" :alt="ic.name" class="nsc-icon-img" />
                        <span class="nsc-icon-name" :title="ic.name">{{ ic.name }}</span>
                        <button class="nsc-icon-del" title="Eliminar" @click="deleteIcon(ic.id)">✕</button>
                    </div>
                </div>
                <p v-else class="nsc-empty">Sin iconos. Sube imágenes arriba para usarlas en los equipos.</p>
            </div>

            <!-- ── Biblioteca integrada ── -->
            <div class="nsc-section">
                <div class="nsc-sec-hdr">
                    <span class="nsc-sec-title">Biblioteca de Iconos Integrados</span>
                    <span class="nsc-sec-count">{{ deviceIcons.length + vendorIcons.length }} iconos</span>
                </div>
                <p class="nsc-sec-desc">Iconos predefinidos disponibles para asignar a equipos. Selecciónalos directamente en el modal de equipo desde el Dashboard.</p>

                <div class="nsc-lib-group">
                    <span class="nsc-lib-title">Tipos de Dispositivo ({{ deviceIcons.length }})</span>
                    <div class="nsc-icon-grid">
                        <div v-for="ic in deviceIcons" :key="ic.file" class="nsc-icon-card nsc-icon-card--ro">
                            <img :src="'/nagsa/icons/devices/' + ic.file" :alt="ic.label" class="nsc-icon-img" />
                            <span class="nsc-icon-name">{{ ic.label }}</span>
                        </div>
                    </div>
                </div>

                <div class="nsc-lib-group" style="margin-top:18px">
                    <span class="nsc-lib-title">Fabricantes ({{ vendorIcons.length }})</span>
                    <div class="nsc-icon-grid">
                        <div v-for="ic in vendorIcons" :key="ic.file" class="nsc-icon-card nsc-icon-card--ro">
                            <img :src="'/nagsa/icons/vendors/' + ic.file" :alt="ic.label" class="nsc-icon-img" />
                            <span class="nsc-icon-name">{{ ic.label }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ── Marcas ── -->
            <div class="nsc-section">
                <div class="nsc-sec-hdr">
                    <span class="nsc-sec-title">Marcas / Fabricantes</span>
                    <span class="nsc-sec-count">{{ brands.length }} {{ brands.length === 1 ? 'marca' : 'marcas' }}</span>
                </div>
                <p class="nsc-sec-desc">Registro de marcas para autocompletar al crear equipos. Se añaden automáticamente al guardar un equipo con marca, o manualmente aquí.</p>

                <div class="nsc-brand-row">
                    <input v-model="newBrand" class="nsc-brand-input" placeholder="Añadir marca manualmente…" maxlength="60" @keyup.enter="addBrand" />
                    <button class="nsc-brand-addbtn" @click="addBrand">+ Añadir</button>
                </div>

                <div v-if="brands.length" class="nsc-brand-tags">
                    <span v-for="b in brands" :key="b" class="nsc-brand-tag">
                        {{ b }}
                        <button class="nsc-tag-del" title="Eliminar" @click="deleteBrand(b)">✕</button>
                    </span>
                </div>
                <p v-else class="nsc-empty">Sin marcas. Se añaden al guardar equipos o manualmente arriba.</p>
            </div>

        </div>
    </div>
</template>

<script>
import { DEVICE_ICONS, VENDOR_ICONS } from "../nagsa-icon-library.js";

const MAX_BYTES = 256 * 1024;

export default {
    name: "NagsaSettings",
    data() {
        return {
            icons:    [],
            brands:   [],
            dragging: false,
            newBrand: "",
            loading:    true,
            deviceIcons: DEVICE_ICONS,
            vendorIcons: VENDOR_ICONS,
        };
    },
    mounted() {
        this.$root.getSocket().emit("nagsa:settings:get", (res) => {
            this.icons   = res.icons  || [];
            this.brands  = res.brands || [];
            this.loading = false;
        });
    },
    methods: {
        socket() { return this.$root.getSocket(); },

        // ── Icons ──────────────────────────────────────────────
        onFileChange(e) { this.processFiles(e.target.files); e.target.value = ""; },
        onDrop(e)       { this.dragging = false; this.processFiles(e.dataTransfer.files); },
        processFiles(files) {
            [...files].forEach(file => {
                if (file.size > MAX_BYTES) { alert(`"${file.name}" supera 256 KB — omitido.`); return; }
                const name = file.name.replace(/\.[^.]+$/, "");
                const reader = new FileReader();
                reader.onload = (ev) => {
                    const id = "ico-" + Date.now() + "-" + Math.random().toString(36).slice(2, 7);
                    this.icons.push({ id, name, data: ev.target.result });
                    this.saveIcons();
                };
                reader.readAsDataURL(file);
            });
        },
        deleteIcon(id) {
            this.icons = this.icons.filter(i => i.id !== id);
            this.saveIcons();
        },
        saveIcons() {
            this.socket().emit("nagsa:settings:save", { icons: this.icons }, (res) => {
                if (!res.ok) alert("Error al guardar iconos: " + res.msg);
            });
        },

        // ── Brands ─────────────────────────────────────────────
        addBrand() {
            const b = this.newBrand.trim();
            if (!b || this.brands.includes(b)) { this.newBrand = ""; return; }
            this.brands.push(b);
            this.brands.sort((a, c) => a.localeCompare(c));
            this.saveBrands();
            this.newBrand = "";
        },
        deleteBrand(b) {
            this.brands = this.brands.filter(x => x !== b);
            this.saveBrands();
        },
        saveBrands() {
            this.socket().emit("nagsa:settings:save", { brands: this.brands }, (res) => {
                if (!res.ok) alert("Error al guardar marcas: " + res.msg);
            });
        },
    },
};
</script>

<style>
.nsc-wrap  { min-height:100vh; background:#eef0f5; font-family:"Segoe UI",Arial,sans-serif; font-size:13px; }
.nsc-topbar{ display:flex; align-items:center; gap:16px; padding:12px 24px; background:#1e2130; }
.nsc-back  { color:#88a4d8; text-decoration:none; font-size:12px; }
.nsc-back:hover { color:#b0c4f0; }
.nsc-title { color:#fff; font-weight:700; font-size:15px; }
.nsc-body  { max-width:900px; margin:0 auto; padding:28px 20px; display:flex; flex-direction:column; gap:20px; }
.nsc-section{ background:#fff; border-radius:8px; padding:20px 24px; box-shadow:0 1px 4px rgba(0,0,0,.07); }
.nsc-sec-hdr{ display:flex; align-items:baseline; gap:10px; margin-bottom:6px; }
.nsc-sec-title{ font-size:15px; font-weight:700; color:#1a1e2e; }
.nsc-sec-count{ font-size:11px; color:#778; background:#eef0f5; border-radius:10px; padding:2px 8px; }
.nsc-sec-desc { font-size:12px; color:#667; margin:0 0 16px; line-height:1.5; }
.nsc-empty { font-size:12px; color:#aaa; font-style:italic; margin:10px 0 0; }

/* Drop zone */
.nsc-drop-zone { border:2px dashed #c0cce0; border-radius:8px; padding:28px 20px; cursor:pointer; transition:border-color .15s,background .15s; margin-bottom:16px; }
.nsc-drop-zone:hover,.nsc-drop-zone.dragging { border-color:#4a7ad8; background:#f0f5ff; }
.nsc-drop-inner{ display:flex; flex-direction:column; align-items:center; gap:6px; pointer-events:none; }
.nsc-drop-ico  { font-size:28px; color:#6080c0; }
.nsc-drop-text { font-size:13px; font-weight:600; color:#3a4a6a; text-align:center; }

/* Icon grid */
.nsc-icon-grid { display:flex; flex-wrap:wrap; gap:10px; }
.nsc-icon-card { position:relative; display:flex; flex-direction:column; align-items:center; gap:5px; background:#f5f7fc; border:1px solid #dde3ef; border-radius:6px; padding:12px 10px 8px; width:88px; }
.nsc-icon-img  { width:44px; height:44px; object-fit:contain; }
.nsc-icon-name { font-size:10px; color:#445; text-align:center; word-break:break-word; max-width:72px; line-height:1.3; }
.nsc-icon-del  { position:absolute; top:4px; right:4px; background:none; border:none; color:#b03030; font-size:11px; cursor:pointer; opacity:0; transition:opacity .15s; line-height:1; padding:1px 3px; }
.nsc-icon-card:hover .nsc-icon-del { opacity:1; }

/* Brands */
.nsc-brand-row    { display:flex; gap:8px; margin-bottom:12px; }
.nsc-brand-input  { flex:1; padding:6px 10px; border:1px solid #c8cfe0; border-radius:5px; font-size:13px; outline:none; }
.nsc-brand-input:focus { border-color:#5a8fd0; box-shadow:0 0 0 2px rgba(90,143,208,.18); }
.nsc-brand-addbtn { background:#4a7ad8; color:#fff; border:none; border-radius:5px; padding:6px 14px; font-size:12px; font-weight:600; cursor:pointer; }
.nsc-brand-addbtn:hover { background:#3a6ab8; }
.nsc-brand-tags   { display:flex; flex-wrap:wrap; gap:6px; }
.nsc-brand-tag    { display:inline-flex; align-items:center; gap:5px; background:#e8ecf8; border:1px solid #c0cce0; border-radius:12px; padding:3px 8px 3px 10px; font-size:12px; color:#334; }
.nsc-tag-del      { background:none; border:none; cursor:pointer; color:#b03030; font-size:11px; line-height:1; padding:0; opacity:.6; }
.nsc-tag-del:hover{ opacity:1; }
/* Built-in library */
.nsc-lib-group { }
.nsc-lib-title { display:block; font-size:12px; font-weight:700; color:#556; text-transform:uppercase; letter-spacing:.04em; margin-bottom:10px; }
.nsc-icon-card--ro { cursor:default; }
.nsc-icon-card--ro:hover .nsc-icon-del { display:none; }
</style>
