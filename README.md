# RestAPI
## GET
get flight details
 - {{base_url}}/flights/flight_id 
 - example: http://127.0.0.1:8000/flights/B12
## POST
update/add flight, assuming that flight id is uniqe for all the flights in the files. (If not we can remove the flag "remove_duplicate" to allow multiple flight ids)
 - {{base_url}}/flights/
 - data:
```
    flightID: str
    arrival: str
    departure: str
```
