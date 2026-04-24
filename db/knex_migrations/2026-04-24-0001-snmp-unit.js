exports.up = function (knex) {
    return knex.schema.alterTable("monitor", function (table) {
        table.string("snmp_unit").nullable().defaultTo(null);
    });
};

exports.down = function (knex) {
    return knex.schema.alterTable("monitor", function (table) {
        table.dropColumn("snmp_unit");
    });
};
