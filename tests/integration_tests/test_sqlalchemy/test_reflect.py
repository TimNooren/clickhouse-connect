# pylint: disable=no-member
import sqlalchemy as db
from sqlalchemy.engine import Engine

from clickhouse_connect import common
from clickhouse_connect.cc_sqlalchemy.datatypes.sqltypes import UInt32


def test_basic_reflection(test_engine: Engine):
    common.set_setting('invalid_setting_action', 'drop')
    conn = test_engine.connect()
    metadata = db.MetaData(bind=test_engine, schema='system')
    table = db.Table('tables', metadata, autoload_with=test_engine)
    query = db.select([table.columns.create_table_query])
    result = conn.execute(query)
    rows = result.fetchmany(100)
    assert rows


def test_full_table_reflection(test_engine: Engine, test_db: str, test_table_engine: str):
    common.set_setting('invalid_setting_action', 'drop')
    conn = test_engine.connect()
    conn.execute(
        'CREATE TABLE IF NOT EXISTS reflect_test (key UInt32, value FixedString(20))' +
        f'ENGINE {test_table_engine} ORDER BY key')
    metadata = db.MetaData(bind=test_engine, schema=test_db)
    table = db.Table('reflect_test', metadata, autoload_with=test_engine)
    assert table.columns.key.type.__class__ == UInt32
    assert 'MergeTree' in table.engine.name


def test_table_exists(test_engine: Engine):
    common.set_setting('invalid_setting_action', 'drop')
    conn = test_engine.connect()
    assert test_engine.dialect.has_table(conn, 'columns', 'system')
    assert not test_engine.dialect.has_table(conn, 'nope', 'fake_db')
