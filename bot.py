from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from company import CompanyInfo
from constants import seed_url as init_seed_url


class Bot:
    def __init__(self, seed_url: str = init_seed_url, wait_time: int = 15,
                 teardown: bool = False):
        self.original_window = None
        self.company_link_list = None
        self.iapd_url_list = []
        self.company_name_list = []
        self.search_results_list = []
        self.phone_number_list = []
        self.average_client_balance_list = []
        self.assets_under_management_list = []
        self.company_website_list = []
        self.address_list = []
        self.company_info_list: list[CompanyInfo] = []
        options = Options()
        options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=options)
        self.seed_url = seed_url
        self.teardown = teardown
        self.driver.implicitly_wait(wait_time)
        self.driver.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.driver.quit()

    def update_company_list(self):
        self.company_link_list = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/rias/')]")

    def land_first_page(self):
        self.driver.get(self.seed_url)
        self.original_window = self.driver.current_window_handle
        self.update_company_list()
        self.company_name_list = [link.get_attribute("innerHTML") for link in self.company_link_list]

    def update_original_window(self):
        self.original_window = self.driver.current_window_handle
