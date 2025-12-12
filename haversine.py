import math

# Earth's radius in kilometers (R)
R = 6371.0

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points 
    on the surface of a sphere using the Haversine formula.
    """
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # The Haversine Formula itself
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return distance

# Example Use:
# distance = haversine_distance(38.897676, -77.036530, 38.900989, -77.037415)
# print(f"Distance: {distance:.2f} km")