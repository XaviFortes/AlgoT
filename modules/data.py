import yfinance as yf

def get_stock_data(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period=f"{period}d")
        return stock, info, hist
    except Exception as e:
        return None, None, None

def get_news(stock):
    """
    Fetches and parses news from yfinance.
    Handles the nested structure: item['content']['title']
    """
    try:
        raw_news = stock.news
        parsed_news = []
        
        if raw_news:
            for item in raw_news:
                # Check if content is nested (new yfinance structure)
                content = item.get('content', item)
                
                news_item = {
                    'title': content.get('title', 'No Title'),
                    'link': content.get('link', content.get('clickThroughUrl', {'url': '#'}).get('url', '#')),
                    'publisher': content.get('pubDate', 'Unknown'), # yfinance news structure varies, sometimes no publisher
                    'providerPublishTime': content.get('pubDate', 0) # Using pubDate as proxy if providerPublishTime missing
                }
                
                # Try to find better keys if defaults failed
                if 'provider' in content:
                     news_item['publisher'] = content['provider'].get('displayName', 'Unknown')
                
                parsed_news.append(news_item)
                
        return parsed_news
    except Exception as e:
        return []
