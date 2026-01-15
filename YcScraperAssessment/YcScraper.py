import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

# Algolia configuration
ALGOLIA_URL = "https://45bwzj1sgc-dsn.algolia.net/1/indexes/*/queries"

HEADERS = {
    "x-algolia-application-id": "45BWZJ1SGC",
    "x-algolia-api-key": "MjBjYjRiMzY0NzdhZWY0NjExY2NhZjYxMGIxYjc2MTAwNWFkNTkwNTc4NjgxYjU0YzFhYTY2ZGQ5OGY5NDMxZnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJZQ0NvbXBhbnlfcHJvZHVjdGlvbiUyMiUyQyUyMllDQ29tcGFueV9CeV9MYXVuY2hfRGF0ZV9wcm9kdWN0aW9uJTIyJTVEJnRhZ0ZpbHRlcnM9JTVCJTIyeWNkY19wdWJsaWMlMjIlNUQmYW5hbHl0aWNzVGFncz0lNUIlMjJ5Y2RjJTIyJTVE",
    "Content-Type": "application/json",
    "Origin": "https://www.ycombinator.com",
    "Referer": "https://www.ycombinator.com/",
    "User-Agent": "Mozilla/5.0"
}

# Store final results
all_companies = []

# Pagination: 25 pages × 20 ≈ 500 companies
for page in range(25):
    payload = {
        "requests": [
            {
                "indexName": "YCCompany_production",
                "params": f"hitsPerPage=20&page={page}"
            }
        ]
    }
    
    response = requests.post(ALGOLIA_URL, json=payload, headers=HEADERS)
    data = response.json()

    hits = data.get("results", [{}])[0].get("hits", [])

    for company in hits:
        name = company.get("name")
        batch = company.get("batch")
        description = company.get("one_liner")
        slug = company.get("slug")

        founder_names = []
        founder_linkedins = []

        # Visit company profile page
        if slug:
            profile_url = f"https://www.ycombinator.com/companies/{slug}"

            try:
                profile_response = requests.get(profile_url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(profile_response.text, "html.parser")

                # Each founder is inside: div.ycdc-card-new
                founder_cards = soup.find_all("div", class_="ycdc-card-new")

                for card in founder_cards:
                    # Founder name (div with font-bold)
                    name_tag = card.find("div", class_="font-bold")
                    if name_tag:
                        founder_names.append(name_tag.get_text(strip=True))

                    # LinkedIn URL
                    linkedin_tag = card.find(
                        "a",
                        href=lambda x: x and "linkedin.com/in" in x
                    )
                    if linkedin_tag:
                        founder_linkedins.append(linkedin_tag["href"])

            except Exception as e:
                print(f"Error scraping founders for {slug}: {e}")

        # Final formatting
        founders = ", ".join(sorted(set(founder_names))) if founder_names else "N/A"
        linkedin_urls = ", ".join(sorted(set(founder_linkedins))) if founder_linkedins else "N/A"

        # Append result
        all_companies.append({
            "Company Name": name,
            "Batch": batch,
            "Short Description": description,
            "Company Slug": slug,
            "Founder Name(s)": founders,
            "Founder LinkedIn URL(s)": linkedin_urls
        })

    # Rate limiting
    time.sleep(1)

df = pd.DataFrame(all_companies)

df.to_csv("yc_companies.csv", index=False)

#if you need xlsx format uncomment below
#df.to_csv("yc_companies.csv", index=False)

print("CSV file saved successfully")
