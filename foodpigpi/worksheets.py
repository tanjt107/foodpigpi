import gspread
from typing import Iterator
from foodpigpi.item import Item
from foodpigpi.order import Order
from foodpigpi.util import map_dict_keys


class FormResponse:
    def __init__(self, worksheet: gspread.models.Worksheet):
        self.ws = worksheet
        self.initilise_columns()
        self.all_responses = self.ws.get_all_records(default_blank=None)

    def initilise_columns(self) -> None:
        "Duplicate columns will be specified as 'X', 'X.1', ...'X.N', rather than 'X'...'X'."
        # To be introduced in the gspread 5.2.0 milestone
        try:
            counts = {}
            for i, c in enumerate(self.ws.row_values(1)):
                cur_count = counts.get(c, 0)
                if cur_count > 0:
                    self.ws.update_cell(1, i + 1, f"{c}.{cur_count}")
                    print(
                        f"Renamed '{c}' to '{c}.{cur_count} in worksheet '{self.title}'."
                    )
                counts[c] = cur_count + 1
        except:
            pass

    @property
    def title(self) -> str:
        return self.ws.title

    @property
    def locale(self) -> str:
        if self.title == "Form responses 1":
            return "en-GB"
        elif self.title == "表格回應 1":
            return "zh-TW"

    @property
    def columns(self) -> list[str]:
        "Column labels of the worksheet."
        return [c for c in self.all_responses[0] if c]

    @property
    def timestamp(self) -> str:
        return "Timestamp" if self.locale == "en-GB" else "時間戳記"

    @property
    def ig_name(self) -> str:
        return (
            "IG 名稱~ (必需正確全名✅)"
            if "IG 名稱~ (必需正確全名✅)" in self.columns
            else "IG 名稱~ (必需正確全名✅) "
        )

    @property
    def phone_number(self) -> str:
        return "聯絡電話〜(會whatsapp回覆訂單的)"

    @property
    def index(self) -> tuple[str]:
        # Change if merging orders is allowed
        return self.timestamp, self.ig_name

    @property
    def delivery_cols(self) -> list[str]:
        "Columns of '您選擇的交收時間地點〜〜'"
        return [c for c in self.columns if c.startswith("您選擇的交收時間地點〜〜")]

    @property
    def delivery_map(self) -> dict[str, str]:
        "A dictionary of {delivery_group: delivery_option}."
        return {c: str(i) for i, c in enumerate(self.delivery_cols, start=1)}

    def orders(self, items_map: dict) -> Iterator[Order]:
        "Iterate over all responses and return an Order object."
        for response in self.all_responses:
            response = {k: v for k, v in response.items() if v is not None}
            if items := map_dict_keys(response, items_map):
                yield (
                    Order(
                        tuple(response[i] for i in self.index),
                        str(response[self.phone_number]),
                        items,
                        map_dict_keys(response, self.delivery_map),
                    )
                )


class CannedMessage:
    def __init__(self, worksheet: gspread.models.Worksheet):
        self.ws = worksheet
        self.all_items = self.ws.get_all_records(default_blank=None)

    @property
    def items_map(self) -> dict[str, Item]:
        "A dictionary of {item_name: item_object}."
        return {i["Excel Name"]: Item(*i.values()) for i in self.all_items}

    @property
    def number_of_deliveries(self) -> int:
        return len({i["Delivery"] for i in self.all_items})
