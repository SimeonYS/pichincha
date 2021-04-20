import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import PpichinchaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class PpichinchaSpider(scrapy.Spider):
	name = 'pichincha'
	start_urls = ['https://www.pichincha.com/portal/blog']

	def parse(self, response):
		post_links = response.xpath('//h5/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Weiter"]/@href').get()
		if len(post_links) == 9:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="date"]/text()').get()
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PpichinchaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
