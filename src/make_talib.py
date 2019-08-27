from talib._ta_lib import  __TA_FUNCTION_NAMES__

def write_function(name):
    statement_function = """
    def %s(self, name, **parameters):
        data = self.__data[name]
        return talib.%s(data, **parameters)
    """ % (name, name)
    return statement_function

if __name__== "__main__":

    code_string = """
# encoding: utf-8

import talib
    
class Tec():

    def __init__(self, data):
        self.__data = data
        return
    """

    for func_name in __TA_FUNCTION_NAMES__:
        statement = write_function(func_name)
        code_string = code_string + statement
    with open("talib_class.py", "w") as f:
        f.write(code_string)




