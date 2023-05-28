import csv
import math

import pandas as pd

from selenium.webdriver.common.by import By

from bot import Bot
from company import CompanyInfo
from constants import output_file_name, search_keywords, seed_url, input_file_name
from utils import extract_text_content_from_url, search_with_context

dataframe_input = pd.read_excel(input_file_name)


def read_from_xlsx(bot: Bot):
    for index, row in dataframe_input.iterrows():
        company: CompanyInfo = CompanyInfo()
        company.company_name = row['Primary Business Name']
        tmp_strings: list = [row['Main Office Street Address 1'], row['Main Office Street Address 2'],
                             row['Main Office City'], row['Main Office State'], row['Main Office Country'],
                             str(row['Main Office Postal Code'])]
        company.address = ', '.join([str(s) for s in tmp_strings if not (isinstance(s, float) and math.isnan(s))])
        company.crd_num = row['Organization CRD#']
        company.iapd_url = "https://adviserinfo.sec.gov/firm/brochure/" + str(company.crd_num)
        company.company_website = row['Website Address']
        company.index = index
        company.phone_number = row['Main Office Telephone Number']
        company.discretionary_aum = row['5F(2)(a)']
        company.non_discretionary_aum = row['5F(2)(b)']
        company.total_aum = row['5F(2)(c)']
        for i in range(ord('a'), ord('n') + 1):
            cur_column_name = "5D(" + chr(i) + ")(1)"
            if not math.isnan(row[cur_column_name]):
                company.client_number += row[cur_column_name]

        bot.company_info_list.append(company)


def iterate_one_iapd_page(bot: Bot, idx: int):
    print(f"Processing company {idx + 1} of {len(bot.company_info_list)}")
    bot.driver.get(bot.company_info_list[idx].iapd_url)
    bot.driver.implicitly_wait(5)
    part_2_brochures_links = bot.driver.find_elements(By.XPATH, "//a[@class='link-nostyle cursor-pointer']")

    company_search_results: list = [[] for _ in range(len(search_keywords))]

    for link in part_2_brochures_links:
        tmp_original_window = bot.driver.current_window_handle
        link.click()
        bot.driver.switch_to.window(bot.driver.window_handles[len(bot.driver.window_handles) - 1])
        bot.driver.implicitly_wait(15)
        tmp_url = bot.driver.current_url

        raw_text: str = extract_text_content_from_url(tmp_url)
        for i, cur_keyword in enumerate(search_keywords):
            cur_search_results = search_with_context(raw_text, cur_keyword)
            company_search_results[i].extend(cur_search_results)
            cur_search_results.clear()
        bot.driver.close()
        bot.driver.switch_to.window(tmp_original_window)
    bot.company_info_list[idx].search_results = company_search_results
    # bot.driver.close()


def iterate_all_iapd_pages(bot: Bot):
    for i in range(len(bot.company_info_list)):
        iterate_one_iapd_page(bot, i)


def write_to_csv(bot: Bot):
    with open(output_file_name, "w", newline='', encoding='utf-8') as file:
        w = csv.writer(file, escapechar='\\')
        first_row: list = ["Index", "Financial Advisor Firm", "Phone Number", "Total Client Number",
                           "Discretionary Assets Under Management", "Non-Discretionary Assets Under Management",
                           "Total Discretionary Assets Under Management", "Main Office Address", "Website", "IAPD Page"]
        for word in search_keywords:
            first_row.append(f"Search Results with keyword: {word}")
        w.writerow(first_row)
        for i in range(len(bot.company_info_list)):
            cur_row: list = [i + 1, bot.company_info_list[i].company_name, bot.company_info_list[i].phone_number,
                             bot.company_info_list[i].client_number, bot.company_info_list[i].discretionary_aum,
                             bot.company_info_list[i].non_discretionary_aum, bot.company_info_list[i].total_aum,
                             bot.company_info_list[i].address, bot.company_info_list[i].company_website,
                             bot.company_info_list[i].iapd_url]
            for j in range(len(search_keywords)):
                cur_row.append("|||||".join(bot.company_info_list[i].search_results[j]))
            w.writerow(cur_row)


def run_from_xlsx():
    bot = Bot()
    read_from_xlsx(bot)
    iterate_all_iapd_pages(bot)
    write_to_csv(bot)
    bot.driver.close()
