from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO
from app import db

import os.path

db.create_all()

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    # 如果数据仓库不存在,就创建一个,参数是资源位置和资源名字
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    """
    version_control(url, repository, version=None, **opts)
    Mark a database as under this repository's version control.
    Once a database is under version control,
    schema changes should only be done via change scripts in this repository.
    This creates the table version_table in the database.
    By default, the database begins at version 0 and is assumed to be empty.
    If the database is not empty, you may specify a version at which to begin instead.
    No attempt is made to verify this version's correctness - the database schema
    is expected to be identical to what it would be if the database were created from scratch.
    """
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
