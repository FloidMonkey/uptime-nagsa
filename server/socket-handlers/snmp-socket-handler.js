const { checkLogin } = require("../util-server");
const { log } = require("../../src/util");
const path = require("path");
const fs = require("fs");
const snmp = require("net-snmp");
const { R } = require("redbean-node");

const authProtocolMap = {
    "MD5":    snmp.AuthProtocols.md5,
    "SHA":    snmp.AuthProtocols.sha,
    "SHA256": snmp.AuthProtocols.sha256,
};
const privProtocolMap = {
    "DES": snmp.PrivProtocols.des,
    "AES": snmp.PrivProtocols.aes,
};

function formatValue(varbind) {
    const val = varbind.value;
    if (Buffer.isBuffer(val)) {
        let result = BigInt(0);
        for (const byte of val) {
            result = (result << BigInt(8)) | BigInt(byte);
        }
        return result.toString();
    }
    return val.toString();
}

function buildSession(params) {
    const { hostname, port, snmpVersion, snmpCommunity, snmpV3Username, snmpAuthProtocol, snmpAuthPass, snmpPrivProtocol, snmpPrivPass } = params;

    const sessionOptions = {
        port: port || 161,
        retries: 1,
        timeout: 10000,
        version: snmp.Version3,
    };

    if (snmpVersion === "3") {
        if (!snmpV3Username) throw new Error("SNMPv3 username is required");

        let level = snmp.SecurityLevel.noAuthNoPriv;
        if (snmpAuthPass && snmpPrivPass) level = snmp.SecurityLevel.authPriv;
        else if (snmpAuthPass) level = snmp.SecurityLevel.authNoPriv;

        const userObj = { name: snmpV3Username, level };
        if (snmpAuthPass) {
            userObj.authProtocol = authProtocolMap[snmpAuthProtocol] || snmp.AuthProtocols.md5;
            userObj.authKey = snmpAuthPass;
        }
        if (snmpAuthPass && snmpPrivPass) {
            userObj.privProtocol = privProtocolMap[snmpPrivProtocol] || snmp.PrivProtocols.des;
            userObj.privKey = snmpPrivPass;
        }

        return snmp.createV3Session(hostname, userObj, sessionOptions);
    }

    sessionOptions.version = snmpVersion === "1" ? snmp.Version1 : snmp.Version2c;
    return snmp.createSession(hostname, snmpCommunity || "public", sessionOptions);
}

function templatesDir() {
    return path.join(__dirname, "..", "snmp-templates");
}

module.exports.snmpSocketHandler = (socket, server) => {

    socket.on("snmpWalk", (params, callback) => {
        try {
            checkLogin(socket);
        } catch (e) {
            callback({ ok: false, msg: e.message });
            return;
        }

        let session;
        try {
            session = buildSession(params);
        } catch (e) {
            callback({ ok: false, msg: e.message });
            return;
        }

        const results = [];
        const MAX_OIDS = 500;
        const rootOid = (params.startOid || "1.3.6.1").replace(/^\./, "");

        session.subtree(
            rootOid,
            20,
            (varbinds) => {
                for (const varbind of varbinds) {
                    if (results.length >= MAX_OIDS) break;
                    if (snmp.isVarbindError(varbind)) continue;
                    results.push({
                        oid:      varbind.oid,
                        typeName: snmp.ObjectType[varbind.type] || String(varbind.type),
                        value:    formatValue(varbind),
                    });
                }
            },
            (error) => {
                session.close();
                if (error) {
                    callback({ ok: false, msg: error.message });
                } else {
                    callback({ ok: true, oids: results });
                }
            }
        );
    });

    socket.on("getSnmpTemplates", (callback) => {
        try {
            checkLogin(socket);
            const dir = templatesDir();
            const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
            const templates = files.map((file) => JSON.parse(fs.readFileSync(path.join(dir, file), "utf8")));
            callback({ ok: true, templates });
        } catch (e) {
            callback({ ok: false, msg: e.message });
        }
    });

    socket.on("applySnmpTemplate", async (params, callback) => {
        try {
            checkLogin(socket);
        } catch (e) {
            callback({ ok: false, msg: e.message });
            return;
        }

        try {
            const { templateId, deviceName, hostname, groupId, interval = 60, snmpV3Username, snmpAuthProtocol, snmpAuthPass, snmpPrivProtocol, snmpPrivPass } = params;

            const templatePath = path.join(templatesDir(), `${templateId}.json`);
            if (!fs.existsSync(templatePath)) throw new Error(`Template not found: ${templateId}`);
            const template = JSON.parse(fs.readFileSync(templatePath, "utf8"));

            let created = 0;

            for (const monitorDef of template.monitors) {
                const monitorName = monitorDef.name.replace(/\{device\}/g, deviceName || hostname);

                const bean = R.dispense("monitor");
                bean.user_id    = socket.userID;
                bean.name       = monitorName;
                bean.hostname   = hostname;
                bean.interval   = interval;
                bean.maxretries = 3;
                bean.parent     = groupId || null;
                bean.active     = true;
                bean.accepted_statuscodes_json = JSON.stringify([ "200-299" ]);
                bean.conditions = JSON.stringify([]);
                bean.kafka_producer_brokers = JSON.stringify([]);
                bean.kafka_producer_sasl_options = JSON.stringify({});
                bean.rabbitmq_nodes = JSON.stringify([]);

                if (monitorDef.type === "ping") {
                    bean.type = "ping";
                } else {
                    bean.type = "snmp";
                    bean.snmp_oid            = (monitorDef.oid || "").replace(/^\./, "");
                    bean.snmp_version        = template.snmpVersion || "2c";
                    bean.snmp_v3_username    = snmpV3Username   || null;
                    bean.snmp_auth_protocol  = snmpAuthProtocol || "MD5";
                    bean.snmp_auth_pass      = snmpAuthPass     || null;
                    bean.snmp_priv_protocol  = snmpPrivProtocol || "DES";
                    bean.snmp_priv_pass      = snmpPrivPass     || null;
                    bean.snmp_condition      = monitorDef.condition || ">=";
                    bean.snmp_control_value  = monitorDef.value    || "0";
                    bean.snmp_unit           = monitorDef.unit      || null;
                    bean.port               = 161;
                }

                await R.store(bean);
                created++;

                await server.sendUpdateMonitorIntoList(socket, bean.id);

                if (bean.active) {
                    const { startMonitor } = require("../server");
                    try { await startMonitor(socket.userID, bean.id); } catch (_) {}
                }
            }

            callback({ ok: true, created });
        } catch (e) {
            log.error("snmpSocketHandler", e.message);
            callback({ ok: false, msg: e.message });
        }
    });
};
