import csv

from selenium.webdriver.common.by import By

from bot import Bot
from constants import output_file_name, search_keywords, seed_url
from utils import extract_text_content_from_url, search_with_context


def iterate_one_iapd_page(bot: Bot, cur_link):
    bot.update_original_window()
    cur_link.click()
    bot.driver.switch_to.window(bot.driver.window_handles[1])
    bot.driver.implicitly_wait(5)
    part2_tab_link = bot.driver.find_element(By.XPATH, "//li[@data-link-page='FIRM_PART_2_BROCHURES']")
    part2_tab_link.click()
    part_2_brochures_links = bot.driver.find_elements(By.XPATH, "//a[@class='link-nostyle cursor-pointer']")
    bot.iapd_url_list.append(bot.driver.current_url)

    company_search_results: list = [[] for _ in range(len(search_keywords))]

    for link in part_2_brochures_links:
        tmp_original_window = bot.driver.current_window_handle
        link.click()
        bot.driver.switch_to.window(bot.driver.window_handles[2])
        bot.driver.implicitly_wait(5)
        tmp_url = bot.driver.current_url

        raw_text: str = extract_text_content_from_url(tmp_url)
        for i, cur_keyword in enumerate(search_keywords):
            cur_search_results = search_with_context(raw_text, cur_keyword)
            company_search_results[i].extend(cur_search_results)
            cur_search_results.clear()
        bot.driver.close()
        bot.driver.switch_to.window(tmp_original_window)
    bot.search_results_list.append(company_search_results)
    bot.driver.close()
    bot.driver.switch_to.window(bot.original_window)


def iterate_100_companies(bot: Bot):
    for i in range(len(bot.company_name_list)):
        print(f"\nCurrent index: {i + 1}")
        bot.update_company_list()
        cur_financial_advisor = bot.company_link_list[i]
        print(f"Current Financial Advisor: {cur_financial_advisor.get_attribute('innerHTML').strip()}")
        cur_financial_advisor.click()
        tmp_link = bot.driver.find_element(By.PARTIAL_LINK_TEXT, "View Filings")
        print(f"Current IAPD link: {tmp_link.get_attribute('href')}")
        phone_number_link = bot.driver.find_element(By.XPATH, "//a[contains(@href, 'tel:')]")
        bot.phone_number_list.append(phone_number_link.get_attribute('innerHTML'))
        average_client_balance_element = bot.driver.find_element \
            (By.XPATH, "//tr[td[contains(., 'Average Client Balance')]][1]/td[2]")
        bot.average_client_balance_list.append(average_client_balance_element.get_attribute('innerHTML').strip())
        assets_under_management_element = bot.driver.find_element \
            (By.XPATH, "//tr[td[contains(., 'Assets Under Management')]][1]/td[2]")
        bot.assets_under_management_list.append(assets_under_management_element.get_attribute('innerHTML').strip())
        company_web_link = bot.driver.find_element(By.XPATH, "//tr[td[contains(., 'Website')]][1]/td[2]/a")
        bot.company_website_list.append(company_web_link.get_attribute('href').strip())
        iterate_one_iapd_page(bot, tmp_link)
        bot.driver.back()


def write_to_file(bot: Bot):
    with open(output_file_name, "w", newline='', encoding='utf-8') as file:
        w = csv.writer(file)
        first_row: list = ["Index", "Financial Advisor Firm", "Phone Number", "Average Client Balance",
                           "Assets Under Management", "Website", "IAPD Page"]
        for word in search_keywords:
            first_row.append(f"Search Results with keyword: {word}")
        w.writerow(first_row)
        for i in range(len(bot.company_name_list)):
            cur_row: list = [i + 1, bot.company_name_list[i].strip(), bot.phone_number_list[i],
                             bot.average_client_balance_list[i], bot.assets_under_management_list[i],
                             bot.company_website_list[i], bot.iapd_url_list[i]]
            for j in range(len(search_keywords)):
                cur_row.append("|||||".join(bot.search_results_list[i][j]))
            w.writerow(cur_row)


def run():
    bot = Bot(seed_url=seed_url, wait_time=15, teardown=False)
    bot.land_first_page()
    iterate_100_companies(bot)
    write_to_file(bot)
