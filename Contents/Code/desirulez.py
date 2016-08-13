
import common
import urlparse
import re
import time
import datetime

SITETITLE = L('DesiRulezTitle')
SITEURL = 'http://www.desirulez.me/'
SITETHUMB = 'icon-desirulez.png'
BOLLYWOODMOVIES = 'http://www.desirulez.net/forums/260-Bollywood-Movies?s=ff8112e19bee5e07f0e95696812ae217'

DESIRULEZMOVIES = ['Latest & Exclusive Movie HQ']

PREFIX = common.PREFIX
NAME = common.NAME
ART = common.ART
ICON = common.ICON

####################################################################################################

@route(PREFIX + '/desirulez/typemenu')
def TypeMenu(url):
	oc = ObjectContainer(title2=SITETITLE)
	
	# Add the item to the collection
	oc.add(DirectoryObject(key=Callback(ChannelsMenu, url=url), title=L('Tv'), thumb=R('icon-default.png')))
	oc.add(DirectoryObject(key=Callback(MovieTypeMenu, url=url), title=L('Movies'), thumb=R('icon-default.png')))
	
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('TypeWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desirulez/movietype')
def MovieTypeMenu(url):
	oc = ObjectContainer(title2=SITETITLE)

	html = HTML.ElementFromURL(url)

	for item in html.xpath("//li[@id='cat17']//h2[@class='forumtitle']/a"):
		try:
			# Movie Section
			section = item.xpath("./text()")[0]

			# Section Link
			link = item.xpath("./@href")[0]
			if link.startswith("http") == False:
				link = SITEURL + link
		except:
			continue

		if section in DESIRULEZMOVIES:
			oc.add(DirectoryObject(key=Callback(MovieListMenu, url=link, title=section), title=section))
			
	oc.add(DirectoryObject(key=Callback(MovieSectionMenu, url=BOLLYWOODMOVIES, title=L('BollywoodMovies')), title=L('BollywoodMovies')))
		
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=SITETITLE, message=L('MovieWarning'))

	return oc

####################################################################################################
@route(PREFIX + '/desirulez/movielist')
def MovieListMenu(url, title, page=1, pages=1):
	oc = ObjectContainer(title2=title)

	pageurl = url + '/page' + str(page)
	
	html = HTML.ElementFromURL(pageurl)
	
	for item in html.xpath("//div[@class='inner']/h3[@class='threadtitle']/a[contains(@id,'thread_title') and contains(text(),'Watch')]"):
		try:
			# Movie title
			movie = item.xpath("./text()")[0]
			
			# Movie link
			link = item.xpath("./@href")[0]
			if link.startswith("http") == False:
				link = SITEURL + link
		except:
			continue

		# Add the found item to the collection
		oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=movie, type=L('Movies')), title=movie))
	
	# Find the total number of pages
	if pages == 1:
		for items in html.xpath("//span/a[contains(text(),'Page') and @class='popupctrl']"):
			try:
				pages = int((items.xpath("./text()")[0].split()[-1]).strip())
			except:
				continue

	# Add the next page link if exists
	if page < pages:
		oc.add(DirectoryObject(key=Callback(MovieListMenu, url=url, title=title, page=int(page)+1, pages=pages), title=L('Pages')))
	
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('EpisodeWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desirulez/moviesection')
def MovieSectionMenu(url, title):
	oc = ObjectContainer(title2=SITETITLE)
	
	html = HTML.ElementFromURL(url)
	
	for item in html.xpath("//div[@class='forumbitBody']//h2[@class='forumtitle']/a"):
		try:
			# Movie Section
			section = item.xpath("./text()")[0]
	
			# Section Link
			link = item.xpath("./@href")[0]
			if link.startswith("http") == False:
				link = SITEURL + link
		except:
			continue
	
		if section != 'Upcoming Movie Trailers':
			oc.add(DirectoryObject(key=Callback(MovieListMenu, url=link, title=section), title=section))
		
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=SITETITLE, message=L('MovieWarning'))
	
	return oc

####################################################################################################

