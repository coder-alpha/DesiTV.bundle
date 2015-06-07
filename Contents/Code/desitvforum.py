
import common
import urlparse
import re
import time
import datetime
import test

SITETITLE = L('DesiTvForumTitle')
SITEURL = 'http://www.desitvforum.net/forum/'
SITETHUMB = 'icon-desitvforum.png'

DESITVFORUMTVSHOWS = ['Telly News','Zee Tv Archive','Other Show (Zee Tv)','Lie To Me','How I Met Your Mother (Season 5)','MasterChef Australia','Masterchef US','The Good Guys Season 1','Two And A Half Men Season 7','The Simpsons Season 17','Love2 Hate U','Chivas Studio – Gentlemen\'s Code','Star World Archive']

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/desitvforum/typemenu')
def TypeMenu(url):
  oc = ObjectContainer(title2=SITETITLE)

  # Add the item to the collection
  oc.add(DirectoryObject(key=Callback(ChannelsMenu, url=url), title=L('Tv'), thumb=R('icon-default.png')))
  #oc.add(DirectoryObject(key=Callback(MovieTypeMenu, url=url), title=L('Movies'), thumb=R('icon-default.png')))

  # If there are no channels, warn the user
  if len(oc) == 0:
	return ObjectContainer(header=title, message=L('TypeWarning'))

  return oc

####################################################################################################

@route(PREFIX + '/desitvforum/channels')
def ChannelsMenu(url):
  oc = ObjectContainer(title2=SITETITLE)

  html = HTML.ElementFromURL(url)

  for item in html.xpath("//table[@class='tborder']//tbody/tr"):
	try:
	  # Channel title
	  channel = item.xpath("./td[@class='alt1Active']/div[1]/a/strong/text()")[0]
	  # Channel link
	  link = item.xpath("./td[@class='alt1Active']/div[1]/a/@href")[0]
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

@route(PREFIX + '/desitvforum/channels/shows')
def ShowsMenu(url, title):
  oc = ObjectContainer(title2=title)

  html = HTML.ElementFromURL(url)

  for item in html.xpath("//table[@class='tborder']//td[@class='alt1Active']"):
	try:
	  # Show title
	  show = item.xpath(".//div/a/strong[not(font) and not(b)]/text()")[0]
	  # Show link
	  link = item.xpath(".//div/a/@href")[0]
	  if link.startswith("http") == False:
		link = SITEURL + link
	except:
	  continue

	if show not in DESITVFORUMTVSHOWS:
	  # Add the found item to the collection
	  oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=link, title=show), title=show))

  # If there are no channels, warn the user
  if len(oc) == 0:
	return ObjectContainer(header=title, message=L('ShowWarning'))

  return oc

####################################################################################################

@route(PREFIX + '/desitvforum/channels/shows/episodes')
def EpisodesMenu(url, title, page=1, pages=1):
  oc = ObjectContainer(title2=title)

  pageurl = url + 'index' + str(page) + '.html'

  html = HTML.ElementFromURL(pageurl)

  for item in html.xpath("//table[@id='threadslist']//tbody[2]/tr/td/div/a[contains(text(),'Watch Online') or contains(span/text(),'Watch Online')]"):
	try:
	  # Episode title
	  episode = item.xpath("./text() | ./span/text()")[0]

	  # episode link
	  link = item.xpath("./@href")[0]
	  if link.startswith("http") == False:
		link = SITEURL + link
	except:
	  continue

	# Add the found item to the collection
	oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=link, title=episode, type=L('Tv')), title=episode))

  # Find the total number of pages
  if pages == 1:
	for items in html.xpath("//div[@class='pagenav']//td[@class='vbmenu_control' and contains(text(),'Page')]"):
	  try:
		pages = int((items.xpath("./text()")[0].split()[-1]).strip())
	  except:
		continue

  # Add the next page link if exists
  if page < pages:
	oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=url, title=title, page=int(page)+1, pages=pages), title=L('Pages')))

  # If there are no channels, warn the user
  if len(oc) == 0:
	return ObjectContainer(header=title, message=L('EpisodeWarning'))

  return oc

####################################################################################################

@route(PREFIX + '/desitvforum/channels/shows/episodes/source')
def EpisodeLinksMenu(url, title, type):
  oc = ObjectContainer(title2=title)

  html = HTML.ElementFromURL(url)

  items = GetSourceType(html)

  for item in items:
	try:
	  # Video site
	  videosite = item.xpath("./text()")[0]
	  # Video link
	  link = item.xpath("./@href")[0]
	  if link.startswith("http") == False:
		link = link.lstrip('htp:/')
		link = 'http://' + link
	  # Show date
	  date = GetShowDate(videosite)
	  # Get video source url and thumb
	  link, thumb = GetTvURLSource(link,url,date)
	except:
	  continue

	# Add the found item to the collection
	if link.find('dailymotion') != -1:
	  #Log ('Dailymotion Link: ' + link)
	  oc.add(VideoClipObject(
		url = link, 
		title = videosite,
		thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),        
		originally_available_at = Datetime.ParseDate(date).date()))
	elif link.find('playwire') != -1:
	  oc.add(CreateVideoObject(
		url = link, 
		title = videosite,
		thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
		originally_available_at = Datetime.ParseDate(date).date()))

  # If there are no channels, warn the user
  if len(oc) == 0:
	return ObjectContainer(header=title, message=L('SourceWarning'))

  return oc

####################################################################################################

def GetTvURLSource(url, referer, date=''):
  html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
  string = HTML.StringFromElement(html)

  if string.find('dailymotion') != -1:
	url = html.xpath("//iframe[contains(@src,'dailymotion')]/@src")[0]
  elif string.find('playwire') != -1:
	url = 'http://cdn.playwire.com/' + html.xpath("//script/@data-publisher-id")[0] + '/video-' + date + '-' + html.xpath("//script/@data-video-id")[0] + '.mp4'

  thumb = GetThumb(html)

  return url, thumb

####################################################################################################

def GetSourceType(html):
  #items = html.xpath("//table[@class='tborder']//div[@align='center']/b[contains(text(),'dailymotion 720p')]/following-sibling::a[count(. | //b[count(//b[contains(text(),'dailymotion 720p')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(text(),'dailymotion 720p')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
  items = html.xpath("//table[@class='tborder']//div[@align='center']/a[contains(text(),'Watch Online')]")
  return items

####################################################################################################

def GetShowDate(title):
  # find the date in the show title
  match = re.search(r'\d{1,2}[thsrdn]+\s\w+\s?\d{4}', title)
  Log ('date match: ' + match.group())
  # remove the prefix from date
  match = re.sub(r'(st|nd|rd|th)', "", match.group(), 1)
  Log ('remove prefix from match: ' + match)
  # add space between month and year
  match = re.sub(r'(\d{1,2}\s\w+)(\d{4})', r'\1 \2', match)
  Log ('add space to month and year match: ' + match)
  # strip date to struct
  date = time.strptime(match, '%d %B %Y')
  # convert date
  date = time.strftime('%Y%m%d', date)
  Log ('Final Date: ' + date)
  return date

####################################################################################################

def GetThumb(html):
  try:
	thumb = html.xpath("//ul[@class='singlecontent']/li/p/img/@src")[0]
	#Log ('Thumb: ' + thumb)
  except:
	thumb = R(ICON)
  return thumb

####################################################################################################

@route(PREFIX + '/desitvforum/createvideoobject')
def CreateVideoObject(url, title, thumb, originally_available_at='', include_container=False):
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
