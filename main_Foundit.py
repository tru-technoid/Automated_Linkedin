from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import re

"""For Initilize Chrome Driver Browser"""
def init_browser():
    #1
    chrome_path = r"E:\TRUSHAR\Sem_8_Final\drivers\chromedriver-win64\chromedriver.exe"
    #2
    if not os.path.exists(chrome_path):
        raise FileNotFoundError(f"ChromeDriver not found at: {chrome_path}")

    browser_options = Options()
    options = [
        '--disable-blink-features',
        '--no-sandbox',
        '--start-maximized',
        '--disable-extensions',
        '--ignore-certificate-errors',
        '--disable-blink-features=AutomationControlled'
    ]

    for option in options:
        browser_options.add_argument(option)

    #3
    service = Service(chrome_path)
    
    driver = webdriver.Chrome(service=service, options=browser_options)
    #If Above Not Work Then Comment 1,2,3 step and use below 
    #driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=browser_options)

    driver.set_window_position(0, 0)
    driver.maximize_window()
    print("\nChrome Browser Initialisation Sucessfull.")
    return driver

def validate_email(email):
    """Validate email using regex."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number is 10 digits."""
    return phone.isdigit() and len(phone) == 10

def validate_json():
    config_path = os.path.join(os.path.dirname(__file__), "config_Foundit.json")
    with open(config_path, 'r') as file:
        parameters = json.load(file)

    mandatory_params = ['email', 'password', 'keywords', 'location', 'applied_job', 'no_of_jobs']

    # Check presence of all mandatory fields
    for param in mandatory_params:
        if param not in parameters:
            raise Exception(f"Missing mandatory parameter: {param}")

    # Validate individual fields
    assert validate_email(parameters['email']), "Invalid email format"
    assert isinstance(parameters['password'], str) and parameters['password'], "Password cannot be empty"
    assert isinstance(parameters['keywords'], str) and parameters['keywords'], "Keywords must be a non-empty string"
    assert isinstance(parameters['location'], str) and parameters['location'], "Location must be a non-empty string"
    assert isinstance(parameters['applied_job'], list), "'applied_job' must be a list"
    assert isinstance(parameters['no_of_jobs'], int) and parameters['no_of_jobs'] > 0, "'no_of_jobs' must be a positive integer"

    print("\nValidation of config.json file was successful!")
    return parameters

