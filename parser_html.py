import time
import requests
import pyodbc
import uuid
from bs4 import BeautifulSoup
# import datetime
import threading
import math
from UserData import Candidate, LinkScraper

# TIME_PERIOD defines whole amount of cv that shows at rabota.ua
TIME_PERIOD = '7'
KEY_WORD = 'Юрист'
CURRENT_PAGE = 1
URL = 'https://rabota.ua'
USER_EMAIL = 'vorona.mvl@gmail.com'
USER_PASSWORD = 'Vorona_Ukraine'

# Constatns for database
# predefined values for testing
# functional part to define it from some outer source
# should be done
# This company Id only for development and testing
COMPANY_ID = '00000000-0000-0000-0000-000000000000'
PRIVATE = 1
PERSONAL_PROFILE = 0
PROCESSED = 1
STATUS = 8
REGISTERED_USER = 0
ROLE = 0
categories = {
    'geo_coords': 'Географические координаты',
    'country': 'Страна',
    'region': 'Область',
    'district': 'Район',
    'city': 'Населенный пункт',
    'street': 'Улица',
    'house': 'Дом',
    'apartment': 'Квартира',
    'gender': 'Пол',
    'birth_date': 'Дата рождения',
    'family_status': 'Семейное положение',
    'nationality': 'Национальность',
    'religion': 'Вероисповедание',
    'phone_number': 'Телефон',
    'email': 'E-mail',
    'messanger': 'Мессенджер',
    'social_network': 'Социальная сеть',
    'name': 'ФИО',
    'address': 'Адрес',
    'job_status': 'Занятость',
    'work_experience': 'Стаж',
    'salary': 'Оклад',
    'skills': 'Навыки',
    'internet': 'Интернет',
    'education': 'Образование',
    'scholar_edu': 'Среднее образование',
    'higher_edu': 'Высшее образование',
    'languages': 'Владение языками',
    'general_info': 'Общие данные'
}

def get_one_page_links(request_link):
    req = requests.get(request_link, auth=(USER_EMAIL, USER_PASSWORD))
    soup = BeautifulSoup(req.text, 'html.parser')
    cv_links_wrappers = soup.find_all('h3', attrs={'class': 'cv-list__cv-title'})
    cv_hrefs = list(map(lambda wrapper: wrapper.a['href'], cv_links_wrappers))
    return cv_hrefs


def get_pages_html(cv_page_links, soap_arr):
    for i, link in enumerate(cv_page_links):
        print("In scraping sicle; TIMEOUT: 0" + " " + str(i) + "-th page was taken")
        print(link)
        req = requests.get(link, auth=(USER_EMAIL, USER_PASSWORD))
        soup_arr.append(BeautifulSoup(req.text, 'html.parser'))

# 'https://rabota.ua/employer/find/cv_list?keywords=Маркетолог&period=7&sort=date&pg=1'
t = time.time()

