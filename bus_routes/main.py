import os

from copy import deepcopy
import googlemaps
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
from pathlib import Path


print("-" * 55 + "\nGenerating Bus Route Directions!\n" + "-" * 55)


# Retrieve API key from .env file (not checked into version control)
load_dotenv()
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
    "487 Carlton Avenue, Brooklyn, NY 11238",
    "1229 Atlantic Avenue, Brooklyn, NY 11216",
    "789 St Marks Avenue, Brooklyn, NY 11213",
    "1430 Bergen Street, Brooklyn, NY 11213",
    "180 Troy Avenue, Brooklyn, NY 11213",
    "1639 Carroll Street, Brooklyn, NY 11213",
]

addresses.reverse()


def get_pickup_plan(addresses: list[str], required_at_school_by: datetime):
    origin = addresses[0]
    destination = addresses[-1]
    waypoints = addresses[1:-1]
    directions = get_directions(gmaps, origin, destination, waypoints)

    pickup_times = []
    total_duration = timedelta()
    for leg in reversed(directions[0]["legs"]):
        leg_duration = leg["duration"]["value"]
        total_duration += timedelta(seconds=leg_duration)
        pickup_times.append(required_at_school_by - total_duration)
    pickup_times.reverse()

    return directions, pickup_times


def get_dropoff_plan(addresses: list[str], pickup_from_school_at: datetime):
    addresses = deepcopy(addresses)
    addresses.reverse()

    origin = addresses[0]
    destination = addresses[-1]
    waypoints = addresses[1:-1]
    directions = get_directions(gmaps, origin, destination, waypoints)

    dropoff_times = []
    total_duration = timedelta()
    for leg in directions[0]["legs"]:
        leg_duration = leg["duration"]["value"]
        total_duration += timedelta(seconds=leg_duration)
        dropoff_times.append(pickup_from_school_at + total_duration)

    return directions, dropoff_times


# Function to get directions
def get_directions(gmaps, origin: str, destination: str, waypoints: list[str]):
    directions_result = gmaps.directions(
        origin,
        destination,
        mode="driving",
        waypoints=waypoints,
        departure_time=datetime.now(),
    )
    return directions_result


def write_plan(directions: list[str], stop_times: list[time], file_name: str | None = None):
    file_name = file_name or (
        f"directions_{len(addresses)}_stops_from_{addresses[0]}_to_{addresses[-1]}"
    )
    out_path = Path(__file__).parent.parent / "output" / file_name

    # Save directions to a file
    with open(out_path, "w") as f:
        print()
        for i, leg in enumerate(directions[0]["legs"]):
            if i == 0:
                f.write(
                    f"Start at: {leg['start_address']} at {stop_times[i].strftime('%I:%M %p')}\n"
                )
            else:
                f.write(
                    f"{i}th Pick: {leg['start_address']} at {stop_times[i].strftime('%I:%M %p')}\n"
                )

            for step in leg["steps"]:
                instructions = (
                    step["html_instructions"]
                    .replace('<div style="font-size:0.9em">', " (")
                    .replace("</div>", ")")
                    .replace("<b>", "")
                    .replace("</b>", "")
                    .replace("<br/>", "")
                    .replace("/<wbr/>", "")
                )
                instructions = instructions.replace("&nbsp;", " ").replace("&amp;", "&")
                distance = step["distance"]["text"]
                duration = step["duration"]["text"]
                f.write(f"{instructions} ({distance}, {duration})\n")

            f.write("\n")

        f.write(
            f"Arrive at: {directions[0]['legs'][-1]['end_address']} by {stop_times[-1]:%H:%M}\n"
        )


# pickup_directions, pickup_times = get_pickup_plan(
#     addresses, required_at_school_by=datetime(2024, 9, 1, 8)
# )
# 
# write_plan(pickup_directions, pickup_times, "am_pickup.txt")

pm_only_addresses = [
    addr
    for addr in addresses
    if addr
    not in {
        "487 Carlton Avenue, Brooklyn, NY 11238",
        "1229 Atlantic Avenue, Brooklyn, NY 11216",
    }
]
dropoff_directions, dropoff_times = get_dropoff_plan(
    pm_only_addresses, pickup_from_school_at=datetime(2024, 9, 1, 15)
)

write_plan(dropoff_directions, dropoff_times, "pm_dropoff.txt")
