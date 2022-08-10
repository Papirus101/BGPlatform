import aiohttp
import os
import re

import asyncio

import datetime

from dotenv import load_dotenv
from fastapi import HTTPException

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup as bss
from sqlalchemy.ext.asyncio import async_session

from db.queries.bg_request_q import get_fz_type_by_name, update_request_info
from db.session import async_sessionmaker
from utils.bot import send_telegram_error

load_dotenv('.env')


class ZakupkiParse:
    def __init__(self):
        #print('Connection create')
        self.company_data = {}
        options = Options()
        #options.add_argument("--headless")
        self.driver = webdriver.Firefox()
        # jar = aiohttp.CookieJar(unsafe=True, quote_cookie=False)
        self.session = aiohttp.ClientSession()
        self.base_url = 'https://zakupki.gov.ru/epz/main/public/home.html'
        #self.driver.get(self.base_url)
        self.domain = 'https://zakupki.gov.ru'
        self.base_search_url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'
        self.order_page = 'https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber={purchase_id}'
        self.search_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString={purchase_id}&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&ca=on&pc=on&pa=on&currencyIdGeneral=-1"

    async def check_available(self):
        session = aiohttp.ClientSession()
        request = await session.get(self.base_url)
        await session.close()
        if request.status != 200:
            return False
        return True
 
    async def _get_cookie(self):
        driver = webdriver.Firefox()
        driver.get(self.domain)
        cookie = driver.get_cookies()
        return cookie

    async def __create_request(self, url: str, name: str, purchase_id: str):
        itter = 1
        if name not in ['base page', 'base search url']:
            try:
                self.driver.get(url)
            except:
                pass

        while True:
            print(itter)
            if itter >= 20:
                self.driver.get(self.base_url)
                self.driver.get(url)
                itter = 0
            try:
                r = await self.session.get(url)
            except:
                r = await self.session.get(url)
            if r.status == 200:
                break
            itter += 1
            await asyncio.sleep(7)
        return r

    async def fz_233_get_data(self, soup, purchase_id):
        lots_link = soup.find_all('a', {'class': 'tabsNav__item'})[1].get('href')
        lots_page = await self.__create_request(self.domain + lots_link, 'lots page', purchase_id)
        soup = bss(await lots_page.text(), 'html.parser')
        lot_link = soup.find('div', {'id': 'inner-html'}).find('a', {'target': '_blank'}).get('href')
        lot_page = await self.__create_request(self.domain + lot_link, 'lot page', purchase_id)
        soup = bss(await lot_page.text(), 'html.parser')
        self.company_data['company_address'] = soup.find('div', {'class': 'common-text__value_no-padding'})
        if self.company_data['company_address'] is None:
            self.company_data['company_address'] = ''
        else:
            self.company_data['company_address'] = self.company_data['company_address'].text.strip()
    
    
    async def fz_44_get_data(self, soup, purchase_id):
        self.company_data['company_address'] = soup.find(
                    'span', text='Место нахождения'
                    ).findParent(
                    'section', {'class': 'blockInfo__section'}
                    ).find(
                    'span', {'class': 'section__info'}
                    ).text.strip()
        organization_link = soup.find(
                'span', text='Размещение осуществляет'
                ).findParent(
                'section', {'class': 'blockInfo__section'}).find(
                'a', {'target': '_blank'}).get('href')
        organization_page = await self.__create_request(organization_link, 'organization page', purchase_id)
        soup = bss(await organization_page.text(), 'html.parser')

    async def test(self, purchase_id: str, request_id: int):
        await self.__create_request(self.base_url, 'base page', purchase_id)
        await self.__create_request(self.base_search_url, 'base search url', purchase_id)
        await asyncio.sleep(5)

        search_page = await self.__create_request(self.search_url.format(purchase_id=purchase_id), 'search page', purchase_id)
        soup = bss(await search_page.text(), 'html.parser')
        try:
            href = soup.find('div', {'class': 'registry-entry__header-mid__number'}).find('a').get('href')
        except AttributeError:
            await send_telegram_error(f'🛒 <strong>Закупки</strong> Ошибка при парсинге информации ИД: {purchase_id}')
            await self.session.close()
            self.driver.close()
            return None
        await asyncio.sleep(5)

        data_page = await self.__create_request(self.domain + href, 'data page', purchase_id)
        soup = bss(await data_page.text(), 'html.parser')

        # Начало парсинга страницы
        try:
            fz = soup.find('div', {'class': 'registry-entry__header-top__title'}).text
        except:
            fz = soup.find('div', {'class': 'cardMainInfo__title'}).text
        self.company_data['company_fz'] = ''.join(re.findall(r'\d+', fz.split('ФЗ')[0]))

        # В зависимости от типа ФЗ, парсим данные
        if self.company_data['company_fz'] == '223':
            try:
                await self.fz_233_get_data(soup, purchase_id)
            except Exception as e:
                await send_telegram_error(e)
        elif self.company_data['company_fz'] == '44':
            try:
                await self.fz_44_get_data(soup, purchase_id)
            except Exception as e:
                await send_telegram_error(e)
        await self.session.close()
        self.driver.close()
        self.company_data['company_fz_id'] = await get_fz_type_by_name(
                async_sessionmaker,
                ''.join(i for i in re.findall(r'\d+', self.company_data['company_fz']))
            )
        del self.company_data['company_fz']
        await send_telegram_error(f'🛒 <strong>Закупки</strong>Спарсили информацию о компании {self.company_data}')
        await update_request_info(async_sessionmaker, request_id, **self.company_data)


