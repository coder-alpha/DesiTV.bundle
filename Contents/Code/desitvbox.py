
import common
import re
import time
import datetime

SITETITLE = 'DesiTvBox'
SITEURL = 'http://www.desitvbox.me/'
SITETHUMB = 'icon-desitvbox.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/desitvbox/channels')
def ChannelsMenu(url):
	oc = ObjectContainer(title2=SITETITLE)

	html = HTML.ElementFromURL(url)

	for item in html.xpath("//div[@id='categories']//a"):
		try:
			# Channel title
			channel = item.xpath("text()")[0]

			# Channel link
			link = item.xpath("@href")[0]
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

@route(PREFIX + '/desitvbox/showsmenu')
def ShowsMenu(url, title):
	oc = ObjectContainer(title2=title)

	html = HTML.ElementFromURL(url)
	
	for item in html.xpath("//li[@class='categories']//li//a"):
		try:
			# Show title
			show = item.xpath("text()")[0]
			
			# Show link
			link = item.xpath("@href")[0]
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

@route(PREFIX + '/desitvbox/episodesmenu')
def EpisodesMenu(url, title):
	oc = ObjectContainer(title2 = unicode(title))

	pageurl = url

	html = HTML.ElementFromURL(pageurl)
	
	for item in html.xpath("//div[@id='left-inside']//h2[@class='titles']//a"):
		try:
			# Episode title
			episode = unicode(str(item.xpath("text()")[0].strip()))
			
			# episode link
			link = item.xpath("@href")[0]
			if link.startswith("http") == False:
				link = SITEURL + link
			#Log("Episode: " + episode + " Link: " + link)
		except:
			continue

		# Add the found item to the collection
		if 'Watch Online' in episode:
			oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=episode, type=L('Tv')), title=episode))
	
	# Find the total number of pages
	pages = ' '
	try:
		pages = html.xpath("//div[@id='left-inside']//p[@class='pagination']//a//@href")[0]
	except:
		pass
			
	# Add the next page link if exists
	if ' ' not in pages:
		oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=pages, title=title), title=L('Pages')))
	
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('EpisodeWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desitvbox/playerlinksmenu')
def PlayerLinksMenu(url, title, type):
	oc = ObjectContainer(title2 = unicode(title))
	
	# Add the item to the collection
	content = HTTP.Request(url).content
	
	if type == "TV":
		if content.find('Dailymotion') != -1:
			oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='Dailymotion'), title='Dailymotion', thumb=R('icon-dailymotion.png')))
		if content.find('Flash') != -1:
			oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='Flash'), title='Flash', thumb=R('icon-playwire.png')))
		if content.find('Cloudy') != -1:
			oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='Cloudy'), title='Cloudy', thumb=R('icon-cloudy.png')))
		if content.find('Letwatch') != -1:
			oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='Letwatch'), title='Letwatch', thumb=R('icon-letwatchus.png')))
		if content.find('Letwatch 720p HD') != -1:
			oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='Letwatch 720p HD'), title='Letwatch 720p HD', thumb=R('icon-letwatchus.png')))
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('PlayerWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desitvbox/episodelinksmenu')
def EpisodeLinksMenu(url, title, type):
	oc = ObjectContainer(title2 = unicode(title))

	html = HTML.ElementFromURL(url)
	
	# Summary
	summary = GetSummary(html)
	items = GetParts(html, type)

	links = []

	for item in items:
		
		try:
			# Video site
			videosite = item.xpath("./text()")[0]
			Log("Video Site: " + videosite)
			# Video link
			link = item.xpath("./@href")[0]
			if link.startswith("http") == False:
				link = link.lstrip('htp:/')
				link = 'http://' + link
			if len(links) > 1 and link.find('Part 1') != -1:
				break
			# Show date
			date = GetShowDate(videosite)
			# Get video source url and thumb
			link, thumb = GetTvURLSource(link,url,date)
			Log("Video Site: " + videosite + " Link: " + link + " Thumb: " + thumb)
		except:
			continue
			
		try:
			originally_available_at = Datetime.ParseDate(date).date()
		except:
			originally_available_at = ''

		# Add the found item to the collection
		if link.find('vidshare') != -1 or link.find('dailymotion') != -1 or link.find('playwire') != -1 or link.find('cloudy') != -1:
			links.append(URLService.NormalizeURL(link))
			if link.find('cloudy') != -1 and not isValidCloudyURL(link):
				videosite = videosite + ' (vid removed)'
			#Log ('Link: ' + link)
			oc.add(VideoClipObject(
				url = link,
				title = videosite,
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),				
				summary = summary,
				originally_available_at = originally_available_at))

	
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('SourceWarning'))

	return oc

####################################################################################################

def GetTvURLSource(url, referer, date=''):

	if 'xpressvids.info' in url:
		url = url.replace('xpressvids.info','dramatime.me')
		
	html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
	string = HTML.StringFromElement(html)

	if string.find('dailymotion') != -1:
		url = html.xpath("//iframe[contains(@src,'dailymotion')]/@src")[0]
	elif string.find('vidshare') != -1:
		url = html.xpath("//iframe[contains(@src,'vidshare')]/@src")[0]
	elif string.find('cloudy') != -1:
		url = html.xpath("//iframe[contains(@src,'cloudy')]/@src")[0]
	elif string.find('playwire') != -1:
		url = html.xpath("//script/@data-config")[0]

	thumb = GetThumb(html)

	return url, thumb
	
####################################################################################################

def GetParts(html, keyword):
	items = html.xpath("//div[@id='left-inside']//p[contains(b//text(),'"+keyword+"')]//following-sibling::p[1]//a")
	if len(items) == 0:
		items = html.xpath("//div[@id='left-inside']//p[contains(span//text(),'"+keyword+"')]//following-sibling::p[1]//a")
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

def GetSummary(html):
	try:
		summary = html.xpath("//div[@class='content']//font[@size='3']/font/text()")[0]
		summary = summary.replace(" preview: ","",1)
		summary = summary.replace("Find out in","",1)
	except:
		summary = None
	return summary

####################################################################################################

def GetThumb(html):
	try:
		thumb = html.xpath("//ul[@class='singlecontent']/li/p/img/@src")[0]
		#Log ('Thumb: ' + thumb)
	except:
		thumb = R(ICON)
	return thumb

####################################################################################################

########################################################################################
def isValidCloudyURL(url):
		
	vurl = False
	try:
		# use api www.cloudy.ec/api/player.api.php?'user=undefined&pass=undefined&file={file}&key={key}
		# https://github.com/Eldorados/script.module.urlresolver/blob/master/lib/urlresolver/plugins/cloudy.py
		
		content = unicode(HTTP.Request(url).content)
		elems = HTML.ElementFromString(content)
		key = elems.xpath("substring-before(substring-after(//script[@type='text/javascript'][3]//text(),'key: '),',')").replace("\"",'')
		file = elems.xpath("substring-before(substring-after(//script[@type='text/javascript'][3]//text(),'file:'),',')").replace("\"",'')
		
		furl = "http://www.cloudy.ec/api/player.api.php?'user=undefined&pass=undefined&file="+file+"&key="+key
		
		content = unicode(HTTP.Request(furl).content)
		#Log(vurl)
		if 'error' not in content:
			vurl = True
	except:
		vurl = False
		
	#Log("bool --------" + str(vurl))
	return vurl