import scrapy
from scrapy import exceptions
from ..items import ContainerItem, BOLItem, MovementContainerItem
class MSCSpider(scrapy.Spider):
    name = "msc"
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id')
        self.headers = {
            "Accept":" text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language":"en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.msc.com",
            "Origin": "https://www.msc.com",
            "Referer": "https://www.msc.com/track-a-shipment",
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            "sec-ch-ua-mobile": "?0",
            "Sec-Fetch-Site": "same-origin" ,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        }
        self.form_data = {
            "__EVENTTARGET" : "ctl00$ctl00$plcMain$plcMain$TrackSearch$hlkSearch",
            "__LASTFOCUS": "",
            "__EVENTARGUMENT": "",
            "ctl00$ctl00$plcMain$plcMain$TrackSearch$txtBolSearch$TextField": kwargs.get('id'),
            "ctl00$ctl00$Header$LanguageSelectionDropDown$ddlSelectLanguage": "en-GB",
            "ctl00$ctl00$Header$HeaderMenuLower$ucHeaderSearchDropdown$txtSearch": "",
            "ctl00$ctl00$Header$HeaderMenuLower$ucHeaderSearchDropdown$vceSearch_ClientState": "",
            "ctl00$ctl00$plcMain$plcMain$hdnEmailAlertsId": "",
            "ctl00$ctl00$plcMain$plcMain$txtEmail$TextField": "",
            "ctl00$ctl00$plcMain$plcMain$hdnDetailsTrackingType": "",
            "ctl00$ctl00$plcMain$plcMain$hdnDetailsTrackingKey": "",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldRecipientName$TextField": "",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldRecipientEmail$TextField": "",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldSenderName$TextField": "",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldSenderEmail$TextField": "",
            "ctl00$ctl00$ucTradeFinanceSignUpModal$hdnFinanceCompanyTerms": "",
            "ctl00$ctl00$ucTradeFinanceSignUpModal$txtName$TextField": "",
            "ctl00$ctl00$ucTradeFinanceSignUpModal$txtEmailAddress$TextField": "",
            "ctl00$ctl00$ucTradeFinanceSignUpModal$txtCompanyName$TextField": "",
            'ctl00$ctl00$ucTradeFinanceSignUpModal$txtPhoneNumber$TextField': "",
            'g-recaptcha-response': "",
        }
        self.start_urls = ["https://www.msc.com/track-a-shipment"]


    def parse(self, response):
        names = response.xpath('//form[@id="aspnetForm"]/input/@name').getall()
        values = response.xpath('//form[@id="aspnetForm"]/input/@value').getall()

        for index, name in enumerate(names):
            self.form_data[name] = values[index]

        url = "https://www.msc.com/track-a-shipment"

        yield scrapy.FormRequest(
            url=url,
            method="POST",
            headers=self.headers,
            formdata=self.form_data,
            callback=self.parse_page
        )

    def parse_page(self, response):

        error_message = response.xpath("//div[@id='ctl00_ctl00_plcMain_plcMain_pnlTrackingResults']/h3/text()").getall()

        if (len(error_message) == 0):
            def scrape_container(array_of_tables: list, container_id: str, updated_at: str) -> ContainerItem:
                container = ContainerItem()
                container['id_type'] = 'CON'
                container['id'] = container_id
                container['updated_at'] = updated_at

                [details_table, movements_table] = array_of_tables

                titles = details_table.xpath(".//thead/tr/th/text()").getall()
                values = list(map(lambda v: v.replace("\n", "").replace("\r", "").strip(), details_table.xpath('.//tbody/tr/td/text()').getall()))

                for index, title in enumerate(titles):
                    container[title.replace("*", "").strip().lower().replace(" ", "_")] = values[index]

                movements = []

                titles = movements_table.xpath(".//thead/tr/th/text()").getall()

                entries = movements_table.xpath(".//tbody/tr")

                for entry in entries:
                    movement = MovementContainerItem()
                    points = list(map(lambda v: v.replace("\n", "").replace("\r", "").strip(), entry.xpath(".//td/text()").getall()))

                    for index, title in enumerate(titles):
                        movement[title.strip().replace(" ", "_").lower()] = points[index]

                    movements.append(dict(movement))

                container['movements'] = movements

                return container

            def scrape_bill_info(table: list, bol_id: str, updated_at: str) -> ContainerItem:
                bol = BOLItem()
                bol['id_type'] = 'BOL'
                bol['id'] = bol_id

                bol['updated_at'] = updated_at

                titles = table.xpath(".//thead/tr/th/text()").getall()
                values = list(map(lambda v: v.replace("\n", "").replace("\r", "").strip(), table.xpath('.//tbody/tr/td/text()').getall()))

                for index, title in enumerate(titles):
                    bol[title.replace("*", "").strip().lower().replace(" ", "_")] = values[index]

                return bol
                    


            tables = response.xpath("//table")
            updated_at = response.xpath("//div[@id='ctl00_ctl00_plcMain_plcMain_pnlTrackingResults']/p/text()").get()
            updated_at = (updated_at[updated_at.find(".")-2: updated_at.rfind(".")+5] + " " + updated_at[updated_at.find(":") -2 : updated_at.find(":") +3]).replace(".", "/").strip()+":00"

            if len(tables) <= 2:
                container_id = response.xpath("//a[@class='containerToggle']/text()").get()
                container_id = container_id[container_id.index(":") +1:].strip()
                
                yield scrape_container(tables, container_id=container_id, updated_at=updated_at)
            else:
                containers = []
                bol_id = response.xpath("//a[@class='bolToggle']/text()").get()
                bol_id = bol_id[bol_id.index(":")+1:bol_id.index("(")].strip()
                bl_issuer = response.xpath("//div[@id='ctl00_ctl00_plcMain_plcMain_rptBOL_ctl00_pnlBOLContent']/p/text()").getall()[1]
                bol = scrape_bill_info(tables[0], bol_id=bol_id, updated_at=updated_at)
                bol['bl_issuer'] = bl_issuer[bl_issuer.index('MSC'):].strip()
                container_ids = list(map(lambda v: v[v.index(":") + 1:].strip(), response.xpath("//a[@class='containerToggle']/text()").getall()))
                for index, table in enumerate(tables):
                    if index % 2 == 1:
                        container = scrape_container(array_of_tables=[table, tables[index+1]], container_id=container_ids[index // 2], updated_at=updated_at)
                        containers.append(dict(container))
                    
                bol['containers'] = containers

                yield bol
        
        else:
            raise exceptions.CloseSpider(reason='INVALID ID: {0}'.format(self.id))


        



        