@route(PREFIX + '/desirulez/channels')
def ChannelsMenu(url):
	oc = ObjectContainer(title2=SITETITLE)

	html = HTML.ElementFromURL(url)

	for item in html.xpath("//li[@id='cat41']//div[@class='foruminfo td']"):
		try:
			# Channel title
			channel = item.xpath("./div/div/div/h2/a/text()")[0]

			# Channel link
			link = item.xpath("./div/div/div/h2/a/@href")[0]
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

@route(PREFIX + '/desirulez/showsmenu')
def ShowsMenu(url, title):
	oc = ObjectContainer(title2=title)

	html = HTML.ElementFromURL(url)
	
	for item in html.xpath("//div[@class='forumbitBody']//div[@class='foruminfo']"):
		try:
			# Show title
			show = item.xpath("./div/div/div/h2/a/text()")[0]
			
			# Show link
			link = item.xpath("./div/div/div/h2/a/@href")[0]
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

@route(PREFIX + '/desirulez/episodesmenu')
def EpisodesMenu(url, title, page=1, pages=1):
	oc = ObjectContainer(title2=title)

	pageurl = url + '/page' + str(page)
	
	html = HTML.ElementFromURL(pageurl)
	
	for item in html.xpath("//h3[@class='threadtitle']/a[contains(text(),'Watch Online')]"):
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
		oc.add(PopupDirectoryObject(key=Callback(PlayerLinksMenu, url=link, title=episode, type=L('Tv')), title=episode))
	
	# Find the total number of pages
	if pages == 1:
		for items in html.xpath("//span/a[contains(text(),'Page') and @class='popupctrl']"):
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

@route(PREFIX + '/desirulez/playerlinksmenu')
def PlayerLinksMenu(url, title, type):
	oc = ObjectContainer(title2=title)
	
	# Add the item to the collection
	if type == "TV":
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type='LetWatchUS'), title='LetWatchUS', thumb=R('icon-letwatchus.png')))
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('DailymotionHD')), title=L('DailymotionHD'), thumb=R('icon-dailymotion.png')))
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('DailymotionDVD')), title=L('DailymotionDVD'), thumb=R('icon-dailymotion.png')))
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('DailymotionSD')), title=L('DailymotionSD'), thumb=R('icon-dailymotion.png')))
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('FlashPlayerHD')), title=L('FlashPlayerHD'), thumb=R('icon-flashplayer.png')))
		oc.add(DirectoryObject(key=Callback(EpisodeLinksMenu, url=url, title=title, type=L('FlashPlayerDVD')), title=L('FlashPlayerDVD'), thumb=R('icon-flashplayer.png')))
	elif type == "Movies":
		oc.add(DirectoryObject(key=Callback(MovieLinksMenu, url=url, title=title, type=L('Dailymotion')), title=L('Dailymotion'), thumb=R('icon-dailymotion.png')))
		oc.add(DirectoryObject(key=Callback(MovieLinksMenu, url=url, title=title, type=L('FlashPlayer')), title=L('FlashPlayer'), thumb=R('icon-flashplayer.png')))
		
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('PlayerWarning'))

	return oc

####################################################################################################

@route(PREFIX + '/desirulez/movielinksmenu')
def MovieLinksMenu(url, title, type):
	oc = ObjectContainer(title2=title)

	html = HTML.ElementFromURL(url)
	
	# Get thumb
	thumb = html.xpath("//div[@class='content']//img/@src")[0]
	
	if type == "Dailymotion":
		items = GetDailymotion(html)
	elif type == "Flash Player":
		items = GetFlashPlayer(html)
	else:
		items = None

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
			#date = GetMoviePostDate(html)
			# Get video source url
			link = GetMovieURLSource(link,url,date='')
		except:
			continue
		
		# Add the found item to the collection
		if link.find('dailymotion') != -1:
			#Log ('Dailymotion Link: ' + link)
			oc.add(VideoClipObject(
				url = link, 
				title = videosite, 
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))))
		elif link.find('playwire') != -1:
			oc.add(CreateVideoObject(
				url = link, 
				title = videosite, 
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))))

	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('SourceWarning'))

	return oc
	
