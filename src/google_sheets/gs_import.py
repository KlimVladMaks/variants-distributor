import gspread
from oauth2client.service_account import ServiceAccountCredentials

from ..config import SHEET_KEY


def gs_import(sheet_key, worksheet_name):
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_key)

    worksheet = sheet.worksheet(worksheet_name)
    all_values = worksheet.get_all_values()
    result = []

    for row in all_values:
        if not any(row):
            break
        row_data = []
        for cell in row:
            if cell == '':
                break
            row_data.append(cell)
        result.append(tuple(row_data))

    return result


def get_students_data_from_google_sheets():
    students_data = gs_import(SHEET_KEY, "students_for_bot")
    del students_data[0]
    return students_data


def get_variants_data_from_google_sheets():
    variants_data = gs_import(SHEET_KEY, "variants_for_bot")
    del variants_data[0]
    return variants_data
