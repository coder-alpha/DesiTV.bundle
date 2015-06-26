# DesiTV Plex Plugin Version 1.2
import common
import desirulez
import apnitv
import desitvforum
import updater

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON
ICON_PREFS = "icon-prefs.png"
ICON_UPDATE = "icon-update.png"

####################################################################################################
def Start():
  ObjectContainer.title1 = NAME
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  EpisodeObject.thumb = R(ICON)
  EpisodeObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

####################################################################################################

@handler(PREFIX, NAME, art=ART, thumb=ICON)
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(desirulez.TypeMenu, url=desirulez.SITEURL), title=desirulez.SITETITLE, thumb=R(desirulez.SITETHUMB)))
  oc.add(DirectoryObject(key=Callback(apnitv.ChannelsMenu, url=apnitv.SITEURL), title=apnitv.SITETITLE, thumb=R(apnitv.SITETHUMB)))
  oc.add(DirectoryObject(key=Callback(desitvforum.TypeMenu, url=desitvforum.SITEURL), title=desitvforum.SITETITLE, thumb=R(desitvforum.SITETHUMB)))
  oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update Plugin', thumb = R(ICON_UPDATE)))
  oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
  return oc

####################################################################################################