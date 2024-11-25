import googlemaps # type: ignore

# Initialize the client with your API key
gmaps = googlemaps.Client(key='AIzaSyAhagodsFfVLkHh952Qc31OyC7wO0DXf7c')

# Define the locations
origin = "Undi"
destination = "Bhimavaram"

# Get the distance matrix result
result = gmaps.distance_matrix(origin, destination)

# Parse the response to extract distance and duration
distance = result['rows'][0]['elements'][0]['distance']['text']
duration = result['rows'][0]['elements'][0]['duration']['text']

# Print the results
print(f"Distance: {distance}")
print(f"Duration: {duration}")
