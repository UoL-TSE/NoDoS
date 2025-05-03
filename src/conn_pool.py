import MySQLdb

MAX_HELD_CONNECTIONS = 10
DB_ARGS = {
    "host": "127.0.0.1",
    "user": "root",
    "passwd": "nodos-pass",
    "db": "nodos"
}

class _ConnPool:
    _conn_pool: list[MySQLdb.Connection] = []

    def pop(self) -> MySQLdb.Connection:
        try:
            return self._conn_pool.pop()
        except:
            return MySQLdb.connect(**DB_ARGS)

    def push(self, conn: MySQLdb.Connection):
        if len(self._conn_pool) >= MAX_HELD_CONNECTIONS:
            conn.close()
            return

        self._conn_pool.append(conn)


conn_pool = _ConnPool()
