from bs4 import BeautifulSoup;
from threading import Lock, Event, Thread;
from queue import LifoQueue;
from requests.exceptions import ConnectionError, ReadTimeout, Timeout
import requests;
import time;
import common;
import math;
import datetime;

class MostList:
	def __init__(self):
		self.views = [];
		self.rviews = [];
		self.likes = [];
		self.dislikes = [];
		self.vpd = [];
	def compare(self, v1, v2, key):
		if v1[key] < v2[key]:
			return -1;
		elif v1[key] == v2[key]:
			return 0;
		else:
			return 1;
	def add_if_most(self, video, limit, compare_type, compare_key):
		if compare_key == "vpd":
			mList = self.vpd;
		elif compare_key == "views":
			if compare_type == 1:
				mList = self.views;
			else:
				mList = self.rviews;
		elif compare_key == "likes":
			mList = self.likes;
		elif compare_key == "dislikes":
			mList = self.dislikes;
		if len(mList) < limit:
			mList.append(video);
		else:
			index = limit-1;
			while index >= 0:
				comp = self.compare(mList[index], video, compare_key);
				if comp == compare_type:
					break;
				else:
					index -= 1;
			if index < limit-1:
				mList[limit-1] = video;
	def decide_most_list(self, video, limit=3):
		views = self.views;
		rviews = self.rviews;
		likes = self.likes;
		dislikes = self.dislikes;
		vpd = self.vpd;

		self.add_if_most(video, limit, 1, "vpd");
		self.add_if_most(video, limit, 1, "views");
		self.add_if_most(video, limit, -1, "views");
		self.add_if_most(video, limit, 1, "likes");
		self.add_if_most(video, limit, 1, "dislikes");

		self.views = sorted(self.views, key=lambda vid: vid["views"], reverse=True);
		self.rviews = sorted(self.rviews, key=lambda vid: vid["views"]);
		self.likes = sorted(self.likes, key=lambda vid: vid["likes"], reverse=True);
		self.dislikes = sorted(self.dislikes, key=lambda vid: vid["dislikes"], reverse=True);
		self.vpd = sorted(self.vpd, key=lambda vid: vid["vpd"], reverse=True);

class Result:
	def __init__(self):
		self.count = 0;
		self.views = 0;
		self.likes = 0;
		self.dislikes = 0;
		self.upload_dates = [];
		self.most = MostList();
	def add(self, data):
		self.most.decide_most_list(data);
		self.count += 1;
		self.views += data["views"];
		self.likes += data["likes"];
		self.dislikes += data["dislikes"];
		self.upload_dates.append(data["upload_date"]);
	def finalize(self):
		return {
			"count": self.count,
			"views": self.views,
			"likes": self.likes,
			"dislikes": self.dislikes,
			"most_viewed": self.most.views,
			"least_viewed": self.most.rviews,
			"most_liked": self.most.likes,
			"most_disliked": self.most.dislikes,
			"most_vpd": self.most.vpd
		};

class ResultPool(Thread):
	def __init__(self, join_date, highlight=[]):
		Thread.__init__(self);
		self.lock = Lock();
		self.event = Event();
		self.queue = LifoQueue();
		self.running = False;
		self.finish = Event();
		self.finish.set();
		self.duration = 0;
		self.upload_dates = [];
		self.join_date = join_date;
		self.result = Result();
		self.highlight = highlight;
		self.h_lower = [];
		self.h_res = [];
		for i in range(0, len(highlight)):
			self.h_res.append(Result());
			self.h_lower.append(highlight[i].lower());
	def add(self, data, link):
		self.lock.acquire();
		self.queue.put({"data": data, "link": link});
		self.event.set();
		self.lock.release();
	def result_report(self, link, data):
		print(str(self.result.count + 1) + ". Result from " + link);
		common.print_video_data(data);
	def analyze(self, item):
		self.result_report(item["link"], item["data"]);
		self.upload_dates.append(item["data"]["upload_date"]);
		self.result.add(item["data"]);
		title = item["data"]["title"].lower();
		for i in range(0, len(self.highlight)):
			if title.find(self.h_lower[i]) != -1:
				self.h_res[i].add(item["data"]);
	def run(self):
		if self.finish.is_set() == False:
			raise RuntimeError("Unable to start running ResultPool.");
		self.running = True;
		self.finish.clear();
		time_start = time.time();
		while self.running == True or self.queue.empty() == False:
			self.event.wait();
			if self.queue.empty() == False:
				item = self.queue.get();
				self.analyze(item);
			else:
				self.event.clear();
		self.duration = int(round(time.time() - time_start));
		self.finish.set();
	def stop(self):
		self.running = False;
		self.event.set();
	def calculate_upload_interval(self):
		sorted(self.upload_dates);
		sum_interval = (self.upload_dates[0] - self.join_date).days;
		for i in range(1, len(self.upload_dates)):
			sum_interval += (self.upload_dates[i] - self.upload_dates[i-1]).days;
		return math.floor(sum_interval/(len(self.upload_dates)));
	def get_result(self):
		if self.running == True:
			raise RuntimeError("Unable to get result from running ResultPool. Call stop() first.");
		self.finish.wait();
		result = {
			"main": self.result.finalize(),
			"highlight": {},
			"duration": self.duration,
			"avg_upload_interval": self.calculate_upload_interval()
		};
		for i in range(0, len(self.highlight)):
			result["highlight"][self.highlight[i]] = self.h_res[i].finalize();
		return result;

