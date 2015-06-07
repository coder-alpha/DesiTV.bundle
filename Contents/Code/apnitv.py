
import common
import urlparse
import re
import time

SITETITLE = L('ApniTvTitle')
SITEURL = 'http://apni.tv/'
SITETHUMB = 'icon-apnitv.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/apnitv/channels')
def ChannelsMenu(url):
  oc = ObjectContainer(title2=SITETITLE)

  html = HTML.ElementFromURL(url)

  for item in html.xpath("//div[@id='navi']/a"):
    try:
      # Channel title
      channel = item.xpath("./text()")[0]
      channel = channel.replace(" Serials","",1)
      
      # Channel link
      link = item.xpath("./@href")[0]
      if link.startswith("http") == False:
        link = SITEURL + link
    except:
      continue

    try:
      image = common.GetThumb(channel.lower())
    except:
      continue

    if channel.lower() in common.GetSupportedChannels():
      oc.add(DirectoryObject(key=Callback(ShowsMenu, url=link, title=channel), title=channel, thumb=image))
    
  # If there are no channels, warn the user
  if len(oc) == 0:
    return ObjectContainer(header=SITETITLE, message=L('ChannelWarning'))

  return oc

####################################################################################################

@route(PREFIX + '/apnitv/showsmenu')
def ShowsMenu(url, title):
  oc = ObjectContainer(title2=title)

  html = HTML.ElementFromURL(url)
  
  for item in html.xpath("//div[@id='centerblocks']/div[@class='serial']/strong/a"):
    try:
      # Show title
      show = item.xpath("./text()")[0]
      
      # Show link
      link = item.xpath("./@href")[0]
      if link.startswith("http") == False:
        link = SITEURL + link
    except:
      continue

    # Add the found item to the collection
    oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=link, title=show), title=show))
    
  # If there are no channels, warn the user
  if len(oc) == 0:
    return ObjectContainer(header=title, message=L('ShowWarning'))

  return oc

####################################################################################################

@route(PREFIX + '/apnitv/episodesmenu')
def EpisodesMenu(url, title):
  oc = ObjectContainer(title2=title)

  html = HTML.ElementFromURL(url)

  for item in html.xpath("//div[@id='centerblocks']/table[@class='list']/tr/td/a[contains(text(),'Episode')]"):
    try:
      # Episode title
      episode = item.xpath("./text()")[0]
      # episode link
      link = item.xpath("./@href")[0]
      if link.startswith("http") == False:
        link = SITEURL + link
    except:
      continue

    # Add the found item to the collection
    oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=episode), title=episode))
  
  # If there are no channels, warn the user
  if len(oc) == 0:
    return ObjectContainer(header=title, message=L('EpisodeWarning'))

  return oc

####################################################################################################

@route(PREFIX + '/apnitv/playerlinksmenu')
def PlayerLinksMenu(url, title):
  oc = ObjectContainer(title2=title)
  
  # Add the item to the collection
  oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('Fastplay')), title=L('Fastplay'), thumb=R('icon-flashplayer.png')))
  oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('Dailymotion')), title=L('Dailymotion'), thumb=R('icon-dailymotion.png')))
  
  # If there are no channels, warn the user
  if len(oc) == 0:
    return ObjectContainer(header=title, message=L('PlayerWarning'))

  return oc

####################################################################################################

