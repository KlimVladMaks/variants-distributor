import gspread
from oauth2client.service_account import ServiceAccountCredentials

from ..database import crud
from ..config import SHEET_KEY


def gs_export(data, sheet_key, worksheet_name):
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_key)

    try:
        worksheet = sheet.worksheet(worksheet_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)

    worksheet.update(range_name='A1', values=data)


async def export_to_google_sheets():
    students_data = await crud.get_students_data_for_google_sheets()
    variants_data = await crud.get_variants_data_for_google_sheets()
    gs_export(students_data, SHEET_KEY, "students_from_bot")
    gs_export(variants_data, SHEET_KEY, "variants_from_bot")