class Worker(Thread):
	def __init__(self, links, pool, id):
		Thread.__init__(self);
		self.pool = pool;
		self.links = links;
		self.id = id;
	def extract_data(self, url):
		headers = {"accept-language": "en-us"};
		requestOK = False;
		while requestOK == False:
			try:
				page = requests.get(url, headers=headers, timeout=5.000);
				requestOK = True;
			except (ConnectionError, ReadTimeout, Timeout):
				print("Worker " + str(self.id) + " is reloading...");
				requestOK = False;
		parsed = BeautifulSoup(page.content, "html.parser");

		ldate = list(parsed.select("strong.watch-time-text"));
		lTitle = list(parsed.select("span.watch-title"));
		lView = list(parsed.select("div.watch-view-count"));
		lSentiment = list(parsed.select('button[data-position="bottomright"] span'));

		title = lTitle[0].get_text().strip();
		try:
			views = common.toInt(lView[0].get_text().strip().split(" ")[0], ",");
		except IndexError as err:
			print("Length of elements: ", len(lView));
			if len(lView) > 0:
				print(lView[0].get_text());
			print(err);
			return None;
		likes = common.toInt(lSentiment[0].get_text().strip(), ",");
		dislikes = common.toInt(lSentiment[2].get_text().strip(), ",");

		sdate = ldate[0].get_text().strip().split(" ");
		slen = len(sdate);
		upload_date = datetime.date(int(sdate[slen-1]), common.get_month(sdate[slen-3]), common.toInt(sdate[slen-2], ","));
		date_diff = datetime.date.today() - upload_date;
		if date_diff == 0:
			vpd = views;
		else:
			vpd = int(math.floor(views / date_diff.days));

		return {
			"title": title,
			"views": views,
			"likes": likes,
			"dislikes": dislikes,
			"vpd": vpd,
			"upload_date": upload_date 
		};
	def run(self):
		prev = 0;
		count = 0;
		failed = 0;
		while count < len(self.links):
			now = time.time();
			if (now - prev) > 0.0:
				url = self.links[count];
				res = self.extract_data(url);
				if res != None:
					self.pool.add(res, url);
					count += 1;
				else:
					self.links = self.links[:count] + self.links[(count+1):];
				prev = now;

def calculate_quota(ammount, divider):
	base = int(math.floor(ammount / divider));
	rem = ammount % divider;
	res = [];
	for i in range(0, divider):
		if rem != 0:
			res.append(base + 1);
			rem -= 1;
		else:
			res.append(base);
	return res;

def scrape(links, rps, join_date=None, highlight=[]):
	interval = 1/rps;
	prev = 0;
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

	print("Collecting data from " + str(len(links)) + " videos...");

	print("Setting up request...");
	pool = ResultPool(join_date, highlight);
	workers = [];
	quota = calculate_quota(len(links), rps);
	left = 0;
	right = 0;
	for i in range(0, rps):
		print("Setting up " + str(i + 1) + " worker...");
		right = left + quota[i]; 
		qLinks = links[left:right];
		worker = Worker(qLinks, pool, (i + 1));
		workers.append(worker);
		left = right;

	print("Starting...");
	pool.start();
	for worker in workers:
		worker.start();
	for worker in workers:
		worker.join();
	pool.stop();
	return pool.get_result();