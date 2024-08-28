from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(
        env,
        [
            ('res.company', 'store_keeper', 'char'),
            ('res.company', 'chief_accountant', 'char'),
            ('res.company', 'president', 'char'),
        ],
    )