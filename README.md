### Hello, World!
This is web robot to crawl data from a youtube __channel__. Develop with Python using three main libraries:
- [Requests](https://github.com/requests/requests) 
- [Selenium](http://selenium-python.readthedocs.io) 
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc)

### What kind of data you can get?
- Total Views
- Total Likes
- Total Dislikes
- Likes per Video
- Dislike per Video
- Views per Day (VPD)
- 3 Most Viewed
- 3 Least Viewed
- 3 Most Liked
- 3 Most Disliked
- 3 Highest VPD
- Total Income Estimation
- Income per Month Estimation

### It's Fun
You can try it. You just need to clone or download all the files. Make sure you have Python 3 already installed (not tested for Python 2), and also make sure [Selenium](http://selenium-python.readthedocs.io/installation.html) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) is available, then execute "*python main.py*" (or "*python3 main.py*" if you use Python in Linux). Give the channel name, then relax and wait until that robot finish crawling. Oh almost forget, this robot use Firefox Browser for some activities, so make sure you have Firefox installed (not already developed to support other browsers).

### Planned to Develop
1. Features:
	- Collect data for spesific keywords found in video's title.
2. Store every result to SQL database
3. Visualize the collected data

### Any Other Idea?
I am still exploring about web scrapping. If you see something not good inside the codes and have better idea (maybe like "Why the robot should use Browser instead of Request?"), I'll be happy to hear another idea. Also, if you have thirst of curiosity about another youtube channel's data, I'll be fascinated to know that. You don't want to tell me? Alright, let me see your pull request.
