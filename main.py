from selenium import webdriver;
import mod_selenium as visible;
import mod_silent as silent;
import common;
import math;
import datetime;
import sys;

channel_name = input("Channel Name: ");
args = sys.argv;
if len(args) > 1:
	channel_data = visible.gather_channel_data(channel_name, args[1], videos=True, join_date=True);
else:
	channel_data = visible.gather_channel_data(channel_name, None, videos=True, join_date=True);

links = channel_data["videos"];
join_date = channel_data["date"];
date_diff = datetime.date.today() - join_date;
day_diff = date_diff.days;
data = silent.scrape(links, 10);

average_likes = int(math.floor(data["likes"]/data["count"]));
average_dislikes = int(math.floor(data["dislikes"]/data["count"]));
average_views = int(math.floor(data["views"]/day_diff));

print("Total Videos      : " + common.readable(data["count"]));
print("Total Views       : " + common.readable(data["views"]));
print("Total Likes       : " + common.readable(data["likes"]));
print("Total Dislikes    : " + common.readable(data["dislikes"]));
print("Likes per Video    : " + common.readable(average_likes));
print("Dislikes per Video : " + common.readable(average_dislikes));
print("Visit Duration " + str(data["duration"]) + " seconds");

print("# Most Viewed Videos:");
common.print_videos_data(data["most_viewed"]);
print("# Least Viewed Videos:");
common.print_videos_data(data["least_viewed"]);
print("# Most Liked Videos:");
common.print_videos_data(data["most_liked"]);
print("# Most Disliked Videos:");
common.print_videos_data(data["most_disliked"]);
if 'most_vpd' in data and len(data['most_vpd']) > 0:
	print("# Most Viewed Video Per Day");
	common.print_videos_data(data["most_vpd"]);

one_mile = 1000;
dollar_to_rupiah = 10000;

print("Join Date     : " + str(join_date));
print("Views per Day : " + common.readable(average_views));
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
print("# Income per Month: " + common.readable(int(math.floor(average_views * 30 * dollar_to_rupiah / one_mile))));
