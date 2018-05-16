from selenium import webdriver;
from selenium.webdriver.common.keys import Keys;
from selenium.webdriver.common.by import By;
from selenium.webdriver.support.ui import WebDriverWait;
from selenium.webdriver.support import expected_conditions as EC;
from selenium.common.exceptions import TimeoutException;
from selenium.common.exceptions import WebDriverException;
import common;
import time;
import math;
import datetime;
import platform;

class StaticScroller:
	def __init__(self, expected, xpath):
		self.expected = expected;
		self.xpath = xpath;

	def __call__(self, driver):
		driver.execute_script("window.scrollTo(0," + str(self.expected + 1) + ")");
		cc = int(math.floor(driver.execute_script("return window.pageYOffset")));
		ce = int(math.floor(self.expected));
		return cc < ce and len(driver.find_elements_by_xpath(self.xpath)) > 0;

def determine_exec():
	os = platform.platform().lower();
	arc = platform.machine().lower();
	if os.find("windows") != -1:
		if arc == "i386" or arc == "i686":
			return "geckodriver/geckodriver-win-32";
		else:
			return "geckodriver/geckodriver-win-64";
	elif os.find("linux") != -1:
		if arc == "i386" or arc == "i686":
			return "geckodriver/geckodriver-linux-32";
		else:
			return "geckodriver/geckodriver-linux-64";
	elif os.find("mac") != -1:
		return "geckodriver/geckodriver-mac";
	else:
		return None;

def force_visit(driver, url):
	try:
		driver.set_page_load_timeout(10);
		driver.get(url);
	except (WebDriverException, TimeoutException) as e:
		print("Reloading");

def get_element(driver, bytype, key):
	wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((bytype, key)));
	return driver.find_element(bytype, key);

def get_elements(driver, bytype, key):
	wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((bytype, key)));
	return driver.find_elements(bytype, key);

def scroll_to_bottom(driver):
	continuation_xpath = "//div[@id='continuations']/yt-next-continuation";
	while len(driver.find_elements_by_xpath(continuation_xpath)) > 0:
		current_offset = driver.execute_script("return window.pageYOffset") + 1000;
		driver.execute_script("window.scrollTo(0," + str(current_offset) + ")");
		try:
			wait = WebDriverWait(driver, 7).until_not(StaticScroller(current_offset, continuation_xpath));
		except TimeoutException:
			return False;
	return True;

def visit_channel(driver, channel_name):
	driver.get(common.URL);
	searchBox = driver.find_element_by_name('search_query');
	searchBox.send_keys(channel_name);
	searchBox.send_keys(Keys.RETURN);
	videosPage = False;
	while videosPage == False:
		try:
			wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "channel-title")));
			videosPage = True;
		except TimeoutException:
			print("Bad Internet or Username does not exist");
			driver.close();
	channelTitle = driver.find_element_by_id("channel-title");
	channelTitle.click();

def open_channel_tab(driver, tabname):
	try:
		wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tabsContent")));
	except TimeoutException:
		print("Reloading...");
		driver.get(driver.current_url);
	tabs = driver.find_elements_by_tag_name("paper-tab");
	videoIndex = -1;
	i = 0;
	for tab in tabs:
		if tab.text == tabname:
			videoIndex = i;
			break;
		i = i + 1;
	tabs[videoIndex].click();

def scan_videos_link(driver, url):
	while True:
		force_visit(driver, url);
		if scroll_to_bottom(driver) == True:
			break;
	videos = driver.find_elements_by_xpath("//h3/a[@id='video-title']");
	channel_name = driver.find_element_by_xpath("//h1[@id='channel-title-container']/span").text;
	eAuthor = driver.find_elements_by_xpath("//div[@id='metadata']/div[@id='byline-container']/yt-formatted-string/a");
	links = [];
	print("Collecting url...");
	for video in videos:
		title = video.text;
		link = video.get_attribute("href");
		if len(eAuthor) > 0:
			true_author = eAuthor[0].text == channel_name;
		else:
			true_author = True;
		if len(title) > 0 and len(link) > 0 and true_author:
			links.append(link);
			print("Appending " + title + " " + link);
	return links;

