# Dashboard Demo #
---
This project demonstrates how to build your own dashboard using web-scraped data.

## Dependencies ##
- Python 3.9.5

## Installation ##
---
1. Clone this project.
2. Create and activate virtual enrinvonment.
3. Download Spacy's package: `python -m spacy download en_core_web_sm`
4. Go to cloned folder (where `requirements.txt` is) and install dependencies: `pip install -r requirements.txt --user`
5. Run the scripts in `\code` folder sequentially to prepare the data for the dashboard: e.g. `python code/1_web_scraping.py`
6. Run `python app.py` to get the dashboard.