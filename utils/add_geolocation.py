#!/usr/bin/env python3
"""
Add latitude/longitude coordinates to company headquarters.
Uses a mapping of known US tech hub locations.
"""

import json
from pathlib import Path

# Known city coordinates (major US tech/business hubs)
CITY_COORDINATES = {
    # California
    "Mountain View, California": (37.3861, -122.0839),
    "Cupertino, California": (37.3230, -122.0322),
    "San Francisco, California": (37.7749, -122.4194),
    "San Jose, California": (37.3382, -121.8863),
    "Palo Alto, California": (37.4419, -122.1430),
    "Santa Clara, California": (37.3541, -121.9552),
    "Los Angeles, California": (34.0522, -118.2437),
    "San Diego, California": (32.7157, -117.1611),
    "Irvine, California": (33.6846, -117.8265),
    "Burbank, California": (34.1808, -118.3090),
    "Sunnyvale, California": (37.3688, -122.0363),
    "Menlo Park, California": (37.4530, -122.1817),
    "Foster City, California": (37.5585, -122.2711),
    "Beaverton, Oregon": (45.4871, -122.8037),

    # Pacific Northwest
    "Seattle, Washington": (47.6062, -122.3321),
    "Redmond, Washington": (47.6740, -122.1215),
    "Bellevue, Washington": (47.6101, -122.2015),

    # Texas
    "Austin, Texas": (30.2672, -97.7431),
    "Dallas, Texas": (32.7767, -96.7970),
    "Houston, Texas": (29.7604, -95.3698),
    "Irving, Texas": (32.8140, -96.9489),
    "Plano, Texas": (33.0198, -96.6989),
    "Round Rock, Texas": (30.5083, -97.6789),

    # Northeast
    "New York, New York": (40.7128, -74.0060),
    "New York City, New York": (40.7128, -74.0060),
    "Boston, Massachusetts": (42.3601, -71.0589),
    "Cambridge, Massachusetts": (42.3736, -71.1097),
    "Philadelphia, Pennsylvania": (39.9526, -75.1652),
    "Pittsburgh, Pennsylvania": (40.4406, -79.9959),
    "Newark, New Jersey": (40.7357, -74.1724),
    "Stamford, Connecticut": (41.0534, -73.5387),
    "Hartford, Connecticut": (41.7658, -72.6734),
    "Providence, Rhode Island": (41.8240, -71.4128),

    # Midwest
    "Chicago, Illinois": (41.8781, -87.6298),
    "Detroit, Michigan": (42.3314, -83.0458),
    "Dearborn, Michigan": (42.3223, -83.1763),
    "Minneapolis, Minnesota": (44.9778, -93.2650),
    "Columbus, Ohio": (39.9612, -82.9988),
    "Cincinnati, Ohio": (39.1031, -84.5120),
    "Indianapolis, Indiana": (39.7684, -86.1581),
    "Milwaukee, Wisconsin": (43.0389, -87.9065),
    "St. Louis, Missouri": (38.6270, -90.1994),

    # Southeast
    "Atlanta, Georgia": (33.7490, -84.3880),
    "Charlotte, North Carolina": (35.2271, -80.8431),
    "Raleigh, North Carolina": (35.7796, -78.6382),
    "Durham, North Carolina": (35.9940, -78.8986),
    "Miami, Florida": (25.7617, -80.1918),
    "Tampa, Florida": (27.9506, -82.4572),
    "Jacksonville, Florida": (30.3322, -81.6557),
    "Nashville, Tennessee": (36.1627, -86.7816),
    "Memphis, Tennessee": (35.1495, -90.0490),
    "Richmond, Virginia": (37.5407, -77.4360),
    "Washington, D.C.": (38.9072, -77.0369),
    "Bethesda, Maryland": (38.9847, -77.0947),
    "Baltimore, Maryland": (39.2904, -76.6122),

    # Mountain/Southwest
    "Denver, Colorado": (39.7392, -104.9903),
    "Phoenix, Arizona": (33.4484, -112.0740),
    "Salt Lake City, Utah": (40.7608, -111.8910),
    "Las Vegas, Nevada": (36.1699, -115.1398),
    "Albuquerque, New Mexico": (35.0844, -106.6504),

    # Other
    "Omaha, Nebraska": (41.2565, -95.9345),
    "Des Moines, Iowa": (41.5868, -93.6250),
    "Kansas City, Missouri": (39.0997, -94.5786),
    "Louisville, Kentucky": (38.2527, -85.7585),
    "Oklahoma City, Oklahoma": (35.4676, -97.5164),
    "Tulsa, Oklahoma": (36.1540, -95.9928),
    "Bentonville, Arkansas": (36.3729, -94.2088),
    "Little Rock, Arkansas": (34.7465, -92.2896),
    "Birmingham, Alabama": (33.5186, -86.8104),
}

def get_coordinates(headquarters: str) -> tuple:
    """
    Get lat/lng for a headquarters location.
    Tries exact match first, then partial match.
    """
    if not headquarters:
        return None, None

    # Clean up the string
    hq_clean = headquarters.replace(", USA", "").strip()

    # Try exact match
    if hq_clean in CITY_COORDINATES:
        return CITY_COORDINATES[hq_clean]

    # Try partial match (city name)
    for city, coords in CITY_COORDINATES.items():
        if city.split(",")[0] in hq_clean:
            return coords

    # Try state match for less common cities
    for city, coords in CITY_COORDINATES.items():
        state = city.split(",")[-1].strip()
        if state in hq_clean:
            # Return state capital or major city as approximation
            return coords

    return None, None

def add_geolocation_to_data():
    """Add lat/lng to each company in the enriched dataset."""
    data_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"

    with open(data_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    updated = 0
    missing = []

    for company in companies:
        hq = company.get('headquarters', '')
        lat, lng = get_coordinates(hq)

        if lat and lng:
            company['latitude'] = lat
            company['longitude'] = lng
            updated += 1
        else:
            missing.append((company.get('company', 'Unknown'), hq))

    # Save updated data
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    print(f"✓ Added geolocation to {updated} companies")

    if missing:
        print(f"\n⚠️  Missing coordinates for {len(missing)} companies:")
        for name, hq in missing:
            print(f"   - {name}: {hq}")

    return updated, missing

if __name__ == "__main__":
    add_geolocation_to_data()