def collect_videos_link(driver):
	open_channel_tab(driver, "VIDEOS");

	category_xpath = "//div[@id='primary-items']/yt-dropdown-menu/paper-menu-button/iron-dropdown[@id='dropdown']/div/div/paper-listbox";

	eLinks = get_elements(driver, By.XPATH, category_xpath + "/a");
	divs = get_elements(driver, By.XPATH, category_xpath + "/a/paper-item/paper-item-body/div[contains(@class, 'item')]");

	if len(eLinks) > 1:
		categoryLinks = [];
		for index in range(0, len(eLinks)):
			name = divs[index].get_attribute("innerText");
			link = eLinks[index].get_attribute("href");
			if name != "All videos":
				print("Appending category " + name);
				categoryLinks.append(link);
		categoryLinks = list(set(categoryLinks));
	else:
		categoryLinks = [eLinks[0].get_attribute("href")];
	
	print("Found " + str(len(categoryLinks)) + " categories... ");

	videoLinks = [];
	for link in categoryLinks:
		print("Collecting links from " + link);
		videoLinks.extend(scan_videos_link(driver, link));

	return list(set(videoLinks));

def get_channel_start_date(driver):
	open_channel_tab(driver, "ABOUT");

	date_xpath = "//div[@id='right-column']/yt-formatted-string[contains(@class, 'ytd-channel-about-metadata-renderer')]";

	eDate = get_elements(driver, By.XPATH, date_xpath);

	str = eDate[1].text.split(" ");
	day = common.toInt(str[2]);
	month = common.get_month(str[1]);
	year = str[3];

	return datetime.date(int(year), month, day);

def gather_channel_data(channel_name, videos=False, join_date=False):
	profile = webdriver.FirefoxProfile();
	profile.set_preference("intl.accept_languages", "en-us");
	executable_path = determine_exec();
	if executable_path == None:
		print("Cannot determine operating system");
		try:
			driver = webdriver.Firefox();
		except Exception:
			print("Cannot find geckodriver executable in PATH");
	else:
		driver = webdriver.Firefox(executable_path=executable_path, firefox_profile=profile);
	visit_channel(driver, channel_name);
	url = driver.current_url;

	res = {
		"videos": None,
		"date": None
	};

	if videos == True:
		videoLinks = collect_videos_link(driver);
		res["videos"] = videoLinks;
		force_visit(driver, url);
	if join_date == True:
		date = get_channel_start_date(driver);
		res["date"] = date;

	driver.close();
	return res;

def gather_video_data(driver, url):
	try:
		driver.set_page_load_timeout(10);
		driver.get(url);
		try:
			title_xpath = "//div[@id='container']/h1[contains(@class, 'title')]/yt-formatted-string";
			view_xpath = "//div[@id='count']/yt-view-count-renderer/span[contains(@class, 'view-count')]";
			sentiment_xpath = "//div[@id='menu']/ytd-menu-renderer/div[@id='top-level-buttons']/ytd-toggle-button-renderer/a/yt-formatted-string";
			
			title = get_element(driver, By.XPATH, title_xpath).text;
			sview = get_element(driver, By.XPATH, view_xpath).text.split(" ");
			sentiments = get_elements(driver, By.XPATH, sentiment_xpath);

			view = common.toInt(sview[0]);
			for sentiment in sentiments:
				label = sentiment.get_attribute("aria-label").split(" ");
				if label[1] == "likes":
					like = common.toInt(label[0]);
				else:
					dislike = common.toInt(label[0]);

			return {
				"title": title,
				"views": view,
				"likes": like,
				"dislikes": dislike
			};

		except TimeoutException:
			return None;
	except (WebDriverException, TimeoutException) as e:
		return None;

def scrape(links):
	driver = webdriver.Firefox();
	print("Visiting " + common.readable(len(links)) + " videos...");
	count = 1;
	sum_view = 0;
	sum_like = 0;
	sum_dislike = 0;
	most = {
		"views": [],
		"rviews": [],
		"likes": [],
		"dislikes": []
	};

	time_start = time.time();
	while count <= len(links):
		url = links[count-1];
		print("Visit page " + str(count) + " " + url);
		res = gather_video_data(driver, url);
		if res == None:
			print("Reloading");
		else:
			common.print_video_data(res);
			common.decide_most_list(most, res);
			sum_view += res["views"];
			sum_like += res["likes"];
			sum_dislike += res["dislikes"];
			count += 1;
	duration = int(round(time.time() - time_start));

	driver.close();

	return {
		"count": count-1,
		"views": sum_view,
		"likes": sum_like,
		"dislikes": sum_dislike,
		"duration": duration,
		"most_viewed": most["views"],
		"least_viewed": most["rviews"],
		"most_liked": most["likes"],
		"most_disliked": most["dislikes"]
	};