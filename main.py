from selenium import webdriver;
import preparator as prep;
import worker as worker;
import common;
import math;
import datetime;
import time;
import sys;

channel_name = input("Channel Name: ");
args = sys.argv;
if len(args) > 1:
	if len(args) > 2 and args[2] == "worker":
		time_start = time.time();
		channel_data = prep.gather_channel_data(channel_name, args[1], True);
	else:
		time_start = time.time();
		channel_data = prep.gather_channel_data(channel_name, args[1]);
else:
	time_start = time.time();
	channel_data = prep.gather_channel_data(channel_name, None);
collect_duration = int(round(time.time() - time_start));

day_diff = (datetime.date.today() - channel_data["date"]).days;
data = worker.scrape(channel_data["videos"], 10);

average_likes = math.floor(data["likes"]/data["count"]);
average_dislikes = math.floor(data["dislikes"]/data["count"]);
average_views = math.floor(data["views"]/day_diff);
one_mile = 1000;
dollar_to_rupiah = 10000;

print("Visit Duration " + str(data["duration"]) + " seconds");
print("Total Duration " + str(data["duration"] + collect_duration) + " seconds");

common.print_videos_data("Most Viewed Videos", data["most_viewed"]);
common.print_videos_data("Least Viewed Videos", data["least_viewed"]);
common.print_videos_data("Most Liked Videos", data["most_liked"]);
common.print_videos_data("Most Disliked Videos", data["most_disliked"]);
if 'most_vpd' in data and len(data['most_vpd']) > 0:
	common.print_videos_data("Most Viewed Video Per Day", data["most_vpd"]);

print("Total Videos       : " + common.readable(data["count"]));
print("Total Views        : " + common.readable(data["views"]));
print("Total Likes        : " + common.readable(data["likes"]));
print("Total Dislikes     : " + common.readable(data["dislikes"]));
print("Likes per Video    : " + common.readable(average_likes));
print("Dislikes per Video : " + common.readable(average_dislikes));
print("Join Date          : " + str(channel_data["date"]));
print("Views per Day      : " + common.readable(average_views));
print("# Estimated Income from Youtube");
print("# Assumed CPM is 1$");
print("# Using adsense after x time join Youtube:");
if (day_diff - (6 * 30)) > 0:
	total_income = int(math.floor((day_diff - 6*30) * average_views * dollar_to_rupiah / one_mile));
	print("# - 6 months  : Rp" + common.readable(total_income));
if (day_diff - 365) > 0:
	total_income = int(math.floor((day_diff - 365) * average_views * dollar_to_rupiah / one_mile));
	print("# - 12 months : Rp" + common.readable(total_income));
if (day_diff - (18 * 30) > 0):
	total_income = int(math.floor((day_diff - 18*30) * average_views * dollar_to_rupiah / one_mile));
	print("# - 18 months : Rp" + common.readable(total_income));
print("# Income per Month: " + common.readable(math.floor(average_views * 30 * dollar_to_rupiah / one_mile)));
