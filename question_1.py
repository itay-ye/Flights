import pandas as pd
from datetime import datetime
import re

MAX_SUCCESS = 20
MIN_DIFF = 180  # minutes
HOUR_REGEX = re.compile(r"(([0-9]){2,2}:([0-9]){2,2})")


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
        return row_dict


flights = Flights('./flights.csv')
flights.process_flights()
flights.export_csv()
