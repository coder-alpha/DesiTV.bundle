
import common
#from lxml import etree


SITETITLE = 'Desi-Tashan'
SITEURL = 'http://www.desi-tashan.com/'
SITETHUMB = 'icon-desitashan.png'

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/desi-tashan/channels')
def ChannelsMenu(url):
	oc = ObjectContainer(title2=SITETITLE)

	html = HTML.ElementFromURL(url)


	for item in html.xpath("//ul[@id='menu-indian-menu']//li//a"):
		try:
			# Channel title
			channel = item.xpath("text()")[0]
	#		Log("Channel = "+channel)
	#		Log("item "+ etree.tostring(item, pretty_print=True))
			# Channel link
			link = item.xpath("@href")[0]
			if link.startswith("http") == False:
				link = SITEURL + link
			
			#Log("Channel Link: " + link)
		except:
			channel = item.xpath("./span/text()")
			if(len(channel) != 0):
				channel = channel[0]	
	#			Log("Channel = "+str(channel))
	#			Log("item "+ etree.tostring(item, pretty_print=True))
				# Channel link
				link = item.xpath("@href")[0]
				if link.startswith("http") == False:
					link = SITEURL + link
			else:
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

@route(PREFIX + '/desi-tashan/showsmenu')
def ShowsMenu(url, title):
	oc = ObjectContainer(title2=title)
	#Log("Shows Menu: " + url + ":" + title)
	html = HTML.ElementFromURL(url)
	
	for item in html.xpath("//div[contains(@class,'fusion-one-fourth fusion-layout-column fusion-spacing-yes ')]//div[@class='fusion-column-wrapper']//h4//a"):
		#Log("item "+ etree.tostring(item, pretty_print=True))
		try:
			# Show title
			show = item.xpath("text()")[0]
			#Log("show name: " + show)
			# Show link
			link = item.xpath("@href")[0]
			#Log("show link: " + link)
			if link.startswith("http") == False:
				link = SITEURL + link.lstrip('/')
#				Log("final show link: " + link)	
		except:
			#Log("In Excpetion")
			continue

		# Add the found item to the collection
		oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=link, title=show), title=show))
		
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('ShowWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desi-tashan/episodesmenu')
def EpisodesMenu(url, title):
	oc = ObjectContainer(title2 = unicode(title))

	pageurl = url

	html = HTML.ElementFromURL(pageurl)
	
	for item in html.xpath("//div[contains(@class,'fusion-one-fourth fusion-layout-column fusion-spacing-yes ')]//div[@class='fusion-column-wrapper']//h4//a"):
		try:
			# Episode title
			episode = unicode(str(item.xpath("text()")[0].strip()))
			if("Written Episode" in episode):
				continue
			# episode link
			link = item.xpath("@href")[0]
			if link.startswith("http") == False:
				link = SITEURL + link.lstrip('/')
			#Log("Episode: " + episode + " Link: " + link)
		except:
			continue

		# Add the found item to the collection
		if 'Written Episode' not in episode:
			oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=episode, type=L('Tv')), title=episode))
	
	# Find the total number of pages
	next_page = ' '
	try:
		next_page = html.xpath("//div[@class='pagination clearfix']//a[@class='pagination-next']/@href")[0]
	except:
		pass
	if next_page.startswith("http") == False:
		if (len(next_page.split('/')) == 3):
			next_page = pageurl + next_page
		else:
			next_page = SITEURL + next_page.lstrip('/')

	# Add the next page link if exists
	if ' ' not in next_page:
		oc.add(DirectoryObject(key=Callback(EpisodesMenu, url=next_page, title=title), title=L('Pages')))
	
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('EpisodeWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desi-tashan/playerlinksmenu')
def PlayerLinksMenu(url, title, type):
	oc = ObjectContainer(title2 = unicode(title))
	
	# Add the item to the collection
	content = HTTP.Request(url).content
	#Log("PlayerLinksMenu " + url + ":" + title + ":" +  type)
	if content.find('Playwire HD') != -1:
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='Playwire HD'), title='Playwire HD', thumb=R('icon-playwire.png')))

	if content.find('PlayU HD') != -1:
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='PlayU HD'), title='PlayU HD', thumb=R('icon-playu.png')))

	if content.find('LetWatch HD') != -1:
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='LetWatch HD'), title='Letwatch HD', thumb=R('icon-letwatchus.png')))

# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('PlayerWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desi-tashan/episodelinksmenu')
def EpisodeLinksMenu(url, title, type):
	oc = ObjectContainer(title2 = unicode(title))

	html = HTML.ElementFromURL(url)
	
	# Summary
	summary = GetSummary(html)
	items = GetParts(html, type)

	links = []
	thumb = ''

	for item in items:
		
		try:
			# Video site
			videosite = item.xpath("./text()")[0]
			#Log("Video Site: " + videosite)
			# Video link
			link = item.xpath("./@href")[0]
			#Log("Link: " + link)
			if link.startswith("http") == False:
				link = link.lstrip('htp:/')
				link = 'http://' + link
			if len(links) > 1 and link.find('Part 1') != -1:
				break
			# Get video source url and thumb
			link, thumb = GetTvURLSource(link,url)
			#Log("Video Site: " + videosite + " Link: " + link + " Thumb: " + thumb)
		except:
			continue

		# Add the found item to the collection
		if link.find('playu') != -1 or link.find('vidshare') != -1  or link.find('playwire') != -1:
			links.append(URLService.NormalizeURL(link))
			#Log ('Link: ' + link)
			oc.add(VideoClipObject(
				url = link,
				title = videosite,
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
				summary = summary))
	
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('SourceWarning'))

	return oc

####################################################################################################

def GetTvURLSource(url, referer):
		
	html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
	string = HTML.StringFromElement(html)
	if string.find('playu.net') != -1:
		url = html.xpath("//iframe[contains(@src,'playu.net')]/@src")[0]
		url = url.replace('playu.net','playu.me',1)
	elif string.find('vidshare.us') != -1:
		url = html.xpath("//iframe[contains(@src,'vidshare.us')]/@src")[0]
	elif string.find('playwire.com') != -1:
		#Log("Found Playwire link")
		url = html.xpath("//script/@data-config")[0]
	else: 
		Log("NO KNOWN PLAYER FOUND")
	thumb = GetThumb(html)

	return url, thumb
	
####################################################################################################

def GetParts(html, keyword):
	items = []
	items = html.xpath("//h2[@class='vidLinks'][contains(text(),'"+keyword+"')]/following-sibling::p[@class='vidLinksContent']")[0]
	return items

####################################################################################################

def GetSummary(html):
	try:
		summary = html.xpath("//h1[@class='entry_title entry-title']/text()")[0]
		#summary = summary.replace(" preview: ","",1)
		#summary = summary.replace("Find out in","",1)
	except:
		summary = ''
	return summary

####################################################################################################

def GetThumb(html):
	try:
		thumb = html.xpath("//ul[@class='singlecontent']/li/p/img/@src")[0]
		#Log ('Thumb: ' + thumb)
	except:
		thumb = R(ICON)
	return thumb

