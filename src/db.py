from enum import Enum
import MySQLdb

from admin.auth import auth_handler
from db_exceptions import *
from models import AuthDetails, Config, Configs, IPAddresses, MetaConfig
from conn_pool import conn_pool

class ListType(Enum):
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"


class DB:
    conn: MySQLdb.Connection

    def __init__(self):
        self.conn = conn_pool.pop()

    def __del__(self):
        self.conn.rollback()
        conn_pool.push(self.conn)

    def user_id_exists(self, user_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE id = %s LIMIT 1;", (user_id,))
        
        return cursor.fetchone() is not None

    def username_exists(self, username: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE name = %s LIMIT 1;", (username,))
        
        return cursor.fetchone() is not None

    def register_user(self, auth_details: AuthDetails):
        if self.username_exists(auth_details.username):
            raise UsernameTakenException(auth_details.username)
 
        hashed_password = auth_handler.get_password_hash(auth_details.password)

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (auth_details.username, hashed_password))
        self.conn.commit()

    def delete_user(self, user_id: int):
        # User ID is decoded from JWT, should exists in database
        assert self.user_id_exists(user_id)

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        self.conn.commit()

    def config_assertion(self, user_id: int, config_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM configs WHERE id = %s AND user_id = %s LIMIT 1;", (config_id, user_id))

        if not cursor.fetchone():
            raise ConfigNotFoundException(config_id)

    def new_config(self, user_id: int, config: Config) -> int:
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO configs (
                name,
                user_id,
                proxy_host,
                proxy_port,
                real_host,
                real_port,
                max_bytes_per_request,
                max_bytes_per_response,
                max_requests_per_second
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            config.name,
            user_id,
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

    def get_configs(self, user_id: int) -> Configs | None:
        cursor = self.conn.cursor()

        cursor.execute("SELECT id, name FROM configs WHERE user_id = %s;", (user_id,))
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

    def get_config(self, user_id: int, config_id: int) -> Config:
        self.config_assertion(user_id, config_id)
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
        WHERE id = %s AND user_id = %s;
        """, (config_id, user_id))

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

    def delete_config(self, user_id: int, config_id: int):
        self.config_assertion(user_id, config_id)
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM configs WHERE id = %s;", (config_id,))
        self.conn.commit()


    def update_config(self, user_id: int, config_id: int, config: Config):
        self.config_assertion(user_id, config_id)
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

    def get_list(self, list_type: ListType, config_id: int) -> IPAddresses:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT ip_address FROM access_control WHERE list_type = '{list_type.value}' AND config_id = %s;",
                       (config_id,))

        results = cursor.fetchall()
        return IPAddresses(ips=[row[0] for row in results])

    def is_in_list(self, list_type: ListType, config_id: int, ip: str):
        cursor = self.conn.cursor()

        ip = ip.strip()

        cursor.execute(f"""
            SELECT 1 FROM access_control 
            WHERE list_type = '{list_type.value}' 
                AND config_id = %s 
                AND ip_address = %s 
            LIMIT 1;
        """, (config_id, ip))

        return cursor.fetchone() is not None
    

    def remove_from_list(self, list_type: ListType, config_id: int, ip: str):
        cursor = self.conn.cursor()

        ip = ip.strip()
        
        cursor.execute(f"""
            DELETE FROM access_control
            WHERE config_id = %s 
                AND ip_address = %s 
                AND list_type = '{list_type.value}';
        """, (config_id, ip))

        self.conn.commit()


    def add_to_list(self, list_type: ListType, config_id: int, ip: str):
        cursor = self.conn.cursor()

        ip = ip.strip()

        if list_type == ListType.WHITELIST:
            self.remove_from_list(list_type.BLACKLIST, config_id, ip)
        elif list_type == ListType.BLACKLIST:
            self.remove_from_list(list_type.WHITELIST, config_id, ip)

        cursor.execute(f"""
            INSERT INTO access_control (
                ip_address,
                list_type,
                config_id
            ) VALUES (%s, '{list_type.value}', %s);
        """, (
            ip, config_id
        ))

        self.conn.commit()