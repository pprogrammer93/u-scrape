from bs4 import BeautifulSoup;
from threading import Lock, Event, Thread;
from queue import LifoQueue;
from requests.exceptions import ConnectionError, ReadTimeout
import requests;
import time;
import common;
import math;
import datetime;

class ResultPool(Thread):
	def __init__(self, join_date):
		Thread.__init__(self);
		self.lock = Lock();
		self.event = Event();
		self.queue = LifoQueue();
		self.running = False;
		self.finish = Event();
		self.finish.set();
		self.upload_dates = [];
		self.join_date = join_date;
		self.result = {
			"count": 0,
			"views": 0,
			"likes": 0,
			"dislikes": 0,
			"duration": 0,
			"most": {
				"views": [],
				"rviews": [],
				"likes": [],
				"dislikes": [],
				"vpd": []	
			}
		};
	def add(self, data, link):
		self.lock.acquire();
		self.queue.put({"data": data, "link": link});
		self.event.set();
		self.lock.release();
	def result_report(self, link, data):
		print(str(self.result["count"] + 1) + ". Result from " + link);
		common.print_video_data(data);
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
				self.result_report(item["link"], item["data"]);
				common.decide_most_list(self.result["most"], item["data"]);
				self.result["count"] += 1;
				self.result["views"] += item["data"]["views"];
				self.result["likes"] += item["data"]["likes"];
				self.result["dislikes"] += item["data"]["dislikes"];
				self.upload_dates.append(item["data"]["upload_date"]);
			else:
				self.event.clear();
		self.result["duration"] = int(round(time.time() - time_start));
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
		return {
			"count": self.result["count"],
			"views": self.result["views"],
			"likes": self.result["likes"],
			"dislikes": self.result["dislikes"],
			"duration": self.result["duration"],
			"avg_upload_interval": self.calculate_upload_interval(),
			"most_viewed": self.result["most"]["views"],
			"least_viewed": self.result["most"]["rviews"],
			"most_liked": self.result["most"]["likes"],
			"most_disliked": self.result["most"]["dislikes"],
			"most_vpd": self.result["most"]["vpd"]
		};

class Worker(Thread):
	def __init__(self, links, pool):
		Thread.__init__(self);
		self.pool = pool;
		self.links = links;
	def extract_data(self, url):
		headers = {"accept-language": "en-us"};
		requestOK = False;
		while requestOK == False:
			try:
				page = requests.get(url, headers=headers);
				requestOK = True;
			except (ConnectionError, ReadTimeout):
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

def scrape(links, rps, join_date=None):
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
	pool = ResultPool(join_date);
	workers = [];
	quota = calculate_quota(len(links), rps);
	left = 0;
	right = 0;
	for i in range(0, rps):
		print("Setting up " + str(i + 1) + " worker...");
		right = left + quota[i]; 
		qLinks = links[left:right];
		worker = Worker(qLinks, pool);
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