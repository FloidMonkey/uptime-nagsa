const { MonitorType } = require("./monitor-type");
const { UP } = require("../../src/util");
const snmp = require("net-snmp");

// Requires NODE_OPTIONS=--openssl-legacy-provider when using DES privacy
// (OpenSSL 3.x disables DES by default; set in docker-compose environment).

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
        // Counter64 arrives as a variable-length big-endian Buffer
        let result = BigInt(0);
        for (const byte of val) {
            result = (result << BigInt(8)) | BigInt(byte);
        }
        return result.toString();
    }
    return val.toString();
}

class SNMPMonitorType extends MonitorType {
    name = "snmp";

    /**
     * @inheritdoc
     */
    async check(monitor, heartbeat, _server) {
        let session;
        try {
            // Support both camelCase (redbean getter) and snake_case (raw bean property)
            const v3user = monitor.snmpV3Username || monitor.snmp_v3_username;
            const authPass = monitor.snmpAuthPass || monitor.snmp_auth_pass;
            const privPass = monitor.snmpPrivPass || monitor.snmp_priv_pass;
            const authProto = monitor.snmpAuthProtocol || monitor.snmp_auth_protocol || "MD5";
            const privProto = monitor.snmpPrivProtocol || monitor.snmp_priv_protocol || "DES";

            const sessionOptions = {
                port: monitor.port || "161",
                retries: monitor.maxretries,
                // Guard against timeout=0 which hangs the session indefinitely
                timeout: Math.max((monitor.timeout || 0), 30) * 1000,
                version: snmp.Version3,
            };

            if (monitor.snmpVersion === "3") {
                if (!v3user) {
                    throw new Error("SNMPv3 username is required");
                }

                let level = snmp.SecurityLevel.noAuthNoPriv;
                if (authPass && privPass) {
                    level = snmp.SecurityLevel.authPriv;
                } else if (authPass) {
                    level = snmp.SecurityLevel.authNoPriv;
                }

                // net-snmp v3.x requires a user object, not a plain username string
                const userObj = { name: v3user, level };
                if (authPass) {
                    userObj.authProtocol = authProtocolMap[authProto] || snmp.AuthProtocols.md5;
                    userObj.authKey = authPass;
                }
                if (authPass && privPass) {
                    userObj.privProtocol = privProtocolMap[privProto] || snmp.PrivProtocols.des;
                    userObj.privKey = privPass;
                }

                session = snmp.createV3Session(monitor.hostname, userObj, sessionOptions);
            } else {
                session = snmp.createSession(monitor.hostname, monitor.radiusPassword || "public", sessionOptions);
            }

            session.on("error", (error) => {
                throw new Error(`Error creating SNMP session: ${error.message}`);
            });

            // net-snmp rejects OIDs that start with a leading dot
            const rawOid = monitor.snmpOid || monitor.snmp_oid || "";
            const oid = rawOid.replace(/^\./, "");

            const varbinds = await new Promise((resolve, reject) => {
                session.get([oid], (error, varbinds) => {
                    error ? reject(error) : resolve(varbinds);
                });
            });

            if (varbinds.length === 0) {
                throw new Error(`No varbinds returned from SNMP session (OID: ${oid})`);
            }

            if (varbinds[0].type === snmp.ObjectType.NoSuchInstance) {
                throw new Error(`The SNMP query returned that no instance exists for OID ${oid}`);
            }

            const value = formatValue(varbinds[0]);
            heartbeat.status = UP;
            heartbeat.msg = `SNMP OK: ${value}`;
        } finally {
            if (session) {
                session.close();
            }
        }
    }
}

module.exports = {
    SNMPMonitorType,
};
