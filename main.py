"""
You have CSV file    having the following  lines
flight ID, Arrival, Departure ,success
A12, 09:00, 13:00 ,’’
A14, 12:00, 19:00 ,’’
B15, 10:00, 13:00 ,’’
C124,14:00, 16:00 ,’’
C23, 08:00, 17:00 ,’’
B12, 13:01, 16:00 ,’’
G56, 09:30, 14:00 ,’’
B35, 16:01, 20:00 ,’’
A21, 08:00, 13:00 ,’’
A19, 17:00, 19:00 ,’’
B55, 11:00, 13:00 ,’’
C128,12:00, 16:00 ,’’
C26, 08:00, 17:00 ,’’
B52, 12:01, 16:00 ,’’
G86, 07:30, 14:00 ,’’
B65, 17:01, 20:00 ,’’
B05, 10:00, 14:00 ,’’
C1223,12:55, 16:00 ,’’
C235, 08:00, 22:00 ,’’
B46, 14:01, 16:00 ,’’
G88, 09:30, 14:00 ,’’
B39, 16:01, 20:00 ,’’
G88, 11:30, 14:05 ,’’
B39, 16:01, 20:00,’’

Assumptions:
===========
Flight id are the same for arrival and departure.
No more than 20 success     can exists in the airport during the day.
Success for a flight is if no more than 20 success happens in a day  and greater equal  than 180 minutes
If there is no success put ‘fail’ in the success column either wise ‘success’
1)Pls  write down
Python(JAVA OR C# also can be  acceptable) code that produce the success column
Should be sorted by arrival time
2)Write 2 rest api
GET  to get info about flight
POST  update the csv file

PLS put the Solution in GIT   and send me the link (give me the correct access  for it).
Not big files can also sent via mail.
Solution can also be written in JAVA or C# .
Answer should be tested.
GOO LUCK !
Index(['flight ID', ' Arrival', ' Departure ', 'success'], dtype='object')

"""
import pandas as pd
from datetime import datetime
from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel

MAX_SUCCESS = 20
MIN_DIFF = 180  # minutes


class Flights:
    def __init__(self, file_path):
        if not file_path:
            raise Exception("Missing file path")
        self.file_path = file_path
        self.flights_df = self._read_flights_csv()
        self.successful_count = 0

    def _is_successful(self, row):
        departure = datetime.strptime(row['Departure'].strip(' '), "%H:%M")
        arrival = datetime.strptime(row['Arrival'].strip(' '), "%H:%M")
        diff = departure - arrival
        if (diff.total_seconds() / 60) >= MIN_DIFF and self.successful_count < MAX_SUCCESS:
            row['success'] = True
            self.successful_count += 1
            return True
        row['success'] = False
        return False

    def _read_flights_csv(self, inplace=True):
        flights = pd.read_table(self.file_path, sep=',',
                                skipinitialspace=True)
        flights.rename(columns=lambda x: x.strip(' '), inplace=True)  # remove spaces
        flights.sort_values(by='Arrival', inplace=inplace)
        return flights

    def process_flights(self):
        for i, row in self.flights_df.iterrows():
            self._is_successful(row)

    def export_csv(self):
        self.flights_df.to_csv(self.file_path, index=False)

    def get_flight(self, flight_id):
        row = self.flights_df[self.flights_df['flight ID'] == flight_id]
        res = row.to_dict('records')
        return res[0] if res else {f'Missing Flight {flight_id}'}

    def add_flight(self, entry, remove_duplicate=True):
        if remove_duplicate:
            self.flights_df.drop(self.flights_df.loc[self.flights_df['flight ID'] == entry['flightID']].index,
                                 inplace=True)
        row_dict = {'flight ID': entry['flightID'], 'Arrival': entry['arrival'], 'Departure': entry['departure']}
        self._is_successful(row_dict)
        self.flights_df.loc[len(self.flights_df)] = row_dict
        self.flights_df.sort_values(by='Arrival', inplace=True)
        print(self.flights_df.to_string())
        return row_dict


flights = Flights('./flights.csv')
flights.process_flights()
flights.export_csv()
app = FastAPI()


class Entry(BaseModel):
    flightID: str
    arrival: str
    departure: str


@app.get("/flights/{flight_id}")
def get_flight(flight_id: str):
    return flights.get_flight(flight_id)


@app.post("/flights/")
async def read_root(entry: Entry):
    return flights.add_flight(entry.dict())
