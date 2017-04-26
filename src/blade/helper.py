
BUILD_VARS = {}

def add_BUILD_var(name, **kwargs):
  class VarData(object):
    def __init__(self, var_name, data):
        self.name = var_name
        self.var_data = {}
        self.var_data.update(data)
    def __getattr__(self, key):
        if key in self.var_data:
            return self.var_data[key]
        raise AttributeError
  BUILD_VARS[name] = VarData(name, kwargs)

def GET_BUILD_VAR(name):
    return BUILD_VARS[name]


