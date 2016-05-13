import types  # import imp is deprecated, use this instead
from migrate.versioning import api
from app import db
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO

"""
SQLAlchemy-migrate 迁移的方式就是比较数据库(在本例中从 app.db 中获取)与我们模型的结构(从文件 app/models.py 获取)。
两者间的不同将会被记录成一个迁移脚本存放在迁移仓库中。
迁移脚本知道如何去迁移或撤销它，所以它始终是可能用于升级或降级一个数据库。
"""
migration = SQLALCHEMY_MIGRATE_REPO +\
            '/versions/%03d_migration.py' % (api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO) + 1)
tmp_module = types.ModuleType('old_model')  # instead tmp_module = imp.new_module('old_model')
old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
exec(old_model, tmp_module.__dict__)
script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI,
                                          SQLALCHEMY_MIGRATE_REPO,
                                          tmp_module.meta, db.metadata)
with open(migration, 'wt') as f:
    f.write(script)

api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print ('New migration saved as ' + migration)
print ('Current database version:' ,
       str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))
