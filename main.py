# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import os
import json
import datetime


LEADS_FILE = 'leads.json'

def load_leads():
    """Loads leads data from the central JSON file."""
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_leads(leads_data):
    """Saves leads data to the central JSON file."""
    with open(LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads_data, f, ensure_ascii=False, indent=4)
    print(f"Leads data saved to {LEADS_FILE}")


def _fetch_url(url):
    """Shared function to fetch URL content with a standard user-agent."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

class WebsiteScanner:
    """Scans a company website to extract basic OSINT data."""
    def __init__(self, company_name):
        self.company_name = company_name
        self.website_url = None
        self.website_content = None
        self.social_links = []
        self.emails = []

    def find_website(self):
        """Searches for a company's website and sets the website_url."""
        print(f"Searching for website for '{self.company_name}'...")
        search_url = f"https://duckduckgo.com/html/?q={self.company_name} official website"
        html_content = _fetch_url(search_url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            result_link = soup.find('a', class_='result__a')
            if result_link:
                self.website_url = result_link['href']
                print(f"Found website: {self.website_url}")
                return self.website_url
        print("Could not find website.")
        return None

    def scan_website(self):
        """Fetches and scans the content of the company's website."""
        if not self.website_url:
            print("Cannot scan website, no URL found.")
            return False
        
        print("Fetching and scanning website content...")
        self.website_content = _fetch_url(self.website_url)
        if not self.website_content:
            return False

        self._extract_social_media_links()
        self._extract_emails()
        return True

    def _extract_social_media_links(self):
        if not self.website_content: return
        links = [a.get('href', '') for a in BeautifulSoup(self.website_content, 'html.parser').find_all('a')]
        patterns = {
            'x_twitter_url': r"https?://(www\.)?twitter\.com/.*",
            'x_linkedin_url': r"https?://(www\.)?linkedin\.com/company/.*",
            'x_facebook_url': r"https?://(www\.)?facebook\.com/.*",
            'x_instagram_url': r"https?://(www\.)?instagram\.com/.*",
            'x_github_url': r"https?://(www\.)?github\.com/.*",
        }
        
        # Use a dictionary to store one link per platform to avoid ambiguity
        found_links = {}
        for link in links:
            for key, pattern in patterns.items():
                if key not in found_links and re.match(pattern, link):
                    found_links[key] = link
                    break # Move to next link once a pattern is matched
        
        self.social_links = found_links
        print(f"Found {len(self.social_links)} unique social media links.")

    def _extract_emails(self):
        if not self.website_content: return
        self.emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", self.website_content)))
        print(f"Found {len(self.emails)} unique email addresses.")

class TwitterScanner:
    """
    Scrapes a Twitter profile for basic information.
    NOTE: This is highly fragile and likely to break.
    """
    def __init__(self, twitter_url):
        self.url = twitter_url.split('?')[0].strip('/')
        self.handle = self.url.split('/')[-1]

    def scrape_profile(self):
        print(f"\n--- Scraping Twitter Profile: {self.handle} ---")
        content = _fetch_url(self.url)
        if not content:
            print("Failed to fetch Twitter page.")
            return None

        profile_data = {'x_twitter_handle': self.handle}
        try:
            soup = BeautifulSoup(content, 'html.parser')
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                data = json.loads(script.string)
                if data.get('@type') == 'Person':
                    profile_data['x_twitter_description'] = data.get('description')
                    followers = data.get('interactionStatistic', [{}])[0].get('userInteractionCount')
                    if followers:
                        profile_data['x_twitter_followers'] = followers
                    return profile_data
        except (json.JSONDecodeError, IndexError):
            pass # Fallback to basic scraping

        try:
            soup = BeautifulSoup(content, 'html.parser')
            description = soup.find('meta', {'name': 'description'})
            if description:
                profile_data['x_twitter_description'] = description.get('content')
            return profile_data
        except Exception as e:
            print(f"Basic scraping for {self.handle} also failed. Error: {e}")
            
        return None

class GoogleDorker:
    """Performs Google Dork searches to find related information."""
    def __init__(self, target):
        self.target = target

    def search(self, dork_query):
        print(f"Executing Google Dork: '{dork_query}'")
        search_url = f"https://duckduckgo.com/html/?q={dork_query}"
        html_content = _fetch_url(search_url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            return [a['href'] for a in soup.find_all('a', class_='result__a')]
        return []

    def find_employees(self):
        """Finds potential employee profiles on LinkedIn."""
        return self.search(f'site:linkedin.com/in -intitle:"profiles" "{self.target}"')
def generate_email_content(lead_data, prompt):
    """
    Placeholder for AI-driven email content generation.
    In a real scenario, this would call an LLM API (e.g., Gemini, OpenAI)
    to generate personalized email content based on lead_data and the prompt.
    """
    company_name = lead_data.get('company_name', 'Company')
    email_subject = f"Follow-up for {company_name}: {prompt}"
    email_body = f"""
Dear {company_name} Team,

I hope this email finds you well.

Regarding your interest in {prompt}, our team has analyzed some key aspects
of your online presence and market position.

Here are some insights from our OSINT analysis:
- Website: {lead_data.get('osint_data', {}).get('website', 'N/A')}
- Social Links: {', '.join(lead_data.get('osint_data', {}).get('social_links', {}).values()) or 'N/A'}
- Emails found: {', '.join(lead_data.get('osint_data', {}).get('emails', [])) or 'N/A'}

Based on your profile, we believe our solutions could significantly benefit your operations in the area of {prompt}.

We would love to discuss how we can help you further.

Best regards,

Your AI Marketing Assistant
"""
    print(f"\n--- AI Generated Email Content for {company_name} ---")
    print(f"Subject: {email_subject}")
    print(f"Body:\n{email_body}")
    return {"subject": email_subject, "body": email_body}


def send_email(to_email, subject, body):
    """
    Placeholder for sending emails.
    In a real scenario, this would integrate with an email service provider (ESP)
    like SendGrid, Mailgun, or a local SMTP server.
    """
    print(f"\n--- Sending Email to: {to_email} ---")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print("-------------------------------------")
    # Simulate success
    return True


def handle_incoming_email(email_content, lead_data):
    """
    Placeholder for reading and responding to emails.
    In a real scenario, this would involve connecting to an email inbox (IMAP/POP3),
    parsing emails, identifying the sender/lead, and using AI to generate a response.
    """
    print(f"\n--- Handling Incoming Email ---")
    print(f"Received Email Content: {email_content[:100]}...") # Print first 100 chars
    
    # In a real system, you'd match the email to a specific lead.
    # For this placeholder, we assume lead_data is already the correct lead.

    lead_data['email_interactions'].append({
        'type': 'incoming',
        'timestamp': datetime.datetime.now().isoformat(),
        'content': email_content
    })
    print(f"Updated email interactions for lead: {lead_data.get('company_name', 'Unknown Lead')}")

    # Simulate AI generating a response
    response_prompt = f"Reply to an email from {lead_data.get('company_name', 'Unknown')} about their inquiry. Original email: {email_content[:200]}"
    ai_response = generate_email_content(lead_data, response_prompt)
    
    # In a real system, you would then send this response
    print(f"\n--- AI Generated Response for {lead_data.get('company_name', 'Unknown')} ---")
    print(f"Subject: {ai_response['subject']}")
    print(f"Body:\n{ai_response['body']}")

    return True


def run_osint_for_company(company_name, lead_osint_data):
    """
    Orchestrates the full OSINT process for a single company and stores data locally.
    """
    print(f"\n{'='*40}\nRunning OSINT for: {company_name}\n{'='*40}")
    
    # Initialize basic data if not already present
    lead_osint_data.setdefault('company_name', company_name)
    lead_osint_data.setdefault('website', None)
    lead_osint_data.setdefault('social_links', {})
    lead_osint_data.setdefault('emails', [])
    lead_osint_data.setdefault('twitter_profile', {})
    lead_osint_data.setdefault('google_dork_results', {})
    
    scanner = WebsiteScanner(company_name)
    website = scanner.find_website()

    if website:
        lead_osint_data['website'] = website

    if website:
        scanner.scan_website()
        if scanner.social_links:
            lead_osint_data['social_links'].update(scanner.social_links)
        if scanner.emails:
            lead_osint_data['emails'] = scanner.emails
    
    # Scan Social Media Profiles and add to update data
    if 'x_twitter_url' in lead_osint_data['social_links']:
        twitter_scanner = TwitterScanner(lead_osint_data['social_links']['x_twitter_url'])
        profile_data = twitter_scanner.scrape_profile()
        if profile_data:
            print("Scraped Twitter Data:", json.dumps(profile_data, indent=2))
            lead_osint_data['twitter_profile'].update(profile_data)

    # Perform Google Dorking (informational for now)
    print("\n--- Performing Google Dorking ---")
    dorker = GoogleDorker(company_name)
    employees = dorker.find_employees()
    if employees:
        print(f"\nFound {len(employees)} potential employee profiles on LinkedIn (Top 5):")
        for employee_link in employees[:5]: print(employee_link)
        lead_osint_data['google_dork_results']['linkedin_employees'] = employees[:5]
    
    print(f"\n--- OSINT data for {company_name} updated in leads data structure. ---")
    # No return value needed as lead_osint_data is modified in place



if __name__ == '__main__':
    targets = ["SAP", "Microsoft", "Salesforce"]
    
    leads = load_leads() # Load existing leads
    
    for company_name in targets:
        # Check if the company already exists as a lead, if not, create a basic entry
        if company_name not in leads:
            leads[company_name] = {
                'company_name': company_name,
                'osint_data': {},
                'psychoprofile': {}, # Placeholder
                'email_interactions': [] # Placeholder
            }
        
        # Run OSINT and update the lead's osint_data
        run_osint_for_company(company_name, leads[company_name]['osint_data'])
        
    save_leads(leads) # Save all leads after processing
    print(f"\n{'='*40}\nOSINT process completed and all leads saved.\n{'='*40}")