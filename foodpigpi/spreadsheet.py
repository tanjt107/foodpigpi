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
    def locale(self) -> str:
        if self.title.endswith("(Responses)"):
            return "en-GB"
        elif self.title.endswith("(回覆)"):
            return "zh-TW"
        else:
            raise ValueError(f"Cannot determine language of '{self.title}'.")

    def select_worksheet(self, title: str) -> gspread.models.Worksheet:
        return self.sheet.worksheet(title)

    @property
    def FormResponses(self) -> FormResponse:
        title = "Form responses 1" if self.locale == "en-GB" else "表格回應 1"
        return FormResponse(self.select_worksheet(title))

    @property
    def CannedMessage(self) -> CannedMessage:
        return CannedMessage(self.select_worksheet("Canned Message"))

    def create_worksheet(self, title: str, rows: int = 100, cols: int = 20) -> None:
        print(f"Creating worksheet '{title}'...")
        return self.sheet.add_worksheet(title, rows=str(rows), cols=str(cols))

    def update_worksheet(self, title: str, data: list) -> None:
        """Write values to a worksheet"""
        if title in [sheet.title for sheet in self.sheet.worksheets()]:
            ws = self.select_worksheet(title)
            ws.clear()
        else:
            ws = self.create_worksheet(title, rows=len(data), cols=len(data[0]))

        print(f"Updating worksheet '{title}'...")
        ws.update(data, value_input_option="USER_ENTERED")
