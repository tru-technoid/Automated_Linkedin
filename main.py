from selenium import webdriver
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

class AutoJobApplyTest:
    def __init__(self, data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.phone_number = data['phone_number']
        self.applied_job = []
        self.no_of_jobs = data['no_of_jobs']
        service = Service(data['driver_path'])
        self.driver = webdriver.Chrome(service=service)
    
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
        if(current_Page_adrs != "https://www.linkedin.com/feed/?trk=guest_homepage-basic_nav-header-signin" or current_Page_adrs != "https://www.linkedin.com/feed/" ):            
            try:
                check_Security = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'input__email_verification_pin')]"))
                )           
                print("Prints : ",check_Security)
            
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
            return  # Exit the method if the link is not found

        # Wait for the search input fields to be present
        try:
            search_Keyword = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-keyword')]"))
            )
            search_Keyword.clear()
            search_Keyword.send_keys(self.keywords)

            search_Location = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-location')]"))
            )
            search_Location.clear()
            search_Location.send_keys(self.location)
            time.sleep(3)
            search_Location.send_keys(Keys.RETURN)
            time.sleep(5)

        except TimeoutException:
            print("Timeout while waiting for the search input fields.")

    """To Select Or Apply Filters"""
    def easyApply(self):
        #Click on the "Easy Apply" filter button
        easy_apply_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='searchFilter_applyWithLinkedin']"))
        )
        easy_apply_button.click()
        time.sleep(5)
       
        try:
            # Click on the Experience level dropdown button
            experience_dropdown = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "searchFilter_experience"))
            )
            experience_dropdown.click()
            
            time.sleep(3)
            print("\n\n\n Cliked On Experience \n\n\n")
            
            # Wait for the dropdown options to be visible
            entry_level_checkbox = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='experience-2']"))
            )
            entry_level_checkbox.click()  
            
            print("\n\n\n Cliked On Entry Checkbox \n\n\n")
            time.sleep(4)  
            
            try:
                show_results_button = WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label,'Apply current filter to show')]"))
                )
                show_results_button.click()  # Click the button
                print("Clicked on the dynamic Show results button id found : \n\n",show_results_button)
            
            except TimeoutException:
                show_results_button = False
                print("Timeout while waiting for the dynamic Show results button to be clickable.")                    
        
        except TimeoutException:
            print("Timeout while waiting for elements.")
        
        except ElementNotInteractableException:
            print("One of the elements is not interactable.")
    
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
            # Wait for the "Easy Apply" button to be clickable
            easy_apply_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "jobs-apply-button"))
            )
            
            # Click the button
            time.sleep(2)
            easy_apply_button.click()
            print("Clicked on 'Easy Apply' button.")
            #Wait For Apply Form Load
        
        except Exception as e:
            print(f"An error occurred while clicking the 'Easy Apply' button: {e}")

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
                    input_field.send_keys(self.location)
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
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-easy-apply-next-button]"))
                )
                
                # Click the button
                next_button.click()
                print("Clicked on 'Next' button.")

            except TimeoutException:
                print("Timeout while waiting for the Next button. Continuing execution...")
                
            """Check the 'Review' button."""
            try:
                # Wait for the "Review" button to be clickable
                rev_button = WebDriverWait(self.driver, 5).until(
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
                print("Clicked on 'Submit' button.")
                #self.discard_application()
                time.sleep(5)
                
            except TimeoutException:
                print("Timeout while waiting for the Submit button. Continuing execution...")
                self.discard_application()
                pass            
            
        else:
            print("Some Filled Not Handel By Bot. Flag_Input : \n",flag_input)
            print('Not direct application, going to next...')
            self.discard_application()
        
        
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
    def save_to_file(self, file_path):
        data = {
            'email': self.email,
            'password': self.password,
            'keywords': self.keywords,
            'location': self.location,
            'driver_path': self.driver.service.path,  # Update driver path if needed
            'phone_number': self.phone_number,
            'applied_job': self.applied_job
        }
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print("\nData Updated Sucessfully To Json File.")

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
        time.sleep(4)
        self.save_to_file('updated_config.json')
        time.sleep(3)
        self.close_session()

if __name__ == "__main__":
    with open("config.json") as config_file:
        data = json.load(config_file)   
    bot = AutoJobApplyTest(data)
    bot.apply_Functions()