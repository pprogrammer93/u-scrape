from selenium import webdriver;
from bs4 import BeautifulSoup;
import mod_selenium as visible;
import mod_silent as silent;
import common;
import math;
import datetime;
import sys;
import requests;

# headers = {"accept-language": "en-us"};
# page = requests.get("https://www.youtube.com/channel/UCJeH7gl6PbDVV4DTldIOPOA/about", headers=headers);
# parsed = BeautifulSoup(page.content, "html.parser");
# stats = parsed.select('ul#browse-items-primary li div.about-metadata-container div.about-stats span.about-stat');

# for stat in stats:
# 	if stat.get_text().find("Joined", 0, 6) != -1:
# 		print(stat.get_text());

# page = requests.get("https://www.youtube.com/results?search_query=" + "evanescence");
# parsed = BeautifulSoup(page.content, "html.parser");
# urls = parsed.select('div.yt-lockup-content h3.yt-lockup-title a');

# for url in urls:
# 	ls = 1;
# 	le = url["href"].find("/", 1);
# 	href = url["href"][ls:le];
# 	if href=="user" or href=="channel":
# 		print("http://www.youtube.com" + url["href"]);

# page = requests.get("https://www.youtube.com/channel/UCJeH7gl6PbDVV4DTldIOPOA/videos");
# parsed = BeautifulSoup(page.content, "html.parser");
# menuitem = parsed.select('ul#browse-items-primary li.branded-page-v2-subnav-container ul[role="menu"] li[role="menuitem"] span');

# for item in menuitem:
# 	print("Appending category " + item.get_text());
# 	print("https://www.youtube.com" + item["href"]);

channel_name = input("Channel Name: ");
args = sys.argv;
if len(args) > 1:
	if len(args) > 2 and args[2] == "silent":
		channel_data = visible.gather_channel_data(channel_name, args[1], True);
	else:
		channel_data = visible.gather_channel_data(channel_name, args[1]);
else:
	channel_data = visible.gather_channel_data(channel_name, None);

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