@route(PREFIX + '/apnitv/episodelinksmenu')
def EpisodeLinksMenu(url, title, type):
  oc = ObjectContainer(title2=title)

  html = HTML.ElementFromURL(url)
  
  if type == "Dailymotion":
    items = GetDailymotion(html)
  elif type == "Fastplay":
    items = GetFlashPlayer(html)
  else:
    items = None

  for item in items:
    try:
      # Video site
      videosite = item.xpath("./text()")[0]
      # Video link
      link = item.xpath("./@href")[0]
      link = URLCheck(link)
      # Show date
      date = GetShowDate(videosite)
      # Get video source url and thumb
      link = GetURLSource(link,url,date)
    except:
      continue
    
    # Add the found item to the collection
    if link.find('dailymotion') != -1:
      #Log ('Dailymotion Link: ' + link)
      oc.add(VideoClipObject(
        url = link, 
        title = videosite, 
        thumb = Resource.ContentsOfURLWithFallback(R(ICON), fallback=R(ICON)),
        originally_available_at = Datetime.ParseDate(date).date()))
    elif link.find('playwire') != -1:
      oc.add(CreateVideoObject(
        url = link, 
        title = videosite, 
        thumb = Resource.ContentsOfURLWithFallback(R(ICON), fallback=R(ICON)),
        originally_available_at = Datetime.ParseDate(date).date()))

  # If there are no channels, warn the user
  if len(oc) == 0:
    return ObjectContainer(header=title, message=L('SourceWarning'))

  return oc
  
####################################################################################################

def GetURLSource(url, referer, date=''):
  html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
  string = HTML.StringFromElement(html)
    
  if string.find('dailymotion') != -1:
    url = html.xpath("//div[@id='topsource']/a/@href")[0]
  elif string.find('fastplay') != -1:
    url = html.xpath("//div[@id='topsource']/a/@href")[0]
    
    html = HTML.ElementFromURL(url=url, headers={'Referer': url})
    string = HTML.StringFromElement(html)

    if string.find('playwire') != -1:
      url = 'http://cdn.playwire.com/' + html.xpath("//script/@data-publisher-id")[0] + '/video-' + date + '-' + html.xpath("//script/@data-video-id")[0] + '.mp4'
    elif string.find('dailymotion') != -1:
      url = html.xpath("//iframe[contains(@src,'dailymotion')]/@src")[0]
      if url.startswith("http") == False:
        url = url.lstrip('htp:/')
        url = 'http://' + url

  return url

####################################################################################################

def GetDailymotion(html):
  items = html.xpath("//table[@class='list']/tr[@class='heading' and contains(td/text(),'Dailymotion')]/following-sibling::tr/td/a")
  return items

####################################################################################################

def GetFlashPlayer(html):
  items = html.xpath("//table[@class='list']/tr[@class='heading' and contains(td/text(),'Fastplay')]/following-sibling::tr/td/a")
  return items

####################################################################################################

def GetShowDate(title):
  # find the date in the show title
  match = re.search(r'\w+\s\d{1,2}[thsrdn]+\s\d{4}', title)
  #Log ('match: ' + match.group())
  # remove the prefix from date
  match = re.sub(r'(st|nd|rd|th)', "", match.group())
  if match.find('Augu') != -1:
    match = match.replace("Augu", "August", 1)
  # strip date to struct
  date = time.strptime(match, '%B %d %Y')
  # convert date
  date = time.strftime('%Y%m%d', date)
  #Log ('Date: ' + date)
  return date

####################################################################################################

def URLCheck(url):
  url = url.rstrip('\r\n/') + '/'
  if url.startswith("http") == False:
    url = url.lstrip('htp:/')
    url = 'http://' + url
  return url

####################################################################################################

@route(PREFIX + '/apnitv/createvideoobject')
def CreateVideoObject(url, title, thumb, originally_available_at, include_container=False):
  try:
    originally_available_at = Datetime.ParseDate(originally_available_at).date()
  except:
    originally_available_at = None
  
  container = Container.MP4
  video_codec = VideoCodec.H264
  audio_codec = AudioCodec.AAC
  audio_channels = 2

  video_object = VideoClipObject(
    key = Callback(
      CreateVideoObject,
      url=url,
      title=title,
      thumb=thumb,
      originally_available_at=originally_available_at,
      include_container=True
    ),
    rating_key = url,
    title = title,
    thumb=thumb,
    originally_available_at=originally_available_at,
    items = [
      MediaObject(
        parts = [
          PartObject(key=url)
        ],
        container = container,
        video_codec = video_codec,
        audio_codec = audio_codec,
        audio_channels = audio_channels
      )
    ]
  )

  if include_container:
    return ObjectContainer(objects=[video_object])
  else:
    return video_object

####################################################################################################