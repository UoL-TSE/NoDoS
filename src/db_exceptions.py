class ConfigNotFoundException(Exception):
    def __init__(self, config_id: int):
        super().__init__(f"Config with ID {config_id} not found")


class UsernameTakenException(Exception):
    def __init__(self, username: str):
        super().__init__(f"Username {username} is taken")


class BlacklistingWhitelistedException(Exception):
    def __init__(self, ip: str):
        super().__init__(f"IP address {ip} is whitelisted so cannot be blacklisted")


class IPNotFoundException(Exception):
    def __init__(self, ip: str):
        super().__init__(f"IP address {ip} was not found")
