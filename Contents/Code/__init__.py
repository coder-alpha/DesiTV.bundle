# DesiTV Plex Plugin Version 1.2
import common
import desirulez
import apnitv
import desitvforum

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

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
  return oc

####################################################################################################