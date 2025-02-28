"""
LinkedIn Profile Scraper

This script extracts information from LinkedIn profiles and outputs the data to a CSV file.
It uses Selenium for browser automation and BeautifulSoup for HTML parsing.

Requirements:
- Python 3.6+
- Selenium
- BeautifulSoup4
- pandas
- webdriver_manager

Usage:
1. Install dependencies: pip install selenium beautifulsoup4 pandas webdriver_manager
2. Set your LinkedIn credentials in the script
3. Run the script: python scraper.py
"""

import os
import time
import csv
import json
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, email, password, headless=True):
        """
        Initialize the LinkedIn scraper with login credentials.
        
        Args:
            email (str): LinkedIn login email
            password (str): LinkedIn login password
            headless (bool): Whether to run the browser in headless mode
        """
        self.email = email
        self.password = password
        self.driver = self._setup_driver(headless)
        self.is_logged_in = False
        
    def _setup_driver(self, headless):
        """Set up the Selenium WebDriver with appropriate options."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Use webdriver_manager to handle driver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def login(self):
        """Log in to LinkedIn."""
        try:
            logger.info("Logging in to LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for the login page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter credentials
            self.driver.find_element(By.ID, "username").send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-identity-module"))
            )
            
            logger.info("Successfully logged in to LinkedIn")
            self.is_logged_in = True
            
        except TimeoutException:
            logger.error("Timeout while logging in. Check your internet connection or LinkedIn might be detecting automation.")
            raise
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise
    
    def scrape_profile(self, profile_url):
        """
        Scrape a LinkedIn profile and extract relevant information.
        
        Args:
            profile_url (str): URL of the LinkedIn profile to scrape
            
        Returns:
            dict: Dictionary containing the extracted profile information
        """
        if not self.is_logged_in:
            self.login()
        
        profile_data = {
            "LinkedIn URL": profile_url,
            "Name": "",
            "Bio": "",
            "Socials": {},
            "Experience": {},
            "Education": {},
            "Certifications": {},
            "Projects": {}
        }
        
        try:
            logger.info(f"Scraping profile: {profile_url}")
            self.driver.get(profile_url)
            
            # Wait for the profile page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card"))
            )
            
            # Add a small delay to ensure the page is fully loaded
            time.sleep(2)
            
            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Extract name
            try:
                name_element = soup.select_one(".pv-top-card .text-heading-xlarge")
                if name_element:
                    profile_data["Name"] = name_element.get_text().strip()
            except Exception as e:
                logger.warning(f"Error extracting name: {str(e)}")
            
            # Extract bio/headline
            try:
                bio_element = soup.select_one(".pv-top-card .text-body-medium")
                if bio_element:
                    profile_data["Bio"] = bio_element.get_text().strip()
            except Exception as e:
                logger.warning(f"Error extracting bio: {str(e)}")
            
            # Extract social links
            try:
                social_links = soup.select(".pv-contact-info__contact-type a")
                for link in social_links:
                    link_text = link.get_text().strip()
                    link_url = link.get("href")
                    if "twitter" in link_url.lower():
                        profile_data["Socials"]["Twitter"] = link_text
                    elif "github" in link_url.lower():
                        profile_data["Socials"]["GitHub"] = link_text
                    elif "facebook" in link_url.lower():
                        profile_data["Socials"]["Facebook"] = link_text
                    elif "instagram" in link_url.lower():
                        profile_data["Socials"]["Instagram"] = link_text
                    elif "website" in link_url.lower() or "portfolio" in link_url.lower():
                        profile_data["Socials"]["Website"] = link_url
            except Exception as e:
                logger.warning(f"Error extracting social links: {str(e)}")
            
            # Click "Show more" buttons to expand sections
            self._expand_sections()
            
            # Re-parse the page after expanding sections
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Extract experience
            try:
                experience_section = soup.select_one("#experience-section")
                if experience_section:
                    experience_items = experience_section.select("li.pv-entity__position-group-pager")
                    for item in experience_items:
                        company_element = item.select_one(".pv-entity__secondary-title")
                        role_element = item.select_one(".pv-entity__primary-title")
                        
                        if company_element and role_element:
                            company = company_element.get_text().strip()
                            role = role_element.get_text().strip()
                            profile_data["Experience"][company] = role
            except Exception as e:
                logger.warning(f"Error extracting experience: {str(e)}")
            
            # Extract education
            try:
                education_section = soup.select_one("#education-section")
                if education_section:
                    education_items = education_section.select("li.pv-education-entity")
                    for item in education_items:
                        school_element = item.select_one(".pv-entity__school-name")
                        degree_element = item.select_one(".pv-entity__degree-name .pv-entity__comma-item")
                        
                        if school_element:
                            school = school_element.get_text().strip()
                            degree = degree_element.get_text().strip() if degree_element else ""
                            profile_data["Education"][school] = degree
            except Exception as e:
                logger.warning(f"Error extracting education: {str(e)}")
            
            # Extract certifications (bonus)
            try:
                certifications_section = soup.select_one("#certifications-section")
                if certifications_section:
                    certification_items = certifications_section.select("li.pv-certification-entity")
                    for item in certification_items:
                        name_element = item.select_one(".pv-certification-name")
                        issuer_element = item.select_one(".pv-certification-entity__issuer")
                        
                        if name_element and issuer_element:
                            cert_name = name_element.get_text().strip()
                            issuer = issuer_element.get_text().strip()
                            profile_data["Certifications"][issuer] = cert_name
            except Exception as e:
                logger.warning(f"Error extracting certifications: {str(e)}")
            
            # Extract projects (bonus)
            try:
                projects_section = soup.select_one("#projects-section")
                if projects_section:
                    project_items = projects_section.select("li.pv-accomplishment-entity")
                    for item in project_items:
                        title_element = item.select_one(".pv-accomplishment-entity__title")
                        description_element = item.select_one(".pv-accomplishment-entity__description")
                        
                        if title_element:
                            title = title_element.get_text().strip()
                            description = description_element.get_text().strip() if description_element else ""
                            profile_data["Projects"][title] = description
            except Exception as e:
                logger.warning(f"Error extracting projects: {str(e)}")
            
            logger.info(f"Successfully scraped profile: {profile_url}")
            return profile_data
            
        except TimeoutException:
            logger.error(f"Timeout while scraping profile: {profile_url}")
            return profile_data
        except Exception as e:
            logger.error(f"Error scraping profile {profile_url}: {str(e)}")
            return profile_data
    
    def _expand_sections(self):
        """Click 'Show more' buttons to expand all sections."""
        try:
            # Find and click all "Show more" buttons
            show_more_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".pv-profile-section__see-more-inline")
            for button in show_more_buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.5)  # Small delay after each click
                except Exception:
                    pass  # Ignore if a button can't be clicked
                    
            # Expand contact info
            try:
                contact_info_button = self.driver.find_element(By.CSS_SELECTOR, ".pv-top-card--list-bullet a")
                self.driver.execute_script("arguments[0].click();", contact_info_button)
                time.sleep(1)  # Wait for the modal to open
            except Exception:
                pass  # Ignore if contact info can't be expanded
                
        except Exception as e:
            logger.warning(f"Error expanding sections: {str(e)}")
    
    def scrape_profiles_from_excel(self, excel_file, output_csv="scraped_output.csv"):
        """
        Scrape multiple LinkedIn profiles from an Excel file.
        
        Args:
            excel_file (str): Path to the Excel file containing LinkedIn profile URLs
            output_csv (str): Path to the output CSV file
        """
        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)
            
            # Get the column containing LinkedIn URLs
            url_column = df.columns[0]  # Assuming URLs are in the first column
            profile_urls = df[url_column].tolist()
            
            # Create/open the output CSV file
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["LinkedIn URL", "Name", "Bio", "Socials", "Experience", "Education", "Certifications", "Projects"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Scrape each profile
                for url in profile_urls:
                    try:
                        profile_data = self.scrape_profile(url)
                        
                        # Convert dictionaries to strings for CSV
                        for field in ["Socials", "Experience", "Education", "Certifications", "Projects"]:
                            profile_data[field] = json.dumps(profile_data[field])
                        
                        # Write to CSV
                        writer.writerow(profile_data)
                        
                        # Add a delay between requests to avoid rate limiting
                        time.sleep(3)
                        
                    except Exception as e:
                        logger.error(f"Error processing URL {url}: {str(e)}")
                        
                        # Write empty data for failed profiles
                        empty_data = {
                            "LinkedIn URL": url,
                            "Name": "",
                            "Bio": "",
                            "Socials": "{}",
                            "Experience": "{}",
                            "Education": "{}",
                            "Certifications": "{}",
                            "Projects": "{}"
                        }
                        writer.writerow(empty_data)
            
            logger.info(f"Scraping completed. Results saved to {output_csv}")
            
        except Exception as e:
            logger.error(f"Error scraping profiles from Excel: {str(e)}")
            raise
        finally:
            self.close()
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

def main():
    """Main function to run the LinkedIn scraper."""
    # LinkedIn credentials
    EMAIL = "your_email@example.com"  # Replace with your LinkedIn email
    PASSWORD = "your_password"  # Replace with your LinkedIn password
    
    # Input and output files
    EXCEL_FILE = "Assignment.xlsx"
    OUTPUT_CSV = "scraped_output.csv"
    
    # Create and run the scraper
    try:
        scraper = LinkedInScraper(EMAIL, PASSWORD, headless=False)  # Set headless=True for production
        scraper.scrape_profiles_from_excel(EXCEL_FILE, OUTPUT_CSV)
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    main()