while 1:
    print("Current page: " + str(CURRENT_PAGE) + "  in general page")
    request_string = URL + '/employer/find/cv_list?keywords=' + KEY_WORD + '&period=' + TIME_PERIOD + '&sort=date&pg=' + str(CURRENT_PAGE)
    print(request_string)
    cv_hrefs = get_one_page_links(request_string)


    # Devide cv_hrefs list into to halfs to mak 2 threads
    cv_hrefs_1th = cv_hrefs[:math.floor(len(cv_hrefs) / 4)]
    cv_hrefs_2d = cv_hrefs[math.floor(len(cv_hrefs) / 4): math.floor(len(cv_hrefs) / 2)]
    cv_hrefs_3d = cv_hrefs[math.floor(len(cv_hrefs) / 2): 3 * math.floor(len(cv_hrefs) / 4)]
    cv_hrefs_4th = cv_hrefs[3 * math.floor(len(cv_hrefs) / 4):]

    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 13 for SQL Server};Server=tcp:morbaxsql.database.windows.net,1433;Database=MorbaxDB;Uid=morbax@morbaxsql;Pwd={!NeedMoreBaks1111};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = cnxn.cursor()
    # Exit program if there aren't any cv's more
    if len(cv_hrefs) < 1:
        print("ALL CVs were taken")
        exit(0)

    cv_page_links = list(map(lambda cv_id: URL + cv_id, cv_hrefs))
    # print(str(CURRENT_PAGE) + "-th page links were taken")

    cv_page_links1 = list(map(lambda cv_id: URL + cv_id, cv_hrefs_1th))
    cv_page_links2 = list(map(lambda cv_id: URL + cv_id, cv_hrefs_2d))
    cv_page_links3 = list(map(lambda cv_id: URL + cv_id, cv_hrefs_3d))
    cv_page_links4 = list(map(lambda cv_id: URL + cv_id, cv_hrefs_4th))

    scrapper = LinkScraper(USER_EMAIL, USER_PASSWORD)
    # Define 2 threads
    t1 = threading.Thread(target=scrapper.scrap_links, args=(cv_page_links1, scrapper.soup_arr1))
    t2 = threading.Thread(target=scrapper.scrap_links, args=(cv_page_links2, scrapper.soup_arr2))
    t3 = threading.Thread(target=scrapper.scrap_links, args=(cv_page_links3, scrapper.soup_arr3))
    t4 = threading.Thread(target=scrapper.scrap_links, args=(cv_page_links4, scrapper.soup_arr4))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

    soup_arr = scrapper.get_links_list()
    link_iterator = 0

    for html_cv_page in soup_arr:
        print(cv_page_links[link_iterator])
        cv = Candidate()
        cv_last_update = html_cv_page.find('div', attrs={'class': 'cvheadnav'})
        cv_last_update = cv_last_update.find('div', attrs={'class': 'rua-g-clearfix'})
        cv_last_update = cv_last_update.find('span', attrs={'class': 'muted'})
        # Set cv_hash in Candidate instance
        cv.set_cv_hash(cv_last_update)

        personal_info_block = html_cv_page.find('div', attrs={'class': 'gray'})
        html_name_id = 'centerZone_BriefResume1_CvView1_cvHeader_lblName'
        html_job_id = 'centerZone_BriefResume1_CvView1_cvHeader_txtJobName'
        cv.name = personal_info_block.find('span', attrs={'id': html_name_id}).text
        cv.job = personal_info_block.find('span', attrs={'id': html_job_id}).text

        if personal_info_block:
            html_p_elem = personal_info_block.find('p', attrs={'class': 'rua-p-t_12'})
            if html_p_elem:
                cv.city = html_p_elem.contents[0] if len(html_p_elem.contents) > 0 else None

                if len(html_p_elem.contents) > 1:
                    cv.set_age(html_p_elem.contents[2])
                if len(html_p_elem.contents) > 3:
                    cv.set_salary(html_p_elem.contents[4])

        # Taking key information data
        key_info_block = html_cv_page.find('div', attrs={'id': 'SkillsHolder'})
        key_data = {'description': '', 'skills': list()}
        if key_info_block:
            # key_info_text = ''
            key_info_list = key_info_block.find_all('p')
            cv.set_key_data_description(key_info_list)

            if key_info_block.ul:
                skills_soup_arr = key_info_block.ul.find_all('li')
                cv.set_key_data_skills(skills_soup_arr)

        # Taking work experience data
        exp_info_block = html_cv_page.find('div', attrs={'id': 'ExperienceHolder'})

        # it can be a function to make program shorter
        if exp_info_block:
            none_exp_block = exp_info_block.find('div', attrs={'class': 'noExpdiv', 'style': 'display: none'})
            if none_exp_block:
                html_data_arr = exp_info_block.find_all(['p', 'hr', 'ul', 'ol'])
                if html_data_arr:
                    cv.set_work_experience(html_data_arr)

        # Executing education block
        edu_html_block = html_cv_page.find('div', attrs={'id': 'EducationHolder'})
        if edu_html_block:
            h3_html_elem = edu_html_block.find('h3', attrs={'class': 'title'})
            if h3_html_elem:
                h3_html_elem.extract()
            edu_html_arr = edu_html_block.find_all(['p', 'hr'])
            if edu_html_arr:
                cv.set_education_data(edu_html_block, edu_html_arr)

        lang_block = html_cv_page.find('div', attrs={'id': 'LanguagesHolder'})
        if lang_block:
            lang_list = lang_block.find_all('p')
            if lang_list:
                cv.set_language_data(lang_list)

        extra_edu = html_cv_page.find('div', attrs={'id': 'TrainingsHolder'})
        if extra_edu:
            print(extra_edu)
            extra_edu_html = extra_edu.find_all(['p', 'hr'])
            if extra_edu_html:
                cv.set_extra_education(extra_edu_html)

        additional_info = html_cv_page.find('div', attrs={'id': 'AdditionalInfoHolder'})
        if additional_info:
            addit_info_html = additional_info.find_all(['p', 'hr', 'ul', 'ol'])
            if addit_info_html:
                cv.set_additional_info(addit_info_html)

        print("\n\n" + cv_page_links[link_iterator])
        print("NAME: " + cv.name)
        print("CITY: " + cv.city)
        print("JOB: " + cv.job)
        print("AGE: " + str(cv.age))
        print("SALARY: " + str(cv.salary))
        print("KEY_DATA: ")
        print(cv.key_data)
        print("\nWORK_EXP: ")
        if cv.work_exp is not None:
            for work in cv.work_exp:
                print(work)
        else:
            print(None)
        if cv.education is not None:
            print("\nCV_EDU: ")
            for edu in cv.education:
                print(edu)
        if cv.language is not None:
            print("\nCV_LANGUAGES")
            for lang in cv.language:
                print(lang)
        if cv.extra_edu:
            print("\nEXTRA_EDU")
            for extra_edu in cv.extra_edu:
                print(extra_edu)
        if cv.additional_info is not None:
            print("\nADDITIONAL_INFO: ")
            for one_info in cv.additional_info:
                print(one_info)
        print('-' * 40)

        del cv

        link_iterator += 1
        # cv_link = cv_page_links[link_iterator]
        #
        # # Checking this cv in database by hash of last updated date string at web-site
        # query = 'SELECT [Id] FROM [dbo].[tbRaw] WHERE [Signature]=?'
        # res = cursor.execute(query, cv_hash)
        # matchings = res.fetchall()
        # # print(len(res.fetchall()))
        # if len(matchings) == 0:
        #     id_tbRaw = uuid.uuid4()
        #     # Writing data to the database
        #     query = 'INSERT INTO' \
        #             '[dbo].[tbRaw]([Id], [DataSource], [Processed], [ContentType]) ' \
        #             'VALUES(?, ?, ?, ?)'
        #     content_type = 'rabota_ua_text'
        #     print(query)
        #     res = cursor.execute(query, (id_tbRaw, cv_link, PROCESSED, content_type))
        #     print(res)
        #     # cnxn.commit()
        #     id_tbPerson = uuid.uuid4()
        #     query = 'INSERT INTO' \
        #             '[dbo].[tbPerson]([Id], [RegisteredUser], [Role], [Status])' \
        #             'VALUES(?, ?, ?, ?)'
        #     print(query)
        #     res = cursor.execute(query, (id_tbPerson, REGISTERED_USER, ROLE, STATUS))
        #     # cnxn.commit()
        #     print(res)
        #
        #     id_tbPersonFile = uuid.uuid4()
        #     query = 'INSERT INTO' \
        #             '[dbo].[tbPersonFile](' \
        #             '[Id], [Id_Person], [Id_CreatedBy], ' \
        #             '[Id_Raw], [Id_Company], [PersonalProfile])' \
        #             'VALUES(?, ?, ?, ?, ?, ?)'
        #     print(query)
        #     res = cursor.execute(query, (id_tbPersonFile, id_tbPerson, id_tbRaw, id_tbRaw, COMPANY_ID, PERSONAL_PROFILE))
        #     # cnxn.commit()
        #     print(res)
        #     query = ''


        # person_id = uuid.uuid4()
        # query = 'INSERT INTO' \
        #         '[dbo].[tbPerson]'
        ###################################
    # exit(0)

    # print("ALL cv-pages at page " + str(CURRENT_PAGE) + "were taken")

    # if len(cv_page_links) > 0:
    #     print("PREPARING to data to be WRITTEN TO DATABASE "),
    #     print("Current page:  " + str(CURRENT_PAGE))
    #     print("links array with duplicates: ")
    #     print(cv_page_links[link_iterator])
    #     print("\n" + "-" * 40 + "\n")
    #     links_to_download = list(filter(lambda link: len(link) > 1, cv_page_links))
    #     links_to_download = set(list(map(lambda link: link[0], links_to_download)))
        # cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};Server=tcp:morbaxsql.database.windows.net,1433;Database=MorbaxDB;Uid=morbax@morbaxsql;Pwd={!NeedMoreBaks1111};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        # cursor = cnxn.cursor()


        # for i, link in enumerate(links_to_download):
        # 	print("WRITE CVs TO DATABASE "),
        # 	#timeout = random.randrange(2, 6, 1)
        # 	#timeout = 0
        # 	#print("TIMEOUT: " + str(timeout)),
        # 	full_link = URL + link
        # 	print(" CV TO BE WRITTEN: " + full_link)
        # 	id_field = uuid.uuid4()
        # 	#time.sleep(timeout)
        # 	req = requests.get(full_link, auth=(USER_EMAIL, USER_PASSWORD), stream=True)
        # 	content_type = req.headers['Content-Type']
        # 	query = "INSERT INTO " \
        # 			"[dbo].[tbRaw]([Id], [DataSource], [Processed], [ContentType], [Data]) " \
        # 			"VALUES(?, ?, 0, ?, CONVERT(VARBINARY(MAX), ?))"
        # 	cursor.execute(query, (id_field, full_link, content_type, req.content))
        # 	cnxn.commit()
        # 	print("CV WAS SUCCESSFULLY WRITEN; CURRENT PAGE:" + str(CURRENT_PAGE))
    CURRENT_PAGE = CURRENT_PAGE + 1
