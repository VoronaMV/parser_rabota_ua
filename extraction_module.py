import unicodedata
from data_handler_module import date_transform, clear_digit
import re

def work_data_extraction(one_work_data):
    try:
        if one_work_data.find('hr'):
            raise AttributeError
    except AttributeError:
        return None

    cv_job_data = dict()
    cv_job_position_html = one_work_data.find('b')
    if cv_job_position_html:
        cv_job_data['position'] = cv_job_position_html.text
        if not one_work_data.p.find('em', attrs={'class': 'muted'}):
            cv_job_position_html.parent.extract()
    else:
        cv_job_data['position'] = None
    work_dates_html = one_work_data.p.find('em', attrs={'class': 'muted'})
    if work_dates_html:
        work_dates_str = work_dates_html.text
        (work_start_date, work_end_date) = date_transform(work_dates_str)
        cv_job_data['start_date'] = work_start_date
        cv_job_data['end_date'] = work_end_date
        work_dates_html.parent.extract()

    company_name_html = one_work_data.find('p', attrs={'class': 'muted'})
    if company_name_html:
        if company_name_html.b:
            company_name = unicodedata.normalize("NFKC", company_name_html.b.text).strip()
            cv_job_data['company_name'] = company_name
        else:
            cv_job_data['company_name'] = None
        # print(cv_job_data)
        if company_name_html.em:
            info_text = unicodedata.normalize("NFKC", company_name_html.em.text).strip()
            info_text = re.sub(r'[\t\n\r]+', r' ', info_text)
            cv_job_data['company_additional_info'] = info_text
        else:
            cv_job_data['company_additional_info'] = None
        company_name_html.extract()

        work_description = ''
        work_description_html_p = one_work_data.find_all('p')
        for elem in work_description_html_p:
            if not elem.text:
                elem.extract()

        if work_description_html_p:
            for p_elem in work_description_html_p:
                # this block can be function1 to normalize string
                try:
                    one_work_data.p.next_sibling
                except AttributeError:
                    return None

                if one_work_data.p.next_sibling:
                    appropriate_list = one_work_data.p.next_sibling
                    matching = re.match(r'^ul|^ol', str(appropriate_list.name))
                else:
                    matching = None
                p_elem_text = unicodedata.normalize("NFKC", p_elem.text).strip()
                work_description += p_elem_text + '\n'
                if matching:
                    li_text = ''
                    li_elems = appropriate_list.find_all('li')
                    for li_elem in li_elems:
                        li_text += unicodedata.normalize("NFKC", li_elem.text)
                        li_text = li_text.strip() + '\n'
                    appropriate_list.extract()
                    work_description += li_text
                p_elem.extract()
        ul_cleaner = one_work_data.find_all(['ul', 'ol'])
        for i, ul in enumerate(ul_cleaner):
            if not ul.contents:
                ul.extract()
        if one_work_data.ul or one_work_data.ol:
            work_description_html_li = one_work_data.find_all('li')
            if work_description_html_li:
                for li_elem in work_description_html_li:
                    # this block can be function1 to normalize string
                    li_elem_text = unicodedata.normalize("NFKC", li_elem.text).strip()
                    work_description += li_elem_text + '\n'
                    ##################
                    li_elem.extract()
        cv_job_data['work_description'] = work_description
    return cv_job_data


def edu_data_extraction(one_edu_data):
    cv_edu_data = dict()
    institution = one_edu_data.find('b')
    if institution:
        cv_edu_data['institution'] = unicodedata.normalize("NFKC", institution.text)
        institution.extract()
    else:
        cv_edu_data['institution'] = None
    graduation_year = one_edu_data.find('span', attrs={'class': 'muted'})
    if graduation_year:
        cv_edu_data['graduation_year'] = clear_digit(graduation_year.text)
        graduation_year.extract()
    else:
        cv_edu_data['graduation_year'] = None
    location = one_edu_data.find('p')
    if location:
        study_location = unicodedata.normalize('NFKC', location.text).strip()
        study_location = re.sub(r'\(([\D ,]+)\)', r'\1', study_location)
        cv_edu_data['study_location'] = unicodedata.normalize('NFKC', study_location)
        location.extract()
    else:
        cv_edu_data['study_location'] = None
    return cv_edu_data


def extra_edu_extraction(one_extra_edu):
    extra_edu_dict = dict()
    extra_edu_title = one_extra_edu.find('p')
    extra_edu_name_html = extra_edu_title.find('b')
    if extra_edu_name_html:
        extra_edu_name = extra_edu_name_html.text
        extra_edu_name = unicodedata.normalize('NFKC', extra_edu_name)
        extra_edu_dict['name'] = extra_edu_name.strip()
        extra_edu_title.extract()
    else:
        extra_edu_dict['name'] = None
    extra_edu_end = extra_edu_title.find('span', attrs={'class': 'muted'})
    if extra_edu_end:
        end_year = clear_digit(extra_edu_end.text)
        extra_edu_dict['end_year'] = end_year
        extra_edu_end.extract()
        extra_edu_title.extract()
    extra_edu_desc_html = one_extra_edu.find_all('p')
    if extra_edu_desc_html:
        extra_edu_dict['description'] = ''
        for html_elem in extra_edu_desc_html:
            description = html_elem.text
            description = unicodedata.normalize('NFKC', description)
            description = description.replace('-', '').strip()
            extra_edu_dict['description'] += description + '\n'
            html_elem.extract()
    one_extra_edu.find('hr').extract() if one_extra_edu.hr else None
    return extra_edu_dict


def additional_info_extract(one_addit_info):
    addit_info_dict = dict()
    addit_info_title = one_addit_info.find('p')
    addit_info_name_html = addit_info_title.find('b')
    if addit_info_name_html:
        addit_info_name = addit_info_name_html.text
        addit_info_name = unicodedata.normalize('NFKC', addit_info_name)
        addit_info_dict['name'] = addit_info_name.strip()
        addit_info_title.extract()
    else:
        addit_info_dict['name'] = None

    addit_info_desc_html = one_addit_info.find_all(['p', 'li'])
    if addit_info_desc_html:
        addit_info_dict['description'] = ''
        for html_elem in addit_info_desc_html:
            description = html_elem.text
            description = unicodedata.normalize('NFKC', description)
            description = description.strip()
            addit_info_dict['description'] += description + '\n'
            html_elem.extract()
    one_addit_info.find('hr').extract() if one_addit_info.hr else None
    return addit_info_dict
