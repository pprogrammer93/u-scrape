from selenium import webdriver;
from selenium.webdriver.common.keys import Keys;
from selenium.webdriver.common.by import By;
from selenium.webdriver.support.ui import WebDriverWait;
from selenium.webdriver.support import expected_conditions as EC;
from selenium.common.exceptions import TimeoutException;
from selenium.common.exceptions import WebDriverException;
from selenium.webdriver.chrome.options import Options;
from bs4 import BeautifulSoup;
import common;
import time;
import math;
import datetime;
import platform;
import requests;

class StaticScroller:
	def __init__(self, expected, xpath):
		self.expected = expected;
		self.xpath = xpath;

	def __call__(self, driver):
		driver.execute_script("window.scrollTo(0," + str(self.expected + 1) + ")");
		cc = int(math.floor(driver.execute_script("return window.pageYOffset")));
		ce = int(math.floor(self.expected));
		return cc < ce and len(driver.find_elements_by_xpath(self.xpath)) > 0;

def determine_exec(drivertype):
	if drivertype=="firefox":
		driver_uri = "geckodriver/geckodriver";
	elif drivertype=="chrome":
		driver_uri = "chromedriver/chromedriver";
	else:
		raise RuntimeError("Unknown driver type " + drivertype);
	os = platform.platform().lower();
	arc = platform.machine().lower();
	if os.find("windows") != -1:
		if arc == "i386" or arc == "i686":
			if drivertype=="chrome":
				return driver_uri + "-win";
			else:
				return driver_uri + "-win-32";
		else:
			if drivertype=="chrome":
				return driver_uri + "-win";
			else:
				return driver_uri + "-win-64";
	elif os.find("linux") != -1:
		if arc == "i386" or arc == "i686":
			if drivertype=="chrome":
				return driver_uri + "-linux";
			else:
				return driver_uri + "-linux-32";
		else:
			if drivertype=="chrome":
				return driver_uri + "-linux";
			else:
				return driver_uri + "-linux-64";
	elif os.find("mac") != -1:
		return driver_uri + "-mac";
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
	# searchBox.set_attribute("value", channel_name);
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

def collect_videos_link(driver, url, silent=False):
	if silent:
		headers = {"accept-language": "en-us"};
		page = requests.get(url + "/videos", headers=headers);
		parsed = BeautifulSoup(page.content, "html.parser");
		menuitem = parsed.select('ul#browse-items-primary li.branded-page-v2-subnav-container ul[role="menu"] li[role="menuitem"] span');

		categoryLinks = [];
		for item in menuitem:
			print("Appending category " + item.get_text());
			categoryLinks.append("https://www.youtube.com" + item["href"]);
	else:
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

def get_channel_start_date(driver, url, silent=False):
	datestr = None;
	if silent:
		headers = {"accept-language": "en-us"};
		page = requests.get(url + "/about", headers=headers);
		parsed = BeautifulSoup(page.content, "html.parser");
		stats = parsed.select('ul#browse-items-primary li div.about-metadata-container div.about-stats span.about-stat');
		for stat in stats:
			if stat.get_text().find("Joined", 0, 6) != -1:
				datestr = stat.get_text().split(" ");
	else:
		open_channel_tab(driver, "ABOUT");
		date_xpath = "//div[@id='right-column']/yt-formatted-string[contains(@class, 'ytd-channel-about-metadata-renderer')]";
		eDate = get_elements(driver, By.XPATH, date_xpath);
		datestr = eDate[1].text.split(" ");

	day = common.toInt(datestr[2]);
	month = common.get_month(datestr[1]);
	year = datestr[3];

	return datetime.date(int(year), month, day);

def get_chrome_driver(silent):
	options = Options();
	if silent:
		options.add_argument("--mute-audio");
		options.add_argument("--headless");
		options.add_argument("window-size=1366x768");
	options.add_argument("--lang=en-us");
	executable_path = determine_exec("chrome");
	if executable_path == None:
		print("Cannot determine operating system");
		try:
			return webdriver.chrome(chrome_options=options);
		except Exception:
			print("Cannot find chromedriver executable");
	else:
		return webdriver.Chrome(executable_path=executable_path, chrome_options=options);



def get_firefox_driver():
	profile = webdriver.FirefoxProfile();
	profile.set_preference("intl.accept_languages", "en-us");
	executable_path = determine_exec("firefox");
	if executable_path == None:
		print("Cannot determine operating system");
		try:
			return webdriver.Firefox(firefox_profile=profile);
		except Exception:
			print("Cannot find geckodriver executable");
	else:
		return webdriver.Firefox(executable_path=executable_path, firefox_profile=profile);

def get_channel_url(channel_name):
	page = requests.get("https://www.youtube.com/results?search_query=" + channel_name.replace(" ", "+"));
	parsed = BeautifulSoup(page.content, "html.parser");
	urls = parsed.select('div.yt-lockup-content h3.yt-lockup-title a');

	for url in urls:
		ls = 1;
		le = url["href"].find("/", 1);
		href = url["href"][ls:le];
		if href=="user" or href=="channel":
			return "http://www.youtube.com" + url["href"];
	return None;

def gather_channel_data(channel_name, browser=None, silent=False):
	if browser != None:
		if browser == "chrome":
			driver = get_chrome_driver(silent);
		elif browser == "firefox":
			driver = get_firefox_driver();
		else:
			raise RuntimeError("Unknown browser");
	else:
		try:
			driver = get_chrome_driver(silent);
		except Exception:
			try:
				driver = get_firefox_driver();
			except Exception as err:
				print("Cannot use any browser.");
				raise err;
	if silent:
		url = get_channel_url(channel_name);
		if url == None:
			print("Channel not found");
			return None;
	else:
		visit_channel(driver, channel_name);
		url = driver.current_url;

	res = {
		"videos": None,
		"date": None
	};

	date = get_channel_start_date(driver, url, silent);
	res["date"] = date;
	if silent==False:
		force_visit(driver, url);
	videoLinks = collect_videos_link(driver, url, silent);
	res["videos"] = videoLinks;

	driver.close();
	return res;