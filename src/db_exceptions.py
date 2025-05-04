class ConfigNotFoundException(Exception):
    def __init__(self, config_id: int):
        super().__init__(f"Config with ID {config_id} not found")
