from selenium import webdriver;
import preparator as prep;
import worker as worker;
import common;
import math;
import datetime;
import time;
import sys;

def print_data(name, data, day_diff):
	print("Data for '" + name + "'");
	sum_video_length = 0;
	tmin_video_length = None;
	tmax_video_length = None;
	for length in channel_data["videos_data"]["lengths"]:
		strtime = length.split(":");
		fmt = "%S";
		if len(strtime) > 1:
			fmt = "%M:" + fmt;
		if len(strtime) > 2:
			fmt = "%H:" + fmt; 
		strp = time.strptime(length, fmt);
		total_seconds = datetime.timedelta(hours=strp.tm_hour, minutes=strp.tm_min, seconds=strp.tm_sec).total_seconds();
		if tmin_video_length == None or tmin_video_length > total_seconds:
			tmin_video_length = total_seconds;
		if tmax_video_length == None or tmax_video_length < total_seconds:
			tmax_video_length = total_seconds;
		sum_video_length += total_seconds;
	average_likes = math.floor(data["likes"]/data["count"]);
	average_dislikes = math.floor(data["dislikes"]/data["count"]);
	average_views = math.floor(data["views"]/day_diff);
	average_length = str(datetime.timedelta(seconds=math.floor(sum_video_length/data["count"])));
	min_length = str(datetime.timedelta(seconds=tmin_video_length));
	max_length = str(datetime.timedelta(seconds=tmax_video_length));
	common.print_videos_data("Most Viewed Videos", data["most_viewed"]);
	common.print_videos_data("Least Viewed Videos", data["least_viewed"]);
	common.print_videos_data("Most Liked Videos", data["most_liked"]);
	common.print_videos_data("Most Disliked Videos", data["most_disliked"]);
	if 'most_vpd' in data and len(data['most_vpd']) > 0:
		common.print_videos_data("Most Viewed Video Per Day", data["most_vpd"]);
	print("Total Videos        : " + common.readable(data["count"]));
	print("Total Views         : " + common.readable(data["views"]));
	print("Total Likes         : " + common.readable(data["likes"]));
	print("Total Dislikes      : " + common.readable(data["dislikes"]));
	print("Likes per Video     : " + common.readable(average_likes));
	print("Dislikes per Video  : " + common.readable(average_dislikes));
	print("Avg Video Length    : " + average_length);
	print("Min Video Length    : " + min_length);
	print("Max Video Length    : " + max_length);
	print("Join Date           : " + str(channel_data["date"]) + ", " + str(day_diff) + " days ago");
	print("Views per Day       : " + common.readable(average_views));
	print("======");
	print("");

def manage_data_gathering(channel_name):
	args = sys.argv;
	if len(args) > 1:
		if len(args) > 2 and args[2] == "gui":
			return prep.gather_channel_data(channel_name, args[1], False);
		else:
			return prep.gather_channel_data(channel_name, args[1], True);
	else:
		return prep.gather_channel_data(channel_name, None, True);

def manage_data_scraping(videos_link, highlight=[]):
	return worker.scrape(videos_link, 10, channel_data["date"], highlight);

def ask_highlight():
	print("Any hightlighted keywords? If yes, seperate each key with comma. Ex: horror game, very funny, .....");
	s = input();
	return s.split(",");

channel_name = input("Channel Name: ");
highlight = ask_highlight();
time_start = time.time();
channel_data = manage_data_gathering(channel_name);
collect_duration = int(round(time.time() - time_start));
data = manage_data_scraping(channel_data["videos_data"]["links"], highlight);
day_diff = (datetime.date.today() - channel_data["date"]).days;

for i in range(0, len(highlight)):
	print_data(highlight[i], data["highlight"][highlight[i]], day_diff);
print_data("Main", data["main"], day_diff);

one_mile = 1000;
dollar_to_rupiah = 10000;
average_views = math.floor(data["main"]["views"]/day_diff);
print("Visit Duration " + str(data["duration"]) + " seconds");
print("Total Duration " + str(data["duration"] + collect_duration) + " seconds");
print("Avg Upload Interval : " + common.readable(data["avg_upload_interval"]) + " days");
print("# Estimated Income from Youtube");
print("# Assumed CPM is 1$");
print("# Using adsense after x time join Youtube:");
if (day_diff - (6 * 30)) > 0:
	total_income = math.floor((day_diff - 6*30) * average_views * dollar_to_rupiah / one_mile);
	print("# - 6 months  : Rp" + common.readable(total_income));
if (day_diff - 365) > 0:
	total_income = math.floor((day_diff - 365) * average_views * dollar_to_rupiah / one_mile);
	print("# - 12 months : Rp" + common.readable(total_income));
if (day_diff - (18 * 30) > 0):
	total_income = math.floor((day_diff - 18*30) * average_views * dollar_to_rupiah / one_mile);
	print("# - 18 months : Rp" + common.readable(total_income));
print("# Income per Month: " + common.readable(math.floor(average_views * 30 * dollar_to_rupiah / one_mile)));
print("# Estimated Income from Youtube (with another calculation)");
print("# Using adsense after x time join Youtube:");
if (day_diff - (6 * 30)) > 0:
	total_income = math.floor((day_diff - 6*30) * average_views * dollar_to_rupiah / one_mile);
	per_month = math.floor(total_income/day_diff*30);
	true_income = math.floor(total_income/day_diff) * (day_diff - 6 * 30);
	print("# - 6 months  : Rp" + common.readable(true_income) + " Rp" + common.readable(per_month) + "/month");
if (day_diff - 365) > 0:
	total_income = math.floor((day_diff - 365) * average_views * dollar_to_rupiah / one_mile);
	per_month = math.floor(total_income/day_diff*30);
	true_income = math.floor(total_income/day_diff) * (day_diff - 365);
	print("# - 12 months : Rp" + common.readable(true_income) + " Rp" + common.readable(per_month) + "/month");
if (day_diff - (18 * 30) > 0):
	total_income = math.floor((day_diff - 18*30) * average_views * dollar_to_rupiah / one_mile);
	per_month = math.floor(total_income/day_diff*30);
	true_income = math.floor(total_income/day_diff) * (day_diff - (18 * 30));
	print("# - 18 months : Rp" + common.readable(true_income) + " Rp" + common.readable(per_month) + "/month");
