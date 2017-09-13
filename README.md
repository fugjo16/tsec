# tsec
stock crawler & analyzer

# files
*crawl.py: 
	Download stock prices data & found data.

*post_process.py: 
	Sequence raw data, and get technical values.

*analyze.py: 
	Check info of stocks. 
	If match conditions in Analyzer, then show message on command line window.

# required python tools
requests==2.7.0
lxml==3.5.0
numpy==1.13.1
pandas==0.20.3