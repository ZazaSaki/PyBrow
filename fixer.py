from gspread.utils import ValueRenderOption
from Drive.docsUpdaterBase import client_session

ss = client_session.open_by_url("https://docs.google.com/spreadsheets/d/1_L5KnzKwnInQ07i6s2v4BXhmnRNwzN0kiwfjomz8AQo")

ws = ss.worksheet("!Verifyer")

ng = ws.get(value_render_option = "FORMATTED_VALUE")
fg = ws.get_all_records(default_blank="00_No_Info_00",value_render_option = ValueRenderOption.formatted)
ufg = ws.get_all_records(default_blank="00_No_Info_00",value_render_option = ValueRenderOption.unformatted)
ffg = ws.get_all_records(default_blank="00_No_Info_00",value_render_option = ValueRenderOption.formula)


True