class ZachetniyBiznesParser:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.token = f'?api_key={os.getenv("TOKEN")}'
        self.card_url = 'https://zachestnyibiznesapi.ru/paid/data/card'
        self.fssp_url = 'https://zachestnyibiznesapi.ru/paid/data/fssp-list'
        self.search_url = 'https://zachestnyibiznesapi.ru/paid/data/search'
        self.fs_fns_url = 'https://zachestnyibiznesapi.ru/paid/data/fs-fns'
        self.proverki_url = 'https://zachestnyibiznesapi.ru/paid/data/proverki'
        self.last_year = datetime.date.today().year - 1
        self.company_data = {}

    async def get_company_name(self, inn: int | str):
        page = await self.session.get(f'{self.search_url}{self.token}&string={str(inn)}')
        data = await page.json()
        if data.get('status') != '200':
            await send_telegram_error(f'🏪 <strong>Зачётный бизнес</strong> не получилось спарсить имя по ИНН {inn}')
            await self.session.close()
            return None       
        try:
            name = data.get('body').get('docs')[0].get('НаимЮЛСокр')
        except IndexError:
            raise HTTPException(400, {'error': 'inn invalid'})
        return name

    async def close_session(self):
        await self.session.close()

    async def get_info_company_request(self, inn: int | str, request_id: int):
        self.company_data['company_name'] = await self.get_company_name(inn)
        page = await self.session.get(f'{self.card_url}{self.token}&id={inn}&_format=json')
        data = await page.json()
        data = data.get('body').get('docs')[0]
        self.company_data['company_ogrn'] = data.get('ОГРН')
        self.company_data['company_opf_code'] = data.get('КодОПФ')
        self.company_data['company_address'] = data.get('Адрес')
        self.company_data['company_date_register'] = data.get('ДатаОГРН')
        self.company_data['company_rnp'] = False if data.get('НедобросовПостав') == 0 else True
        self.company_data['company_auth_capital'] = int(data.get('СумКап')) if data.get('СумКап') is not None else 0
        self.company_data['company_bankrupt'] = False
        self.company_data['company_last_revenue_sum'] = 0
        self.company_data['company_tax_arrears_sum'] = 0
        self.company_data['company_arbitration_cases_sum'] = 0
        if data.get('Активность') is not None and data.get('Активность') == 'В стадии ликвидации' or data.get(
                'Активность') == 'Ликвидировано':
            self.company_data['company_bankrupt'] = True
        if data.get(f'ФО{self.last_year}') is not None:
            self.company_data['company_last_revenue_sum'] = data.get(f'ФО{self.last_year}').get('ВЫРУЧКА')
            self.company_data['company_last_revenue_sum'] = 0 if self.company_data[
                                                                     'company_last_revenue_sum'] is None else int(
                self.company_data['company_last_revenue_sum'])
        if data.get('СуммНедоимЗадолж') is not None and len(data.get('СуммНедоимЗадолж')) > 0:
            for nedoim in data.get('СуммНедоимЗадолж'):
                self.company_data['company_tax_arrears_sum'] += nedoim
        if data.get('СудыСтатистика') is not None and len(data.get('СудыСтатистика')) > 0:
            for otvet in data.get('СудыСтатистика').keys():
                if otvet == 'Ответчик':
                    self.company_data['company_arbitration_cases_sum'] += data.get('СудыСтатистика').get(otvet).get(
                        'Сумма')

        self.company_data['company_executed_lists_sum'] = 0
        if self.company_data["company_ogrn"] is not None:
            fssp_page = await self.session.get(
                f'{self.fssp_url}{self.token}&id={self.company_data["company_ogrn"]}&_format=json')
            if fssp_page.status == 200:
                fssp_data = await fssp_page.json()
                fssp_data = fssp_data.get('body')
                if fssp_data is not None:
                    fssp_data = fssp_data.get('docs')
                    if fssp_data is not None and isinstance(fssp_data, dict):
                        for executed_list in fssp_data:
                            self.company_data['company_executed_lists_sum'] += executed_list.get('СуммаДолга')

        self.company_data['company_mass_address'] = False
        if self.company_data['company_mass_address'] is not None:
            search_address = await self.session.get(
                f'{self.search_url}{self.token}&string={self.company_data["company_address"]}&mass_={self.company_data["company_address"]}')
            if search_address.status == 200:
                mass_address_data = await search_address.json()
                mass_address_data = mass_address_data.get('body')
                if mass_address_data is not None and len(mass_address_data.get('docs')) > 10:
                    self.company_data['company_mass_address'] = True

        self.company_data['company_resident'] = True
        resident_page = await self.session.get(
            f'{self.proverki_url}{self.token}&id={self.company_data["company_ogrn"]}&_format=json')
        if resident_page.status == 200:
            resident_data = await resident_page.json()
            if len(resident_data.get('body')) > 0:
                for datas in resident_data.get('body'):
                    if datas.get('I_SUBJECT').get('@attributes').get('IS_RESIDENT') is not None:
                        self.company_data['company_resident'] = datas.get('@attributes').get(
                            'IS_RESIDENT') if datas.get('@attributes').get('IS_RESIDENT') is not None else True
                        break
        await self.session.close()
        await send_telegram_error(f'🏪 <strong>Зачётный бизнес</strong> спарсили информацию {self.company_data}')
        await update_request_info(async_sessionmaker, request_id, **self.company_data)
