
from entities.models import MasterData
from . import constanst

#class Common_BO(object):
#    """description of class"""

def get_configuration():
    #web_title_config = ''
    web_title_config = MasterData.objects.get(type=constanst.CONFIGURATION, key = constanst.WEB_TITLE, is_deleted=False)
    if(web_title_config):
        web_title = web_title_config.value
    else:
        web_title = "Test"

    #top_menu = MetaData.objects.filter(type=constanst.TOP_MENU, is_deleted=False)

    return {'web_title': web_title}
