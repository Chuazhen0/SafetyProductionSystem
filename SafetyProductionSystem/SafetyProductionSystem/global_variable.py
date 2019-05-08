# from systemsettings.views import menu_data

def setting(request):
    content = {"menu_list": gol.get_value('menudata')}
    return content
