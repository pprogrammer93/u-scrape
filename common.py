import math;

URL = "http://youtube.com";

def readable(x):
	digit = 0;
	i = x;

	sint = str(x);
	while i > 1:
		i /= 10;
		digit += 1;
	dot = int(math.floor((digit - 1) / 3));
	for i in range(0, dot):
		pos = i + (3 * (i + 1));
		rpos = len(sint) - pos;
		sint = sint[:rpos] + "." + sint[rpos:];
	return sint;

def toInt(str, splitter=","):
	ls = str.split(splitter);
	sint = "";
	for s in ls:
		sint += s;
	try:
		integer = int(sint);
	except ValueError:
		integer = 0;
	return integer;

def get_month(month):
	month_list = {
		"Jan": 1,
		"Feb": 2,
		"Mar": 3,
		"Apr": 4,
		"May": 5,
		"Jun": 6,
		"Jul": 7,
		"Aug": 8,
		"Sep": 9,
		"Oct": 10,
		"Nov": 11,
		"Dec": 12
	};

	return month_list[month];

def print_video_data(data):
	print("Title    : " + data["title"]);
	print("Views    : " + readable(data["views"]));
	print("Likes    : " + readable(data["likes"]));
	print("Dislikes : " + readable(data["dislikes"]));
	if "vpd" in data:
		print("VPD      : " + readable(data["vpd"]));

def print_videos_data(mList):
	for video in mList:
		print_video_data(video);
		print(".");

def compare(v1, v2, key):
	if v1[key] < v2[key]:
		return -1;
	elif v1[key] == v2[key]:
		return 0;
	else:
		return 1;

def add_if_most(mList, video, limit, compare_type, compare_key):
	if len(mList) < limit:
		mList.append(video);
	else:
		index = limit-1;
		while index >= 0:
			comp = compare(mList[index], video, compare_key);
			if comp == compare_type:
				break;
			else:
				index -= 1;
		if index < limit-1:
			mList[limit-1] = video;

def decide_most_list(most, video, limit=3):
	views = most["views"];
	rviews = most["rviews"];
	likes = most["likes"];
	dislikes = most["dislikes"];

	if 'vpd' in most and 'vpd' in video:
		vpd = most["vpd"];
		add_if_most(vpd, video, limit, 1, "vpd");
		most["vpd"] = sorted(vpd, key=lambda vid: vid["vpd"], reverse=True);

	add_if_most(views, video, limit, 1, "views");
	add_if_most(rviews, video, limit, -1, "views");
	add_if_most(likes, video, limit, 1, "likes");
	add_if_most(dislikes, video, limit, 1, "dislikes");

	most["views"] = sorted(views, key=lambda vid: vid["views"], reverse=True);
	most["rviews"] = sorted(rviews, key=lambda vid: vid["views"]);
	most["likes"] = sorted(likes, key=lambda vid: vid["likes"], reverse=True);
	most["dislikes"] = sorted(dislikes, key=lambda vid: vid["dislikes"], reverse=True);