####################################################################################################

@route(PREFIX + '/desirulez/episodelinksmenu')
def EpisodeLinksMenu(url, title, type):
	oc = ObjectContainer(title2=title)

	html = HTML.ElementFromURL(url)
	
	# Summary
	summary = GetSummary(html)
	
	if type == "LetWatchUS":
		items = GetLetwatchusHD(html)
	elif type == "Dailymotion HD":
		items = GetDailymotionHD(html)
	elif type == "Dailymotion DVD":
		items = GetDailymotionDVD(html)
	elif type == "Dailymotion SD":
		items = GetDailymotionSD(html)
	elif type == "Flash Player HD":
		items = GetFlashPlayerHD(html)
	elif type == "Flash Player DVD":
		items = GetFlashPlayerDVD(html)
	else:
		items = None

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
		if link.find('vidshare') != -1:
			links.append(URLService.NormalizeURL(link))
			#Log ('LetwatchUS Link: ' + link)
			oc.add(VideoClipObject(
				url = link,
				title = videosite,
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),				
				summary = summary,
				originally_available_at = originally_available_at))
		elif link.find('dailymotion') != -1:
			links.append(URLService.NormalizeURL(link))
			Log ('Dailymotion Link: ' + link)
			oc.add(VideoClipObject(
				url = link,
				title = videosite,
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),				
				summary = summary,
				originally_available_at = originally_available_at))
		elif link.find('playwire') != -1 or link.find('phoenix') != -1:
			oc.add(CreateVideoObject(
				url = link, 
				title = videosite,
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
				summary = summary,
				originally_available_at = originally_available_at))
			
	if len(links) > 10:
		JSON_URL = 'http://www.dailymotion.com/json/video/%s?fields=video_id,title,thumbnail_large_url,url,stream_h264_sd_url,stream_h264_url,stream_h264_hd_url,rating,duration,description'
		video_id1 = links[0].rsplit('/',1)[1]
		json_url1 = JSON_URL % video_id1
		video_id2 = links[1].rsplit('/',1)[1]
		json_url2 = JSON_URL % video_id2
	
		vco = VideoClipObject(
			key = title,
			rating_key = title,
			title = 'Play All - ' + title,
			thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
			summary = summary,
			originally_available_at = originally_available_at)
		mo = MediaObject(
			parts = [PartObject(key=Callback(PlayVideo, url=json_url1, post_url=json_url1, fmt='hd'))],
			container = Container.MP4,
			bitrate = '1500',
			video_resolution = '720',
			video_codec = VideoCodec.H264,
			audio_codec = AudioCodec.AAC,
			audio_channels = 2,
			optimized_for_streaming = True)
		mo1 = MediaObject(
			parts = [PartObject(key=Callback(PlayVideo, url=json_url2, post_url=json_url2, fmt='hd'))],
			container = Container.MP4,
			bitrate = '1500',
			video_resolution = '720',
			video_codec = VideoCodec.H264,
			audio_codec = AudioCodec.AAC,
			audio_channels = 2,
			optimized_for_streaming = True)
		
		vco.add(mo1)
		vco.add(mo)
		oc.add(vco)
	
	# If there are no channels, warn the user
	if len(oc) == 0:
		return ObjectContainer(header=title, message=L('SourceWarning'))

	return oc
	
####################################################################################################

def GetMovieURLSource(url, referer, date=''):
	html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
	string = HTML.StringFromElement(html)
		
	if string.find('dailymotion') != -1:
		url = html.xpath("//div[contains(@id,'tab1') and contains(@src,'dailymotion')]/@src")[0]
	elif string.find('playwire') != -1:
		json = JSON.ObjectFromURL('http://cdn.playwire.com/v2/' + html.xpath("//script/@data-publisher-id")[0] + '/config/' + html.xpath("//script/@data-video-id")[0] + '.json')
		url = json['src']
		url = url.replace('rtmp://streaming.playwire.com/','http://cdn.playwire.com/').replace('mp4:','',1)
		Log("URL: " + url)
		#url = 'http://cdn.playwire.com/' + html.xpath("//script/@data-publisher-id")[0] + '/video-' + date + '-' + html.xpath("//script/@data-video-id")[0] + '.mp4'

	return url

