import gspread
from foodpigpi.worksheets import CannedMessage, FormResponse


class Spreadsheet:
    def __init__(self, title: str, config: str):
        """
        title : A title of a spreadsheet.
        config: The path to the service account json file.
        """
        self.title = title
        print(f"Opening spreadsheet '{self.title}'...")
        self.sheet = gspread.service_account(config).open(self.title)

    @property
    def locale(self):
        if self.title.endswith("(Responses)"):
            return "en-GB"
        elif self.title.endswith("(回覆)"):
            return "zh-TW"
        else:
            raise ValueError(f"Cannot determine language of '{self.title}'.")

    def select_worksheet(self, title: str) -> gspread.models.Worksheet:
        ws = self.sheet.worksheet(title)
        self.initilise_columns(ws)
        return ws

    # TODO Staticmethod
    def initilise_columns(self, ws: gspread.models.Worksheet) -> None:
        "Duplicate columns will be specified as 'X', 'X.1', ...'X.N', rather than 'X'...'X'."
        # To be introduced in the gspread 5.2.0 milestone
        counts = {}
        for i, c in enumerate(ws.row_values(1)):
            cur_count = counts.get(c, 0)
            if cur_count > 0:
                ws.update_cell(1, i + 1, f"{c}.{cur_count}")
                print(f"Renamed '{c}' to '{c}.{cur_count} in worksheet '{self.title}'.")
            counts[c] = cur_count + 1

    @property
    def FormResponses(self) -> FormResponse:
        title = "Form responses 1" if self.locale == "en-GB" else "表格回應 1"
        return FormResponse(self.select_worksheet(title))

    @property
    def CannedMessage(self) -> CannedMessage:
        return CannedMessage(self.select_worksheet("Canned Message"))

    def create_worksheet(self, title: str, rows: int = 100, cols: int = 20):
        print(f"Creating worksheet '{title}'...")
        return self.sheet.add_worksheet(title, rows=str(rows), cols=str(cols))

    def update_worksheet(self, title: str, data: dict):
        """Write values to a worksheet."""
        if title in [sheet.title for sheet in self.sheet.worksheets()]:
            ws = self.select_worksheet(title)
            ws.clear()
        else:
            # TODO rows and cols
            ws = self.create_worksheet(title)

        values = []
        for key, value in data.items():
            key = list(key) if isinstance(key, tuple) else [key]
            value = list(value) if isinstance(value, tuple) else [value]
            values.append(key + value)

        print(f"Updating worksheet '{title}'...")
        ws.update(values, value_input_option="USER_ENTERED")
