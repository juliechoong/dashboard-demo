# Dashboard Demo #
This project demonstrates how to build your own analytics dashboard using web-scraped data.

### Dependencies ###
- Python 3.9.5
- [iTunes Store App Review Scraper](https://github.com/mvoran/itunes_app_review_scraper)
- [BERTopic](https://github.com/MaartenGr/BERTopic)
- [Plotly Dash](https://github.com/plotly/dash)

### Installation ###
1. Clone this project.
2. Create and activate virtual enrinvonment.
3. Go to cloned folder (where `requirements.txt` is) and install dependencies: `pip install -r requirements.txt --user`
4. Download Spacy's package: `python -m spacy download en_core_web_sm`
5. Run the scripts in `\code` folder sequentially: e.g. `python code/1_web_scraping.py`
6. Run `python demo.py` to get the dashboard.

### Notes ###
- `/example-data` folder is an example of how the `/data` folder's structure should be when all codes have been run.