####################################################################################################

def GetTvURLSource(url, referer, date=''):
	html = HTML.ElementFromURL(url=url, headers={'Referer': referer})
	string = HTML.StringFromElement(html)

	if string.find('dailymotion') != -1:
		url = html.xpath("//iframe[contains(@src,'dailymotion')]/@src")[0]
	elif string.find('vidshare') != -1:
		url = html.xpath("//iframe[contains(@src,'vidshare')]/@src")[0]
	elif string.find('playwire') != -1:
		#Log("pID: " + str(len(html.xpath("//script/@data-publisher-id"))) + " vID: " + str(len(html.xpath("//script/@data-video-id"))))
		if len(html.xpath("//script/@data-publisher-id")) != 0 and len(html.xpath("//script/@data-video-id")) != 0:
			url = 'http://cdn.playwire.com/' + html.xpath("//script/@data-publisher-id")[0] + '/video-' + date + '-' + html.xpath("//script/@data-video-id")[0] + '.mp4'
		else:
			#Log("JSON: " + str(html.xpath("//script/@data-config")))
			json = JSON.ObjectFromURL(html.xpath("//script/@data-config")[0])
			#Log("JSON: " + str(json))
			manifest = json['src']
			#Log("Manifest: " + str(manifest))
			content = HTTP.Request(manifest, headers = {'Accept': 'text/html'}).content
			content = content.replace('\n','').replace('	','')
			#Log("Content: " + str(content))
			baseurl = re.search(r'>http(.*?)<', content) #<([baseURL]+)\b[^>]*>(.*?)<\/baseURL>
			#Log ('BaseURL: ' + baseurl.group())
			baseurl = re.sub(r'(<|>)', "", baseurl.group())
			#Log ('BaseURL: ' + baseurl)
			mediaurl = re.search(r'url="(.*?)\?', content)
			#Log ('MediaURL: ' + mediaurl.group())
			mediaurl = re.sub(r'(url|=|\?|")', "", mediaurl.group())
			#Log ('MediaURL: ' + mediaurl)
			url = baseurl + "/" + mediaurl
			Log("URL: " + url)

	thumb = GetThumb(html)

	return url, thumb

####################################################################################################

