class Container:
    def __init__(self):
        self.params = self.param_template()

    @staticmethod
    def param_template():
        raise NotImplementedError

    @staticmethod
    def _validate_int(num):
        try:
            int(num)
        except ValueError:
            return False
        return True

    @staticmethod
    def _validate_all(val):
        return True

    # if no validator, everything works
    def get_validator(self, key):
        return getattr(self, '_validate_' + key, self._validate_all)

    def set_param(self, key, value):
        result = self.get_validator(key)(value)
        if result:
            self.params[key] = value

        return result
