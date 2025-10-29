"""
PHIVOLCS Earthquake Data Scraper
Scrapes earthquake data from PHIVOLCS website since JSON API is no longer available
"""

import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_phivolcs_earthquakes():
    """
    Scrape latest earthquake data from PHIVOLCS website
    Returns data in the same format as the old JSON API
    """
    try:
        url = "https://earthquake.phivolcs.dost.gov.ph/"
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all tables on the page
        tables = soup.find_all('table')

        earthquakes = []

        # Look for the table with earthquake data (typically table with most rows)
        for table in tables:
            rows = table.find_all('tr')

            # Skip small tables
            if len(rows) < 10:
                continue

            # Check if this is the earthquake data table by looking at headers
            header_row = rows[0] if rows else None
            if header_row:
                headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]

                # Check if this looks like the earthquake table
                if len(headers) >= 6 and ('Date' in headers[0] or 'Latitude' in str(headers)):
                    # Process data rows
                    for row in rows[1:]:  # Skip header row
                        cells = row.find_all('td')

                        if len(cells) >= 6:
                            try:
                                # Extract data based on column positions
                                # Column 0: Date-Time
                                # Column 1: Latitude
                                # Column 2: Longitude
                                # Column 3: Depth
                                # Column 4: Magnitude
                                # Column 5: Location

                                datetime_text = cells[0].get_text(strip=True)
                                latitude = cells[1].get_text(strip=True)
                                longitude = cells[2].get_text(strip=True)
                                depth = cells[3].get_text(strip=True)
                                magnitude = cells[4].get_text(strip=True)
                                location = cells[5].get_text(strip=True)

                                # Parse date and time
                                # Format: "29 October 2025 - 08:26 AM"
                                date_str = ""
                                time_str = "00:00:00"

                                if ' - ' in datetime_text:
                                    parts = datetime_text.split(' - ')
                                    date_str = parts[0].strip()
                                    if len(parts) > 1:
                                        time_str = parts[1].strip()

                                # Format depth to include 'kilometers'
                                depth_formatted = f"{depth} kilometers"

                                earthquake = {
                                    'date': date_str,
                                    'time': time_str,
                                    'latitude': latitude,
                                    'longitude': longitude,
                                    'depth': depth_formatted,
                                    'magnitude': magnitude,
                                    'location': location
                                }
                                earthquakes.append(earthquake)

                            except Exception as e:
                                logging.debug(f"Error parsing row: {e}")
                                continue

        if earthquakes:
            logging.info(f"Scraped {len(earthquakes)} earthquakes from PHIVOLCS")
            return {'earthquakes': earthquakes}
        else:
            logging.warning("No earthquake data found on PHIVOLCS website")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error scraping PHIVOLCS website: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error scraping PHIVOLCS: {e}")
        return None


if __name__ == '__main__':
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    data = scrape_phivolcs_earthquakes()

    if data:
        print(f"\nFound {len(data['earthquakes'])} earthquakes:")
        for i, eq in enumerate(data['earthquakes'][:5], 1):
            print(f"\n{i}. {eq['date']} {eq['time']}")
            print(f"   Location: {eq['location']}")
            print(f"   Magnitude: {eq['magnitude']}")
            print(f"   Coordinates: {eq['latitude']}, {eq['longitude']}")
            print(f"   Depth: {eq['depth']}")
    else:
        print("Failed to scrape earthquake data")
