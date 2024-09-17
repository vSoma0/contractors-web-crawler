import scrapy
import csv

class WebcrawlingSpider(scrapy.Spider):
    name = "webcrawling"
    allowed_domains = ["muqawil.org"]
    start_urls = ["https://muqawil.org/en/contractors"]
    
    def __init__(self, *args, **kwargs):
        super(WebcrawlingSpider, self).__init__(*args, **kwargs)
        self.scrapedItem = [] # Initialize a list for scraped items
        self.page_count = 0  # Initialize a counter for pages crawled

    def parse(self, response):
        self.page_count += 1 # Increment the page counter
        # Limit to the first 10 pages
        if self.page_count > 10:
            self.logger.info("Reached the limit of 10 pages.")
            return  # Stop crawling further

        contractors = response.css('h4.card-title')
        for contractor in contractors:
            nextUrl = contractor.css('h4 a::attr(href)').get()
            nextCompany = contractor.css('h4 a::text').get()
            if nextUrl and nextCompany:
                yield scrapy.Request(
                    response.urljoin(nextUrl),
                    callback=self.parse_contractor,
                    meta={'Company_name': nextCompany, 'Company_url': nextUrl}
                )

        # Finding the "Next Page" link with the updated selector
        nextPage = response.css('a.page-link[rel="next"]::attr(href)').get()
        # Log which page is being followed
        if nextPage:
            self.logger.info(f"Following next page: https://muqawil.org{nextPage}") 
            yield response.follow(response.urljoin(nextPage), callback=self.parse)
        else:
            self.logger.info("No next page found.")

    def parse_contractor(self, response):
        data = {
            'Company_name': response.meta['Company_name'],
            'Company_url': response.meta['Company_url'],
            'Membership_number': 'N/A',
            'City': 'N/A',
            'Email': 'N/A',
            'Activities': []
        }
        
        details = response.css('div.info-box')
        # Extract membership number and city
        data['Membership_number'] = details[0].css('div.info-value::text').get(default='N/A').strip() if len(details) > 0 else 'N/A'
        data['City'] = details[7].css('div.info-value::text').get(default='N/A').strip() if len(details) > 7 else 'N/A'
        
        # Extract and decode the email
        email = response.css('span.__cf_email__::attr(data-cfemail)').get()
        if email:
            data['Email'] = self.decode_emails(email)
        
        # Extract activities    
        activities = response.css('li.list-item::text').getall()
        data['Activities'] = [activity.strip() for activity in activities]
        
        # Print out the data for debugging
        self.logger.info(f"Scraped: {data}")  # Log scraped data
        self.scrapedItem.append(data)
        yield data
        
    def decode_emails(self, email):
        if not email:
            return 'N/A'
        # Convert the hex string to bytes
        email = email[0:2] + email[2:].replace('0x', '')
        email = email.lower()
        decoded_email = ''
        key = int(email[:2], 16)
        for i in range(2, len(email), 2):
            decoded_email += chr(int(email[i:i+2], 16) ^ key)
        return decoded_email

    def close(self, reason):
        self.logger.info(f"Total items scraped: {len(self.scrapedItem)}")  # Log total number
        if self.scrapedItem:
            with open('contractors.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fields = ['Company_name', 'Company_url', 'Membership_number', 'City', 'Email', 'Activities']
                writer = csv.DictWriter(csvfile, fieldnames = fields)
                writer.writeheader()
                writer.writerows(self.scrapedItem)
        