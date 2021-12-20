# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Set Executable Path & Initialize Chrome Browser
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    
    mars_fact = mars_facts()
    feature_image = featured_image(browser)
    news_title, news_paragraph = mars_news(browser)
    image_url_title = hemisphere(browser)
    # Run all scraping functions and store results in a dictionary
    
    data = {
            "news_title": news_title,
            "news_paragraph": news_paragraph,
            "featured_image": feature_image,
            "facts": mars_fact,
            "hemisphere_image_urls": image_url_title,
            "last_modified": dt.datetime.now()
    }
    

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the NASA Mars News Site
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Get First List Item & Wait Half a Second If Not Immediately Present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)
    
    html = browser.html
    news_soup = soup(html, "html.parser")

    # Parse Results HTML with BeautifulSoup
    # Find Everything Inside:
    #   <ul class="item_list">
    #     <li class="slide">
    try:
        slide_element = news_soup.select_one("ul.item_list li.slide")
        slide_element.find("div", class_="content_title")

        # Scrape the Latest News Title
        # Use Parent Element to Find First <a> Tag and Save it as news_title
        news_title = slide_element.find("div", class_="content_title").get_text()

        news_paragraph = slide_element.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    return news_title, news_paragraph


def featured_image(browser):
    # Visit the NASA JPL (Jet Propulsion Laboratory) Site
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Ask Splinter to Go to Site and Click Button with Class Name full_image
    # <button class="full_image">Full Image</button>
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

   

    # Parse Results HTML with BeautifulSoup
    html = browser.html
    image_soup = soup(html, "html.parser")

   # Find the relative image url
    img_url_rel = image_soup.find('img', class_='fancybox-image').get('src')
    img_url_rel
   # Use Base URL to Create Absolute URL
    img_url = f"{url}{img_url_rel}"
    return img_url

def mars_facts():

    #scrape the entire table with Pandas' .read_html() function
    df = pd.read_html('https://galaxyfacts-mars.com')[0]
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    df
   
    # Add try/except for error handling
    
    # Assign columns and set index of dataframe
    #df.columns = ['Mars-Earth Comparison', 'Mars', 'Earth']
    #df.set_index('Mars-Earth Comparison', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

#scrape the hemisphere data
def hemisphere(browser):

# 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)


    hemisphere_image_urls = []
    #links = browser.find_by_css("a.product-item h3")
    for i in range(4):
            
        hemisphere = {}
        browser.find_by_css("a.product-item h3")[i].click()
        sample_elem = browser.find_link_by_text('Sample').first
        hemisphere['img_url'] = sample_elem['href']
        hemisphere['title'] = browser.find_by_css("h2.title").text
        hemisphere_image_urls.append(hemisphere)
        browser.back()
    return hemisphere_image_urls
    
       
if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
