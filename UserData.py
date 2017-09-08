import re
import unicodedata
import requests
import hashlib
from bs4 import BeautifulSoup
from data_handler_module import clear_digit, check_alpha, lang_level_gerade
from extraction_module import (work_data_extraction,
                               edu_data_extraction,
                               extra_edu_extraction,
                               additional_info_extract)


class Candidate(object):
    cv_link = 'link'

    def __init__(self):
        self.link = None
        self.name = None
        self.city = None
        self.job = None
        self.age = None
        self.salary = None
        self.key_data = dict()
        self.work_exp = list()
        self.education = list()
        self.extra_edu = list()
        self.additional_info = list()
        self.cv_hash = None
        self.language = list()

    def set_cv_hash(self, html_elem=None):
        if html_elem is not None:
            text = unicodedata.normalize('NFKC', html_elem.text).strip()
            self.cv_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

    @staticmethod
    def __extract_number(string):
        extracted_digit = clear_digit(string)
        if len(extracted_digit) > 0:
            return int(extracted_digit)

    @staticmethod
    def __data_appending_loop(html_data_list, target, data_extraction_function):
        one_info_block = BeautifulSoup('<div></div>', 'html.parser')
        for html_elem in html_data_list:
            if re.match(r'<hr[ /]{1,2}>', str(html_elem)):
                extracted_dict = data_extraction_function(one_info_block)
                if extracted_dict:
                    target.append(extracted_dict)
            else:
                one_info_block.append(html_elem)
        else:
            one_info_block.find('div').extract()
            if one_info_block:
                target.append(data_extraction_function(one_info_block))

    def set_age(self, str_with_age):
        self.age = self.__extract_number(str_with_age)

    def set_salary(self, str_with_salary):
        self.salary = self.__extract_number(str_with_salary)

    def set_key_data_description(self, html_data_list=list()):
        text = ''
        for info_html_elem in html_data_list:
            text += unicodedata.normalize("NFKC", info_html_elem.text) + '\n'
        self.key_data['description'] = text

    def set_key_data_skills(self, html_data_list=list()):
        self.key_data['skills'] = list((map(lambda li: li.text, html_data_list)))

    def set_work_experience(self, html_data_arr=list()):
        self.__data_appending_loop(html_data_arr, self.work_exp, work_data_extraction)

    def set_specialities(self, string):
        specialities = unicodedata.normalize("NFKC", string).split('\n')
        specialities_list = list(filter(check_alpha, specialities))
        specialities_list = list(map(lambda elem: elem.strip(), specialities_list))
        for i, one_edu in enumerate(self.education):
            if len(specialities_list) > i:
                one_edu['speciality'] = specialities_list[i]
            else:
                one_edu['speciality'] = None

    def set_education_data(self, edu_html_block, html_data_arr):
        self.__data_appending_loop(html_data_arr, self.education, edu_data_extraction)
        # Specialities text is uot of tags, thats why after
        # all operations with edu block we have only this
        # string, where each speciality devided by new line
        specialities = edu_html_block.text
        self.set_specialities(specialities)

    def set_language_data(self, html_data_arr):
        for lang_info_html in html_data_arr:
            lang_dict = dict()
            if lang_info_html.b:
                lang_name = lang_info_html.b.text
                language = unicodedata.normalize('NFKC', lang_name).strip()
                lang_dict['lang'] = language
                lang_info_html.b.extract()
                interview_lang_html = lang_info_html.find('span', attrs={'class': 'muted'})
                if interview_lang_html:
                    is_interview_lang = interview_lang_html.text
                    is_interview_lang = unicodedata.normalize('NFKC', is_interview_lang)
                    lang_dict['is_interview_lang'] = is_interview_lang.strip()
                    interview_lang_html.extract()
                if lang_info_html.text:
                    lang_level = lang_info_html.text
                    lang_level = unicodedata.normalize('NFKC', lang_level)
                    lang_dict['lang_level'] = lang_level.replace('-', '').strip()
                    lang_dict['level_grade'] = lang_level_gerade(lang_dict['lang_level'])
            self.language.append(lang_dict)

    def set_extra_education(self, html_data_arr):
        self.__data_appending_loop(html_data_arr, self.extra_edu, extra_edu_extraction)

    def set_additional_info(self, html_data_arr):
        self.__data_appending_loop(html_data_arr, self.additional_info, additional_info_extract)


class LinkScraper(object):


    def __init__(self, user_email, user_password):
        self.email = user_email
        self.password = user_password
        self.soup_arr1 = list()
        self.soup_arr2 = list()
        self.soup_arr3 = list()
        self.soup_arr4 = list()

    def scrap_links(self, cv_page_links, soup_arr):
        for i, link in enumerate(cv_page_links):
            print("In scraping sicle; TIMEOUT: 0" + " " + str(i) + "-th page was taken")
            print(link)
            req = requests.get(link, auth=(self.email, self.password))
            soup_arr.append(BeautifulSoup(req.text, 'html.parser'))

    def get_links_list(self):
        links_list = self.soup_arr1 + self.soup_arr2 + self.soup_arr3 + self.soup_arr4
        return links_list
