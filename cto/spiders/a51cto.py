# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from cto.items import CtospiderItem

class CtoSpider(scrapy.Spider):
    name = '51cto'
    allowed_domains = ['51cto.com']

    def start_requests(self):
        urls = ['http://home.51cto.com/index']
        for url in urls:
            yield scrapy.Request(url, callback=self.cto_login, meta={'cookiejar': 1})

    def cto_login(self, response):
        # 获取csrf值
        csrf = response.xpath("//input[@name='d1g0Smlta3o7DE0kJiU8OQM3WTMjXhtDJCp8JC0qADhPH2YbGT5dHw==']/@value").extract_first()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://blog.51cto.com',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        # 此处为logger输出供调试时使用
        # self.logger.info("获取csrf值为 %s" % csrf)
        yield FormRequest.from_response(response,
                                        url='https://blog.51cto.com/linuxliu?type=1',
                                        headers=headers,
                                        meta={'cookiejar': response.meta['cookiejar']},
                                        formdata={
                                                  # 这个位置注意0要加引号，不然会报错，这个参数意思是是否记住密码10天内自动登录
                                                  'LoginForm[rememberMe]': '0',
                                                  'LoginForm[username]': '****',
                                                  'LoginForm[password]': '*****',
                                                  '_csrf': csrf,
                                                  },
                                        callback=self.after_login,
                                        dont_click=True,
                                        )

    def after_login(self, response):

        # 获取的网页内容
        home_page = response.xpath("//a[@class='con']/text()").extract()
        if 'wx5c789cd76c3af' in home_page:
            self.logger.info('我的博客')
        else:
            self.logger.error('登录失败')

        resps = response.css("ul.artical-list li")
        for resp in resps:
            # 写入item字段中
            item['title_url'] = resp.css("a.tit::attr(href)").extract_first()
            item['title'] = resp.css("a.tit::text").extract_first().strip()
            # fullname的格式为“[名称]（链接）”之所以这样是因为
            # markdown语法里这个表示链接的意思，点击名称直接打开链接内容
            item['fullname'] = '[' + item['title'] + ']' + '(' + item['title_url'] + ')'
            # 此处logger也是调试使用
            # self.logger.info("title url的值为：%s , title的值为%s" % (tit_url, tit))
            yield item

        # 下一页内容获取
        next_page = response.css('li.next a::attr(href)').extract_first()
        # self.logger.info("下一页链接为：%s" % next_page)
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.after_login)