import os

import googlemaps
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

print("-"*55 + "\nGenerating Bus Route Directions!\n" + "-"*55)

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
API_KEY = os.environ["GOOGLE_MAPS_API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

# List of addresses with timestamps
addresses = [
    "873 61st Street, Brooklyn, NY 11220",
    "5214 Fourth Avenue, Brooklyn, NY 11220",
    "425 52nd Street, Brooklyn, NY 11220",
    "914 40th Street, Brooklyn, NY 11219",
    "100 Caton Avenue, Brooklyn, NY 11218",
    "143 17th Street, Brooklyn, NY 11215",
    "487 Carlton Avenue, Brooklyn, NY 11238", (AM only)
    "1229 Atlantic Avenue, Brooklyn, NY 11216", (AM only)
    "789 St Marks Avenue, Brooklyn, NY 11213",
    "1430 Bergen Street, Brooklyn, NY 11213",
    "180 Troy Avenue, Brooklyn, NY 11213",
    "1639 Carroll Street, Brooklyn, NY 11213"
]



# Function to get directions
def get_directions(gmaps, origin, destination, waypoints):
    directions_result = gmaps.directions(
        origin,
        destination,
        mode="driving",
        waypoints=waypoints,
        departure_time=datetime.now()
    )
    return directions_result

# Get the directions
origin = addresses[0]
destination = addresses[-1]
waypoints = addresses[1:-1]

directions = get_directions(gmaps, origin, destination, waypoints)

# Calculate the recommended pickup times
final_dropoff_time = datetime.strptime("08:00 AM", "%I:%M %p")
pickup_times = []

total_duration = timedelta()
for leg in reversed(directions[0]['legs']):
    leg_duration = leg['duration']['value']
    total_duration += timedelta(seconds=leg_duration)
    pickup_times.append(final_dropoff_time - total_duration)

pickup_times.reverse()

out_name = f"directions_{len(addresses)}_stops_from_{addresses[0]}_to_{addresses[-1]}"
out_path = Path(__file__).parent + out_name

# Save directions to a file
with open(out_path, "w") as f:
    print()
    for i, leg in enumerate(directions[0]['legs']):
        if i == 0:
            f.write(f"Start at: {leg['start_address']} at {pickup_times[i].strftime('%I:%M %p')}\n")
        else:
            f.write(f"{i}th Pick: {leg['start_address']} at {pickup_times[i].strftime('%I:%M %p')}\n")
        
        for step in leg['steps']:
            instructions = step['html_instructions'].replace('<div style="font-size:0.9em">', ' (').replace('</div>', ')').replace('<b>', '').replace('</b>', '').replace('<br/>', '')
            instructions = instructions.replace('&nbsp;', ' ').replace('&amp;', '&')
            distance = step['distance']['text']
            duration = step['duration']['text']
            f.write(f"{instructions} ({distance}, {duration})\n")
        
        f.write("\n")

    f.write(f"Arrive at: {directions[0]['legs'][-1]['end_address']} by 08:00 AM\n")
