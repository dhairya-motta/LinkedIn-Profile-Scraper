# LinkedIn Profile Scraper

This project is a web scraper that extracts information from LinkedIn profiles and outputs the data into a structured CSV file.

## Disclaimer

Web scraping LinkedIn may violate their Terms of Service. This code is provided for educational purposes only. Use at your own risk and responsibility. Consider using LinkedIn's official API for production use.

## Features

- Extracts profile information including:
  - Name
  - Bio/Headline
  - Social media links
  - Experience
  - Education
  - Certifications (bonus)
  - Projects (bonus)
- Handles multiple profiles from an Excel file
- Outputs data to a structured CSV file
- Includes error handling and logging

## Requirements

- Python 3.6+
- Required Python packages:
  - selenium
  - beautifulsoup4
  - pandas
  - webdriver_manager

## Installation

1. Clone this repository or download the files.
2. Install the required Python packages:

```bash
pip install selenium beautifulsoup4 pandas webdriver_manager
```

3. Make sure you have Chrome browser installed (the script uses ChromeDriver).

## Configuration

Before running the script, you need to:

1. Open `scraper.py` and replace the placeholder LinkedIn credentials with your own:

```python
EMAIL = "your_email@example.com"  # Replace with your LinkedIn email
PASSWORD = "your_password"  # Replace with your LinkedIn password
```

2. Prepare your input Excel file (`Assignment.xlsx`) with LinkedIn profile URLs in the first column.

## Usage

Run the script with:

```bash
python scraper.py
```

The script will:
1. Log in to LinkedIn using your credentials
2. Read the LinkedIn profile URLs from the Excel file
3. Visit each profile and extract the required information
4. Save the data to `scraped_output.csv`

## Output Format

The output CSV file contains the following columns:

- LinkedIn URL: The URL of the profile
- Name: The person's name
- Bio: The person's headline or bio
- Socials: JSON string of social media links (e.g., `{"Twitter": "@johndoe", "GitHub": "johndoe"}`)
- Experience: JSON string of company-role pairs (e.g., `{"Google": "Senior AI Engineer", "Microsoft": "ML Engineer"}`)
- Education: JSON string of institution-degree pairs (e.g., `{"IIT Madras": "MS in AI", "Anna University": "BTech in CS"}`)
- Certifications: JSON string of issuer-certification pairs
- Projects: JSON string of project title-description pairs

## Error Handling

The script includes comprehensive error handling:

- Logs all activities and errors to both console and a log file (`scraper.log`)
- Continues processing other profiles if one fails
- Records empty data for failed profiles in the output CSV

## Limitations

- LinkedIn actively tries to prevent scraping, so the script may stop working if LinkedIn changes its page structure
- The script may be detected as automated activity, which could lead to temporary IP blocks or account restrictions
- Some profiles may have custom layouts that the scraper doesn't handle correctly

## Improvements

Potential improvements for the script:

- Add proxy support to avoid IP blocks
- Implement more sophisticated browser fingerprinting to avoid detection
- Add support for different LinkedIn page layouts
- Implement multithreading for faster scraping (use with caution)
- Add more detailed error reporting and recovery mechanisms

## License

This project is for educational purposes only. Use responsibly and ethically.
