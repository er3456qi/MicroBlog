from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO

"""
升级数据库。
假设你有一个应用程序在开发机器上，同时有一个拷贝部署在到线上的生产机器上。
在下一个版本中，你的数据模型有一个变化，比如新增了一个表。
如果没有迁移脚本，你可能必须要琢磨着如何修改数据库格式在开发和生产机器上，这会花费很大的工作。
如果有数据库迁移的支持，当你准备发布新版的时候，你只需要录制一个新的迁移，
拷贝迁移脚本到生产服务器上接着运行脚本，所有事情就完成了。
"""
api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print('Current database version:',
      str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))