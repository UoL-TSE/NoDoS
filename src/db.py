import MySQLdb

from db_exceptions import *
from models import Config, Configs, MetaConfig
from conn_pool import conn_pool

class DB:
    conn: MySQLdb.Connection

    def __init__(self):
        self.conn = conn_pool.pop()

    def __del__(self):
        self.conn.rollback()
        conn_pool.push(self.conn)

    def config_assertion(self, config_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM configs WHERE id = %s LIMIT 1;", (config_id,))

        if not cursor.fetchone():
            raise ConfigNotFoundException(config_id)

    def new_config(self, config: Config) -> int:
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO configs (
                name,
                proxy_host,
                proxy_port,
                real_host,
                real_port,
                max_bytes_per_request,
                max_bytes_per_response,
                max_requests_per_second
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            config.name,
            config.proxy_host,
            config.proxy_port,
            config.real_host,
            config.real_port,
            config.max_bytes_per_request,
            config.max_bytes_per_response,
            config.max_requests_per_second
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_configs(self) -> Configs | None:
        cursor = self.conn.cursor()

        cursor.execute("SELECT id, name FROM configs;")
        results = cursor.fetchall()

        if len(results) == 0:
            return None

        return Configs(
            configs=[
                MetaConfig(
                    config_id=row[0],
                    config_name=row[1]
                )
                for row in results
            ]
        )

    def get_config(self, config_id: int) -> Config:
        self.config_assertion(config_id)
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            name,
            proxy_host,
            proxy_port,
            real_host,
            real_port,
            max_bytes_per_request,
            max_bytes_per_response,
            max_requests_per_second
        FROM configs
        WHERE id = %s;
        """, (config_id,))

        row = cursor.fetchone()
        assert isinstance(row, tuple)

        return Config(
            name=row[0],
            proxy_host=row[1],
            proxy_port=row[2],
            real_host=row[3],
            real_port=row[4],
            max_bytes_per_request=row[5],
            max_bytes_per_response=row[6],
            max_requests_per_second=row[7]
        )

    def delete_config(self, config_id: int):
        self.config_assertion(config_id)
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM configs WHERE id = %s;", (config_id,))


    def update_config(self, config_id: int, config: Config):
        self.config_assertion(config_id)
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE configs SET
                name = %s,
                proxy_host = %s,
                proxy_port = %s,
                real_host = %s,
                real_port = %s,
                max_bytes_per_request = %s,
                max_bytes_per_response = %s,
                max_requests_per_second = %s
            WHERE id = %s;
        """, (
            config.name,
            config.proxy_host,
            config.proxy_port,
            config.real_host,
            config.real_port,
            config.max_bytes_per_request,
            config.max_bytes_per_response,
            config.max_requests_per_second,
            config_id
        ))

        self.conn.commit()