def GetLetwatchusHD(html):
	items = html.xpath("//div[@class='content']//b[contains(font/text(),'Letwatch')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'Letwatch')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'Letwatch')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	if len(items) == 0:
		items = html.xpath("//div[@class='content hasad']//b[contains(font[@color='Red']//text(), 'Letwatch')]//following-sibling::a")
	return items

####################################################################################################

def GetLetwatchusDVD(html):
	items = html.xpath("//div[@class='content']//b[contains(font/text(),'Letwatch DVD')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'Letwatch DVD')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'Letwatch DVD')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	if len(items) == 0:
		items = html.xpath("//div[@class='content hasad']//b[contains(font[@color='Red']//text(), 'Letwatch DVD')]//following-sibling::a")
	return items
####################################################################################################

def GetDailymotion(html):
	items = html.xpath("//div[@class='content']//b[contains(font/text(),'DailyMotion')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'DailyMotion')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'DailyMotion')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	return items

####################################################################################################

def GetDailymotionHD(html):
	items = html.xpath("//div[@class='content']//b[contains(font/text(),'Dailymotion 720p')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'Dailymotion 720p')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'Dailymotion 720p')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	if len(items) == 0:
		items = html.xpath("//div[@class='content hasad']//b[contains(font[@color='Red']//text(), 'Dailymotion 720p')]//following-sibling::a")
	return items

####################################################################################################

def GetDailymotionDVD(html):
	items = html.xpath("//div[@class='content hasad']//b[contains(font[@color='Red']//text(), 'Dailymotion DVD')]//following-sibling::a")
	if len(items) == 0:
		items = html.xpath("//div[@class='content']//b[contains(font/text(),'Dailymotion DVD')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'Dailymotion DVD')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'Dailymotion DVD')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	return items
	
####################################################################################################

def GetDailymotionSD(html):
	items = html.xpath("//div[@class='content']//font[contains(./text(),'Dailymotion Links')]/following-sibling::a[count(. | //font[count(//font[contains(./text(),'Dailymotion Links')]/preceding-sibling::font)+2]/preceding-sibling::a) = count(//font[count(//font[contains(./text(),'Dailymotion Links')]/preceding-sibling::font)+2]/preceding-sibling::a)]")
	
	if len(items) == 0:
		items = html.xpath("//div[@class='content']//b[contains(./font/text(),'Dailymotion Links')]/following-sibling::a[count(. | //b[count(//b[contains(./font/text(),'Dailymotion Links')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(./font/text(),'Dailymotion Links')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	
	return items
	
####################################################################################################

def GetFlashPlayer(html):
	items = html.xpath("//div[@class='content']//b[contains(font/text(),'Flash Player')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'Flash Player')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'Flash Player')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	return items

####################################################################################################

def GetFlashPlayerHD(html):
	items = html.xpath("//div[@class='content']//b[contains(font/text(),'Flash Player 720p') or contains(font/text(),'Flash 720p')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'Flash Player 720p') or contains(font/text(),'Flash 720p')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'Flash Player 720p') or contains(font/text(),'Flash 720p')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	return items

####################################################################################################

def GetFlashPlayerDVD(html):
	items = html.xpath("//div[@class='content']//b[contains(font/text(),'Flash Player DVD') or contains(font/text(),'Flash DVD')]/following-sibling::a[count(. | //b[count(//b[contains(font/text(),'Flash Player DVD') or contains(font/text(),'Flash DVD')]/preceding-sibling::b)+2]/preceding-sibling::a) = count(//b[count(//b[contains(font/text(),'Flash Player DVD') or contains(font/text(),'Flash DVD')]/preceding-sibling::b)+2]/preceding-sibling::a)]")
	return items

####################################################################################################

def GetMoviePostDate(html):
	# Get date
	date = html.xpath("//span[@class='date']/text()")[0]
	date = date.strip().replace(',','',1)
	Log ("html date: " + str(date))
	# strip date to struct
	if date == 'Today':
		date = time.strftime('%Y%m%d', time.gmtime())
		Log ("today: " + str(date))
	elif date == 'Yesterday':
		date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
		Log ('yesterday: ' + str(date))
	else:
		date = time.strptime(date, '%m-%d-%Y')
		date = time.strftime('%Y%m%d', date)
	#Log ('Date: ' + str(date))
	return date

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
@route(PREFIX + '/desirulez/createvideoobject')
def CreateVideoObject(url, title, thumb, summary='', originally_available_at='', include_container=False):
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
			summary=summary,
			thumb=thumb,
			originally_available_at=originally_available_at,
			include_container=True
		),
		rating_key = url,
		title = title,
		summary=summary,
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

@indirect
def PlayVideo(url=None, fmt=None, **kwargs):

	if not url or not fmt:
		raise Ex.MediaNotAvailable

	try:
		data = HTTP.Request(url).content
		if not data[0:1] == '{':
			raise Ex.MediaNotAvailable
	except:
		raise Ex.MediaNotAvailable

	video = JSON.ObjectFromString(data)
	video_url = None

	if fmt == 'hd':
		if 'stream_h264_hd_url' in video:
			video_url = video['stream_h264_hd_url']
		elif 'stream_h264_url' in video:
			video_url = video['stream_h264_url']
		elif 'stream_h264_sd_url' in video:
			video_url = video['stream_h264_sd_url']

	if fmt == 'sd' or video_url is None:
		if 'stream_h264_url' in video:
			video_url = video['stream_h264_url']
		elif 'stream_h264_sd_url' in video:
			video_url = video['stream_h264_sd_url']
		else:
			raise Ex.MediaNotAvailable

	return IndirectResponse(VideoClipObject, key=video_url)