class AutoJobApplyTest:
    def __init__(self, parameters, driverss):
        self.email = parameters['email']
        self.password = parameters['password']
        self.keywords = parameters['keywords']
        self.location = parameters['location']
        self.applied_job = []
        self.no_of_jobs = parameters['no_of_jobs']
        self.driver = driverss
        self.output_file_directory = parameters['outputFileDirectory']
        self.file_name = "Applied_Jobs_Foundit"

    """For Log In To Account"""
    def login_Foundit(self):
        #Maximize The Window
        self.driver.maximize_window()
                
        #Make Driver Go To Foundit Login Url
        self.driver.get("https://www.foundit.in/")
        
        time.sleep(3)

        self.driver.get("https://www.foundit.in/rio/login")

        """Toggle the 'Keep me logged in' checkbox."""
        
        try:
            time.sleep(2)
            # Wait for the checkbox to be present and clickable
            accept_cookie_allow = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "acceptAll"))
            )
            #Click To Allow Cookie
            accept_cookie_allow.click()
            print("\nSucessFully Clicked  On Accept Cookie.")
            
        except Exception as e:
            print(f"An error occurred while allow cookie : {e}")
        
        time.sleep(2)

        try:
            # Wait for the checkbox to be present and clickable
            login_via = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'loginWith')]"))
            )
            #Click To Login With Password
            login_via.click()
            print("\nSucessFully Clicked  On LoginVia")
            
        except Exception as e:
            print(f"An error occurred while toggling the checkbox: {e}")
        time.sleep(2)

        # Locate the email input field
        login_Email = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "signInName"))
        )
        login_Email.clear()
        login_Email.send_keys(self.email)

        time.sleep(2)

        # Locate the password input field
        login_Password = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        login_Password.clear()
        login_Password.send_keys(self.password)
        
        # Submit the form
        login_Password.send_keys(Keys.RETURN)
        time.sleep(2)

    def job_Search(self):
        #Go to Dashboard
        self.driver.get("https://www.foundit.in/seeker/dashboard")
        # Wait for the search input fields to be present
        try:
            search_Keyword = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "Desktop-skillsAutoComplete--input"))
            )
            search_Keyword.clear()
            search_Keyword.send_keys(self.keywords)
            search_Keyword.send_keys(Keys.RETURN)

        except TimeoutException:
            print("Timeout while waiting for the search input fields.")

    def quickApply(self):
        # Wait for and click the "Quick Apply" button
        quick_apply_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'quickApplyFilter')]"))
        )
        quick_apply_button.click()
        time.sleep(5)

        try :    
            # Step 1: Click the "Location" filter button
            location_filter_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'filter-pill') and contains(text(), 'Location')]"))
            )
            location_filter_btn.click()
            print("\nClick On Location Filter.")
            time.sleep(2)

            # Step 2: Type the location stored in self.location
            search_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input.search-input"))
            )
            search_input.clear()
            search_input.send_keys(self.location)
            print("\nEnter Search Text")
            time.sleep(2)

            # Step 3: Wait and click the checkbox for the searched location
            checkbox_label = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//input[@value='{self.location}']/following-sibling::label"))
            )
            checkbox_label.click()
            print("clicked On Check Box")
            time.sleep(2)

            # Step 4 (Optional): Click the Apply button
            apply_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'apply')]"))
            )
            apply_button.click()
            print("Clicked On Apply")
            time.sleep(2)
        
        except TimeoutException:
            print("Timeout while waiting for the search location fields.")

    def find_offers(self):
        # Wait for the element containing job count text
        job_count_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.job-count"))
        )

        # Extract text and use regex to get the number
        job_count_text = job_count_element.text
        match = re.search(r"Showing\s+(\d+)", job_count_text)

        if match:
            total_results_int = int(match.group(1))
            total_page = int(total_results_int/15)
            print("\nTotal Results:", total_results_int)
        else:
            print("\n Job count number not found.")

        #Get results for the first page
        #results = self.driver.find_elements(By.CSS_SELECTOR, "li.occludable-update")
        
        # Wait until job cards are present
        job_title_elements = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.ID, "jobCardTitle"))
        )

        # Extract the text from each job title element and store in array
        job_titles = [job.text.strip() for job in job_title_elements]

        # Print the extracted job titles
        print("Job Titles Found On 1st Page : ", job_titles)
        for jobs_elements in job_title_elements:
            if(self.no_of_jobs > len(self.applied_job)):
                hover = ActionChains(self.driver).move_to_element(jobs_elements)
                hover.perform()
                print("Applying For : ",jobs_elements)

                #Submit Application
                self.submit_apply(jobs_elements)

        if(self.no_of_jobs>len(self.applied_job)):
            try:
                # Wait until pagination is loaded
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
                )
                print("\nPagination Located ")    
                # Find all number elements again to avoid StaleElementReferenceException
                page_elements = self.driver.find_elements(By.CSS_SELECTOR, ".pagination .number")
                print("Page Elemnts : ",page_elements)
  
                for i in range(2,len(page_elements)):
                    if(self.no_of_jobs==len(self.applied_job)):
                        break
                    for page in page_elements:
                        if(self.no_of_jobs==len(self.applied_job)):
                            break
                        if page.text.strip() == str(i):
                            #self.driver.execute_script("arguments[0].scrollIntoView(true);", page)  # Scroll into view
                            page.click()
                            print(f"Clicked on page {i}")
                            time.sleep(6)  # Wait for results to load
                            # Wait until job cards are present

                            job_title_elements = WebDriverWait(self.driver, 20).until(
                                EC.presence_of_all_elements_located((By.ID, "jobCardTitle"))
                            )

                            # Extract the text from each job title element and store in array
                            job_titles = [job.text.strip() for job in job_title_elements]

                            time.sleep(4) 
                            # Print the extracted job titles
                            print("Job Titles Found On Other Page : ", job_titles)
                            print("\nI = ",i)
                            for jobs_elements in job_title_elements:
                                if(self.no_of_jobs > len(self.applied_job)):
                                    hover = ActionChains(self.driver).move_to_element(jobs_elements)
                                    hover.perform()
                                    print("Applying For : ",jobs_elements)

                                    #Submit Application
                                    self.submit_apply(jobs_elements)
                            break  # Stop looping once the correct page is clicked

            except TimeoutException:
                print("Timeout while waiting for pagination numbers")

    def submit_apply(self,job_ele):
        job_title = job_ele.text.strip()
        print("\nApplying For : ",job_title)
        job_ele.click()

        time.sleep(3)

        try:
            job_title_element = self.driver.find_element(By.CLASS_NAME, "jdTitle")
            s_job_title = job_title_element.text.strip()
            print("Extracted Job Title:", s_job_title)
        except Exception as e:
            print("Error extracting job title:", e)
            
        try:
            company_name_element = self.driver.find_element(By.CLASS_NAME, "jdCompanyName")
            s_company_name = company_name_element.text.strip()
            print("Extracted Company Name:", s_company_name)
        except Exception as e:
            print("Error extracting company name:", e)
            
        # Extracting the third "highlightsRow" div
        try:
            # Find all the 'highlightsRow' divs
            highlight_rows = browser.find_elements(By.CSS_SELECTOR, "div.jdHighlights div.highlightsRow")
            
            # Check if there are enough rows and extract the third one
            if len(highlight_rows) >= 3:
                third_row = highlight_rows[2]  # The third item (index starts from 0)
                
                # Extract the span text (e.g., 'FinTech')
                third_row_text = third_row.find_element(By.TAG_NAME, "span").text.strip()
                
                print("Third Highlight Row Text:", third_row_text)
                s_industry = third_row_text
            else:
                print("Not enough highlight rows found.")
                s_industry = ""
        except Exception as e:
            print("Error:", e)
            s_industry = ""

        
        try:
            # Wait until the Quick Apply button is clickable and then click it
            quick_apply_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "applyNowBtn"))
            )
            quick_apply_btn.click()
            time.sleep(5)
            print("Button Located and clicked Suceessfull Now Go To Next.")
            self.applied_job.append(job_title)
            self.save_to_file(s_job_title,s_company_name,s_industry)

        except TimeoutException:
            print("Timeout while waiting for the search location fields.")

    """Saves the current state to the JSON file."""
    def save_to_file(self, s_job_title,s_company,s_industry):
        file_path = self.output_file_directory + self.file_name + ".json"
        new_data = {
            "job_title": s_job_title,
            "Company Name": s_company,
            "Industry Type": s_industry
        }

        # Load existing data if file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        # Append new job entry
        data.append(new_data)

        # Save back to file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def close_session(self):
        """This function closes the actual session""" 
        print('End of the session, see you later!')
        print("Total Job Applied Are : ",len(self.applied_job))
        print("Total Job Applied Are : ",self.applied_job)
        self.driver.close()

    def apply_Functions(self):
        self.login_Foundit()
        time.sleep(8)  # Wait for login to complete
        self.job_Search()
        time.sleep(8)
        self.quickApply()
        time.sleep(5)
        self.find_offers()
        time.sleep(3)
        self.close_session()

if __name__ == "__main__":
    start_time = datetime.now()
    parameters=validate_json()
    browser = init_browser()
    bot = AutoJobApplyTest(parameters, browser)
    bot.apply_Functions()
    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"\Total time taken : {total_time} ")