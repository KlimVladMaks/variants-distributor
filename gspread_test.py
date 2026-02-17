import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Доступ по ID
sheet = client.open_by_key('1TTNXvKYLuW5r7Qtb9H_8jKn8c8yK9JXoVMC9dkKJRsI').sheet1

# Или по URL
# sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit').sheet1

sheet.update_acell('A1', 'Привет!')
print(sheet.acell('A1').value)
