from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from validate_email import validate_email
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import json
import os, pyautogui, random
import time

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

"""For Validating Generated Json File"""
def validate_json():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, 'r') as file:
        parameters = json.load(file)

    mandatory_params = ['email', 'password', 'disableAntiLock', 'experienceLevel', 'jobTypes', 'date',
                        'positions', 'locations', 'outputFileDirectory']

    for param in mandatory_params:
        if param not in parameters:
            raise Exception(f"Missing mandatory parameter : {param}")

    assert validate_email(parameters['email']), "Invalid email"
    assert len(str(parameters['password'])) > 0

    assert isinstance(parameters['disableAntiLock'], bool)

    assert any(parameters['experienceLevel'].values())
    assert any(parameters['jobTypes'].values())
    assert any(parameters['date'].values())

    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0

    print("\nValidation Of Config.JSON File Was SucessFull !!")
    return parameters

class AutoJobApplyTest:
    def __init__(self, parameters, driverss):
        self.driver = driverss
        self.email = parameters['email']
        self.password = parameters['password']
        self.phone_number = parameters['phone_number']
        self.applied_job = []
        self.no_of_jobs = parameters['no_of_jobs']
        self.disable_lock = parameters['disableAntiLock']
        self.positions = parameters.get('positions')
        self.locations = parameters.get('locations')
        self.seen_jobs = []
        self.output_file_directory = parameters['outputFileDirectory']
        self.file_name = "Applied_Jobs"

    """For Log In To Account"""
    def login_Linkedin(self):
        #Maximize The Window
        self.driver.maximize_window()
                
        #Make Driver Go To Linkedin Login Url
        self.driver.get("https://www.linkedin.com/login")
        
        time.sleep(2)
        
        """Toggle the 'Keep me logged in' checkbox."""
        try:
            # Wait for the checkbox to be present and clickable
            checkbox = WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rememberMeOptIn-checkbox']"))
            )
            
            # Click the checkbox to toggle its state
            checkbox.click()
            print("Toggled 'Keep me logged in Off. ")
            
        except Exception as e:
            print(f"An error occurred while toggling the checkbox: {e}")
        
        # Locate the email input field
        login_Email = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.NAME, "session_key"))
        )
        login_Email.clear()
        login_Email.send_keys(self.email)

        # Locate the password input field
        login_Password = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.NAME, "session_password"))
        )
        login_Password.clear()
        login_Password.send_keys(self.password)
        
        # Submit the form
        login_Password.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        current_Page_adrs = self.driver.current_url
        page_source = self.driver.page_source
        
        if '/checkpoint/challenge/' in current_Page_adrs or 'security check' in page_source:            
            input("Please complete the security check and press enter in this console when it is done.")
            time.sleep(random.uniform(5.5, 10.5))
            try:
                check_Security = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'input__email_verification_pin')]"))
                )           
                print("Found Check Input Field \n Prints : ",check_Security)
            
            except TimeoutException:
                check_Security=False
                print("Timeout while waiting for the security code.")
            
            if isinstance(check_Security, WebElement):
                code_User=input("\nEnter Six Digit Code Only : \n\n")
                if(len(code_User)==6):
                    check_Security.send_keys(code_User)
                    check_Security.send_keys(Keys.RETURN)
                    try:
                        jobs_Links = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, 'Jobs'))
                        )
                        
                    except TimeoutException:
                        print("\n\n Security Can't By Pass Enter Correct Code.")
                else:
                    print("\nEnter Code is not exact six  digit try again.")  
        print("\nSuccessfully Logged In.")

    """To Search for Jobs"""
    def job_Search(self):
        # Wait for the "Jobs" link to be clickable
        try:
            jobs_Links = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Jobs'))
            )
            jobs_Links.click()
            
        except TimeoutException:
            print("Timeout while waiting for the 'Jobs' link to be clickable.")
            self.close_session()
            return  # Exit the method if the link is not found

        # Wait for the search input fields to be present
        try:
            search_Keyword = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-keyword')]"))
            )
            search_Keyword.clear()
            search_Keyword.send_keys(self.positions)

            search_Location = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-location')]"))
            )
            search_Location.clear()
            search_Location.send_keys(self.locations)
            time.sleep(3)
            search_Location.send_keys(Keys.RETURN)
            time.sleep(5)

        except TimeoutException:
            print("Timeout while waiting for the search input fields.")

    def scroll_slow(self, scrollable_element, start=0, end=3600, step=100, reverse=False):
        if reverse:
            start, end = end, start
            step = -step

        for i in range(start, end, step):
            self.driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollable_element)
            time.sleep(random.uniform(1.0, 2.6))

    """To Select Or Apply Filters"""
    def easyApply(self):
        #Click on the "Easy Apply" filter button
        easy_apply_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='searchFilter_applyWithLinkedin']"))
        )
        easy_apply_button.click()
        print("\nSucessfully Clicked On Easy Apply Button.")
        time.sleep(3)

        # Click on the "All filters" button
        all_filters_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'search-reusables__all-filters-pill-button')]"))
        )
        all_filters_button.click()
        time.sleep(3)  # Optional: Wait for the filters to load

        # Wait for the modal to be visible
        try:
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'artdeco-modal')]"))
            )
        except TimeoutException:
            print("Timeout while waiting for the filters modal to be visible.")
            return
        if self.disable_lock:
            try:
                # Wait for and click the "Most recent" radio button
                most_recent_radio = WebDriverWait(self.driver, 10).until(
                    #EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='DD']"))
                    EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-sortBy-DD']"))
                )
                most_recent_radio.click()
                print("\nSucessFully Clicked On Most Recent radio Button.")
                time.sleep(2)
            except Exception as e:
                print(f"Failed to click 'Most recent' radio button: {e}")

        date_table = parameters.get('date', [])
        tmps=0
        for key in date_table.keys():
            tmps=tmps+1
            if tmps==0:
                if date_table[key]:
                    try:
                        radio_any_time = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-timePostedRange-"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-timePostedRange-']"))
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", radio_any_time)
                        radio_any_time.click()
                        time.sleep(1)
                        print("\nClicked On Any Time Radio Successfull.")
                    except Exception as e:
                        print(f"Error clicking 'Any time': {e}")
            
            if tmps==2:
                if date_table[key]:
                    try:
                        radio_past_month = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-timePostedRange-r2592000"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-timePostedRange-']"))
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", radio_past_month)
                        radio_past_month.click()
                        time.sleep(2)
                        print("\nSucessfully Clicked On Past Month Filter.")
                    except Exception as e:
                        print(f"Error clicking 'Past month': {e}")

            if tmps==3:
                if date_table[key]:
                    try:
                        radio_past_week = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-timePostedRange-r604800"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-timePostedRange-r604800']"))
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", radio_past_week)
                        radio_past_week.click()
                        time.sleep(2)
                        print("\nSucessFully Clicked On past week.")
                    except Exception as e:
                        print(f"Error clicking 'Past week': {e}")

            if tmps==4:
                if date_table[key]:
                    try:
                        radio_past_24_hours = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-timePostedRange-r86400"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-timePostedRange-r86400']"))
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", radio_past_24_hours)
                        radio_past_24_hours.click()
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error clicking 'Past 24 hours': {e}")

        experience_table = parameters.get('experienceLevel', [])
        tmps=0
        
        #For Finding Experience Level
        try:
            experience_heading = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Experience level')]"))
            )
            self.scroll_slow(experience_heading)
            self.scroll_slow(experience_heading, step=300, reverse=True)
            print("Successfully found and scrolled to 'Experience level' heading.")
        except Exception as e:
            print(f"Failed to find 'Experience level' heading: {e}")

        for key in experience_table.keys():
            tmps=tmps+1
            if tmps==1:
                if experience_table[key]:
                    try:
                        checkbox_internship = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-experience-1"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-experience-1']"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_internship)
                        checkbox_internship.click()
                        time.sleep(2)
                        print("\n Sucessfully clicked on intership level.")
                    except Exception as e:
                        print(f"Error clicking 'Internship': {e}")

            if tmps==2:
                if experience_table[key]:    
                    try:
                        checkbox_entry = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-experience-2']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-experience-2"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_entry)
                        checkbox_entry.click()
                        time.sleep(2)
                        print("\nSucessfully Clicked On Entry Level.")
                    except Exception as e:
                        print(f"Error clicking 'Entry level': {e}")
            
            if tmps==3:
                if experience_table[key]:
                    try:
                        checkbox_associate = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-experience-3']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-experience-3"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_associate)
                        checkbox_associate.click()
                        time.sleep(2)
                        print("\nSuceessFully Clicked On Associate")
                    except Exception as e:
                        print(f"Error clicking 'Associate': {e}")
            
            if tmps==4:
                if experience_table[key]:
                    try:
                        checkbox_mid_senior = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-experience-4']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-experience-4"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_mid_senior)
                        checkbox_mid_senior.click()
                        time.sleep(2)
                        print("\nSucessFully Clicked On mid_senior.")
                    except Exception as e:
                        print(f"Error clicking 'Mid-Senior level': {e}")
            if tmps==5:
                if experience_table[key]:
                    try:
                        checkbox_director = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-experience-5']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-experience-5"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_director)
                        checkbox_director.click()
                        time.sleep(2)
                        print("\nSucessFully Clicked On director.")
                    except Exception as e:
                        print(f"Error clicking 'Director': {e}")
            if tmps==6:
                if experience_table[key]:
                    try:
                        checkbox_executive = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-experience-6"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-experience-6']"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_executive)
                        checkbox_executive.click()
                        time.sleep(2)
                        print("\n Sucessfully Clicked On executive.")
                    except Exception as e:
                        print(f"Error clicking 'Executive': {e}")
                
        jobType_table = parameters.get('jobTypes', [])
        
        #For Finding Experience Level
        try:
            experience_heading = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Job type')]"))
            )
            self.scroll_slow(experience_heading)
            self.scroll_slow(experience_heading, step=300, reverse=True)
            print("Successfully found and scrolled to 'Job Type' heading.")
        except Exception as e:
            print(f"Failed to find 'Job Type' heading: {e}")
        
        tmps=0
        for key in jobType_table.keys():
            tmps=tmps+1
            if tmps==1:
                if jobType_table[key]:
                    try:
                        checkbox_full_time = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-jobType-F"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-jobType-F']"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_full_time)
                        checkbox_full_time.click()
                        time.sleep(2)
                        print("\n SucessFully Clicked On Full Time.")
                    except Exception as e:
                        print(f"Error clicking 'Full-time': {e}")

            if tmps==2:
                if jobType_table[key]:
                    try:
                        checkbox_part_time = WebDriverWait(self.driver, 10).until(
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-jobType-P"))
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-jobType-P']"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_part_time)
                        checkbox_part_time.click()
                        time.sleep(2)
                        print("\nSucessFully Clicked On Part Time.")
                    except Exception as e:
                        print(f"Error clicking 'Part-time': {e}")

            if tmps==3:
                if jobType_table[key]:
                    try:
                        checkbox_contract = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-jobType-C']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-jobType-C"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_contract)
                        checkbox_contract.click()
                        time.sleep(2)
                        print("\nSucessfully Clicked On Contract")
                    except Exception as e:
                        print(f"Error clicking 'Contract': {e}")

            if tmps==4:
                if jobType_table[key]:
                    try:
                        checkbox_temp = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-jobType-T']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-jobType-T"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_temp)
                        checkbox_temp.click()
                        time.sleep(2)
                        print("\nSucessFully Clicked On temp.")
                    except Exception as e:
                        print(f"Error clicking 'Temporary': {e}")

            if tmps==5:
                if jobType_table[key]:
                    try:
                        checkbox_internship = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-jobType-I']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-jobType-I"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_internship)
                        checkbox_internship.click()
                        time.sleep(2)
                        print("\nSucessFully Clicked On Internship.")
                    except Exception as e:
                        print(f"Error clicking 'Internship': {e}")

            if tmps==6:
                if jobType_table[key]:
                    try:
                        checkbox_other = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-jobType-O']"))
                            #EC.element_to_be_clickable((By.ID, "advanced-filter-jobType-O"))
                        )
                        #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_other)
                        checkbox_other.click()
                        time.sleep(2)
                        print("\nSucessFully Clicked On Other")
                    except Exception as e:
                        print(f"Error clicking 'Other': {e}")

        # For Finding Commitment Level H3
        try:
            commit_heading = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Commitments')]"))
            )
            self.scroll_slow(commit_heading)
            self.scroll_slow(commit_heading, step=300, reverse=True)
            print("Successfully found and scrolled to 'Commitments' heading.")
        except Exception as e:
            print(f"Failed to find 'Commitments' heading: {e}")

        try:
            work_life_check_last = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='advanced-filter-commitments-3']"))
                #EC.element_to_be_clickable((By.ID, "advanced-filter-jobType-O"))
            )
            #self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_other)
            work_life_check_last.click()
            time.sleep(2)
            work_life_check_last.click()
            print("\nSucessFully Clicked On work_life_check_last")
        except Exception as e:
            print(f"Error clicking 'work_life_check_last': {e}")

        pyautogui.press('tab', presses=2)
        print("\nPressed On Tab Key Two Times")
        pyautogui.press('enter')
        time.sleep(5)
        print("\nSucessfully Completed All Filters.")
    

    """Finds all the offers through all the pages"""
    def find_offers(self):
        # Wait for the total amount of results
        total_results = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "small.display-flex.t-normal.t-12.t-black--light.jobs-search-results-list__text"))
        )
        
        total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))
        print("Total_resluts_int",total_results_int)
        time.sleep(2)

        # Get results for the first page
        current_page = self.driver.current_url
        
        #results = self.driver.find_elements(By.CSS_SELECTOR, "occludable-update.artdeco-list__item--offset-4.artdeco-list__item.p0.ember-view")
        
        #Get results for the first page
        results = self.driver.find_elements(By.CSS_SELECTOR, "li.occludable-update")
        
        print("Results found on the first page:", len(results))
        time.sleep(2)
        print("Found  results  : \n\n ",results)

        #Fetch  The Web Element Of Applications
        for result in results:
            if(self.no_of_jobs > len(self.applied_job)):
                hover = ActionChains(self.driver).move_to_element(result)
                hover.perform()
                
                # Retrieve the job title link
                title_element = result.find_element(By.CSS_SELECTOR, 'a.job-card-container__link')
                title_text = title_element.text  # Get the text of the title
                print("Title:", title_text)
                
                # Submit application
                self.submit_apply(title_element)
        
        if(self.no_of_jobs > len(self.applied_job)):        
            #If Job_Application is More Than 
            if total_results_int > 24:
                time.sleep(2)
                
                #Get The Last Page & Get Base URL
                Last_Page=int(total_results_int/25)
                print("\nFound Last Page : ",Last_Page)
                
                #Navigate through all pages
                for page_number in range(1, Last_Page + 1):
                    if page_number > 1:  #Skip the first page since it's already processed
                        
                        #Click on the specific page number button
                        page_button = self.driver.find_element(By.XPATH, f"//button[@aria-label='Page {page_number}']")
                        page_button.click()
                        print("\nClick On Next Page : ",page_number)
                        time.sleep(2)  # Wait for the page to load

                    if(self.no_of_jobs > len(self.applied_job)):
                        #Get results for the current page
                        results_ext = self.driver.find_elements(By.CSS_SELECTOR, "li.occludable-update")
                        for result_ext in results_ext:
                            hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                            hover_ext.perform()
                            
                            if(self.no_of_jobs > len(self.applied_job)):
                                # Retrieve the job title link
                                title_element_ext = result_ext.find_element(By.CSS_SELECTOR, 'a.job-card-container__link')
                                title_text_ext = title_element_ext.text  # Get the text of the title
                                print("Title on page", page_number, ":", title_text_ext)
                                
                                # Submit application
                                self.submit_apply(title_element_ext)
                                if(self.no_of_jobs == len(self.applied_job)):
                                    break
        

    """Submits the application for founded jobs"""
    def submit_apply(self,job_add):
        print('You are applying to the position of: ', job_add.text)
        job_add.click()
        time.sleep(2)
        
        try:
            # Find the outer container
            company_section = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name")

            # Extract the anchor tag inside it
            company_link_element = company_section.find_element(By.TAG_NAME, "a")

            # Extract name and link
            company = company_link_element.text.strip()
            link = company_link_element.get_attribute("href")

            print("Company Name:", company)
            print("Company Link:", link)
            
        except Exception as e:
            print("Error extracting company name/link:", e)
        
        job_location=""
        try:
            # Wait up to 10 seconds for the element to become present
            preference_element = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-details-preferences-and-skills__pill"))
            )
            
            job_location = preference_element.text.strip()
            print("Preference Text:", job_location)

        except Exception as e:
            print("Error extracting preference text:", e)
        
        try:
            # Wait for the "Easy Apply" button to be clickable
            easy_apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "jobs-apply-button"))
            )
            
            # Click the button
            time.sleep(2)
            easy_apply_button.click()
            print("Clicked on 'Easy Apply' button.")
            #Wait For Apply Form Load
            time.sleep(1)
            try:
                reminder_element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'artdeco-modal__header')]//h2[text()='Job search safety reminder']"))
                )
                if reminder_element.is_displayed():
                    print("\nJob search safety reminder is present.")
                    try:
                        continue_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@id='jobs-apply-button-id']//span[text()='Continue applying']"))
                        )
                        continue_button.click()
                        print("\nSuccessfully clicked on 'Continue applying' button.")
                    except Exception as e:
                        print(f"\nFailed to click 'Continue applying' button: {e}")
                        print("\nTry By Own And Press Enter.\n")
                        input("\n\nPress Enter After Clicked To Continue Apply")
            except:
                print("\nNo Job search safety reminder found.")
        
        except Exception as e:
            print(f"\nAn error occurred while clicking the 'Easy Apply' button: {e}")

        # Locate all input fields within the form
        input_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[required], select[required]')
        flag_input=0
        print("\n\nForm Input Fields : \n\n ",input_fields)
        print("\n\n Length : \n\n",len(input_fields)) 
        
        # Check each input field
        for input_field in input_fields:
            field_id = input_field.get_attribute('id')
            field_value = input_field.get_attribute('value').strip()
            
            # Check if the field is empty
            if field_value == "":    
                print(f"\n \n field_id = {field_id.capitalize()} field is empty.")
                print("\n\n DataType : ",type(field_id))
                
                if "phoneNumber" in field_id:
                    print("Found Number : \n\n")
                    time.sleep(3)
                    input_field.send_keys(self.phone_number)
                    print("Successfully Enter The number ")
                    time.sleep(5)
                    flag_input=flag_input+1
                
                if "location-GEO-LOCATION" in field_id:
                    print("Found Location : \n\n")
                    time.sleep(3)
                    input_field.send_keys(self.locations)
                    print("Successfully Enter The Location ")
                    time.sleep(5)
                    input_field.send_keys(Keys.RETURN)
                    flag_input=flag_input+1
            
            else:
                flag_input=flag_input+1
                print(f"{field_id} field is already filled with: {field_value}")
        
        if(flag_input==len(input_fields)):
            track=0
            print("Congratulation All  Fields Are Filled. \n",flag_input)
            """Check the 'Next' button."""
            try:
                # Wait for the "Next" button to be clickable
                next_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-easy-apply-next-button]"))
                )
                
                # Click the button
                next_button.click()
                print("Clicked on 'Next' button.")

            except TimeoutException:
                print("Timeout while waiting for the Next button. Continuing execution...")

            #Resume Next
            try:
                next_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Continue to next step']//span[text()='Next']"))
                )
                self.scroll_slow(next_button)
                next_button.click()
                print("\nSuccessfully clicked on 'Next' button.")
            except Exception as e:
                print(f"Failed to click 'Next' button: {e}")

            #Work Experience Next
            try:
                next_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Continue to next step']//span[text()='Next']"))
                )
                self.scroll_slow(next_button)
                next_button.click()
                print("Successfully clicked on 'Next' button.")
            except Exception as e:
                print(f"Failed to click 'Next' button: {e}")

            # Locate all input fields within the form
            input_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[required], select[required]')
            flag_input=0
            print("\n\nForm Input Fields : \n\n ",input_fields)
            print("\n\n Length : \n\n",len(input_fields)) 
            
            # Check each input field
            for input_field in input_fields:
                field_id = input_field.get_attribute('id')
                field_value = input_field.get_attribute('value').strip()
                
                # Check if the field is empty
                if field_value == "":    
                    print(f"\n \n field_id = {field_id.capitalize()} field is empty.")
                    print("\n\n DataType : ",type(field_id))
                    input_field.send_keys(0)
                    print("\nSuccessfully Enter The Zero.")
                    time.sleep(3)
                    flag_input=flag_input+1
                
                else:
                    flag_input=flag_input+1
                    print(f"{field_id} field is already filled with: {field_value}")            

            """Check the 'Review' button."""
            try:
                # Wait for the "Review" button to be clickable
                rev_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-live-test-easy-apply-review-button]"))
                )
                
                # Click the button
                rev_button.click()
                print("Clicked on 'Review' button.")
                
            except TimeoutException:
                print("Timeout while waiting for the review button. Continuing execution...")
            
            """Check the 'Submit' button."""
            try:
                # Wait for the "Review" button to be clickable
                submit_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-live-test-easy-apply-submit-button]"))
                )
                print("\n\njob_add.text == ",job_add.text)
                self.applied_job.append(job_add.text)
                print("\n\nSelf.applied_job  : ",self.applied_job)
                # Click the button
                submit_button.click()
                print("\nClicked on 'Submit' button.")
                #self.discard_application()
                self.save_to_file(job_add.text, company, job_location, link)
                time.sleep(5)
                time.sleep(5)
                
            except TimeoutException:
                print("Timeout while waiting for the Submit button. Continuing execution...")
                self.discard_application()
                pass            
            
        else:
            print("Some Filled Not Handel By Bot. Flag_Input : \n",flag_input)
            print('Not direct application, going to next...')
            self.discard_application()
        
    def avoid_lock(self):
        if self.disable_lock:
            return
        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(1.0)
        pyautogui.press('esc')

    """Discard Applications If Addition Questions"""
    def discard_application(self):
        print('Now Closing application, going to next...')
        time.sleep(5)
        try:
            # Wait for the Close button to be clickable
            discard_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-modal-close-btn]"))
            )
            
            #discard = self.driver.find_element_by_xpath("//button[@data-test-modal-close-btn]")
            discard_button.click()
            print('\nClick On Disard')
            time.sleep(1)
        
        except TimeoutException:
                print("Timeout while waiting Discard button. Continuing execution...")
        
        except NoSuchElementException:
            pass

        try:
            # Wait for the Confirm Close button to be clickable
            confirm_discard_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-dialog-secondary-btn]"))
            )
            #discard_confirm = self.driver.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
            confirm_discard_button.click()
            print('\nClick On Confirm Disard')
            time.sleep(1)
        
        except TimeoutException:
                print("Timeout while waiting Confirm Discard button. Continuing execution...")
        
        except NoSuchElementException:
            pass    
        print("\n\n\n Going To Next Application")


    """Saves the current state to the JSON file."""
    def save_to_file(self, job_title, company, job_location, link):
        file_path = self.output_file_directory + self.file_name + ".json"
        new_data = {
            "job_title": job_title,
            "company": company,
            "location": job_location,
            "link": link
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
        self.login_Linkedin()
        time.sleep(8)  # Wait for login to complete
        self.job_Search()
        time.sleep(8)
        self.easyApply()
        time.sleep(5)
        self.find_offers()
        time.sleep(3)
        self.close_session()

if __name__ == "__main__":
    #Start time
    start_time = datetime.now()
    parameters = validate_json()
    browser = init_browser()
    bot = AutoJobApplyTest(parameters, browser)
    bot.apply_Functions()
    #End time
    end_time = datetime.now()
    # Total time taken
    total_time = end_time - start_time
    print(f"\Total time taken : {total_time} ")