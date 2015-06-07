import common

PREFIX = common.PREFIX

####################################################################################################

@route(PREFIX + '/testmenu')
def TestMenu(url, title):
  return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")

####################################################################################################