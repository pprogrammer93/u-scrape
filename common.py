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

def print_videos_data(most_type, mList):
	print("# " + most_type + ":");
	for video in mList:
		print_video_data(video);
		print(".");