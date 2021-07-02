from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from string import ascii_uppercase
import re


class SheetsDao:
    def __init__(self, SCOPES=['https://www.googleapis.com/auth/spreadsheets']):
        self.SCOPES = SCOPES
        self.SPREADSHEET_ID = None
        self.RANGE_NAME = None
        self.__setup__()


    def __setup__(self):
        '''setup: credentials.json must be present in root folder. token.json created first run'''
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()

    def __get_id__(self):
        """simple input for sheet id, add flexibility"""
        if self.SPREADSHEET_ID:
            confirm = input(
                f"your last url used looks like: {os.path.join('https://docs.google.com/spreadsheets/d/', self.SPREADSHEET_ID)}\nIs this correct? y/n ")
            if confirm == 'y':
                return

        while True:
            msg = "Input spreadsheet id (copy paste from URL, google sheets) "
            self.SPREADSHEET_ID = input(msg)
            confirm = input(f"your url looks like: {os.path.join('https://docs.google.com/spreadsheets/d/', self.SPREADSHEET_ID)}\nIs this correct? y/n ")
            if confirm == 'y':
                break
            else:
                msg = "Please reenter your spreadsheet id "
                continue

    def __get_range__(self):
        """simple input for sheet range, add flexibility"""
        if self.RANGE_NAME:
            confirm = input(f"your last used data range was: {self.RANGE_NAME}\nIs this correct? y/n ")
            if confirm == 'y':
                return
        while True:
            msg = "Input range name, i.e. click and drag cells then (Ctrl + j) to select name box "
            self.RANGE_NAME = input(msg)
            confirm = input(f"you entered the data range: {self.RANGE_NAME}\nIs this correct? y/n ")
            if confirm == 'y':
                break
            else:
                msg = "Please reenter the desired range name "
                continue

    def get_sheet_values(self):
        self.__get_id__()
        self.__get_range__()
        req = self.sheet.values().get(spreadsheetId=self.SPREADSHEET_ID, range=self.RANGE_NAME)
        result = req.execute()
        values = result.get('values', [])
        if not values:
            print("no data found in given spreadsheet information")
        else:
            for row in values:
                print(row)

    def write_sheet_values(self):
        self.__get_id__()
        self.__get_range__()
        pass

    def __get_next_letter__(self):
        '''a generator to yield a new range secondary value, given starting cell'''
        first_cell = re.match("[A-Z]*", self.RANGE_NAME)
        first_letter = self.RANGE_NAME[:first_cell.span()[1]]
        first_num = int(re.match("[0-9]*[^:]", self.RANGE_NAME[first_cell.span()[1]:]).group())
        first_ind = ascii_uppercase.index(first_letter[-1])
        if first_ind == 25 or len(first_letter) > 1:
            raise ValueError("handling of sheets greater than 26 columns: not yet implemented")
        else:
            second_letter = ascii_uppercase[first_ind+1]
            second_num = first_num

        yield first_letter+f"{first_num}"+":"+second_letter+f"{second_num}"

        while True:
            second_num+=1
            yield first_letter+f"{first_num}"+":"+second_letter+f"{second_num}"

    def write_crypto(self, crypto_values):
        self.__get_id__()
        self.__get_range__()
        letter_gen = self.__get_next_letter__()


        for _ in crypto_values:
            curr_range = next(letter_gen)

        update_body = {
            "range": curr_range,
            "majorDimension": "ROWS",
            "values": crypto_values
        }

        update_req = self.sheet.values().update(spreadsheetId=self.SPREADSHEET_ID, range=curr_range, valueInputOption="USER_ENTERED", body=update_body)
        update_res = update_req.execute()
        print(update_res)


if __name__ == "__main__":
    sDAO = SheetsDao()
    # sDAO.get_sheet_values()
    try:
        c_vals = [
            ["BTC", 35000.0],
            ["ETH", 2100.0],
            ["LTC", 150.0],
            ["ADA", 1.4]
        ]
        sDAO.write_crypto(c_vals)
    except ValueError as e:
        print(e)