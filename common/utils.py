
#from entities.models import MetaData
from common import constanst

class Utils(object):
    """description of class"""
    def get_change(prev, curr):
        if(prev != 0):
            return round(abs((curr - prev)/prev*100),2)
        else:
            return "N/A"
   
    def convert_to_string(value):
        #//if (value):
            return "{}".format(value)
        #else:
        #    return value

    def get_structure(sub, total):
        if(total != 0):
            return "{}".format(round(abs(sub/total*100),2))
        else:
            return "N/A"

    def get_item(dic, index):
        if dic:
            if index >= 0:
                return dict(list(dict)[index])
            else:
                return dict(list(dict)[0])      
        else:
            return "N/A"

    