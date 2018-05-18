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
- Average Upload Interval
- Minimum/Average/Maximum Video Length
- Views per Day (VPD)
- 3 Most Viewed
- 3 Least Viewed
- 3 Most Liked
- 3 Most Disliked
- 3 Highest VPD
- Total Income Estimation
- Income per Month Estimation

You can also hightlight some keywords from video's title to get seperate data from the overall data. It will be usefull in case some the video's author add the video's category at the title, so you can gather the data for certain category.

### It's Fun
You can try it. You just need to clone or download all the files. Make sure you have Python 3 already installed (not tested for Python 2), and also make sure [Selenium](http://selenium-python.readthedocs.io/installation.html) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) is available, then execute "*python main.py*" (or "*python3 main.py*" if you use Python in Linux). Give the channel name, then relax and wait until that robot finish crawling. Oh almost forget, this robot use Firefox Browser or Chrome Browser for some collecting video links, so make sure you have Firefox or Chrome installed.

### Available Arguments
By default, it will try to use Chrome if available, or it will use Firefox otherwise. By default it will run without GUI. You can choose manually which browser to use and whether you want to see the GUI (browser's window) or not by using these commands:
- python main.py chrome gui
- python main.py firefox gui

### Planned to Develop
1. Store every result to SQL database
2. Visualize the collected data

### Any Other Idea?
I am still exploring about web scrapping. If you see something not good inside the codes and have better idea, I'll be happy to hear another idea. Also, if you have thirst of curiosity about another youtube channel's data, I'll be fascinated to know that. You don't want to tell me? Alright, let me see your pull request.
