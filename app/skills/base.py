class BaseSkill:
    name = ''
    version = '1.0.0'

    def validate(self, payload: dict) -> bool:
        raise NotImplementedError

    def execute(self, payload: dict) -> dict:
        raise NotImplementedError
