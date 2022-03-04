from param import *
import gspread as gs
import pandas as pd
import demoji


def main():
    def get_df(name: str) -> pd.DataFrame:
        worksheet = sh.worksheet(name)
        return pd.DataFrame(worksheet.get_all_records())

    def check_duplicate_customers(df: pd.DataFrame):
        """avoid errors when customers making multiple orders"""
        assert len(df["IG 名稱~ (必需正確全名✅)"]) == len(
            set(df["IG 名稱~ (必需正確全名✅)"])
        ), "Duplicate customers"

    def initialise_worksheets():
        """add output sheets"""
        deliveries = pd.unique(canned_message.Delivery).tolist()
        sheet_to_add = deliveries + ["Whatsapp"]
        worksheet_list = [sheet.title for sheet in sh.worksheets()]
        for worksheet in sheet_to_add:
            if str(worksheet) not in worksheet_list:
                sh.add_worksheet(title=str(worksheet), rows="200", cols="3")
                print("Created sheet " + str(worksheet))

    def initialise_columns(name: str):
        worksheet = sh.worksheet(name)
        columns_list = worksheet.row_values(1)
        n = 0
        # TODO enumrate
        for i in range(len(columns_list)):
            # rename duplicate columns for identification
            if columns_list[i] == "您選擇的交收時間地點〜〜":
                if n > 0:
                    worksheet.update_cell(1, i + 1, "您選擇的交收時間地點〜〜." + str(n))
                    print("Updated column '您選擇的交收時間地點〜〜.'" + str(n))
                n += 1
            # avoid bugs from Google sheets where column name changes when applying filter
            if columns_list[i] == "IG 名稱~ (必需正確全名✅) ":
                worksheet.update_cell(1, i + 1, "IG 名稱~ (必需正確全名✅)")
                print("Updated column 'IG 名稱~ (必需正確全名✅)'")
            # change column names to English if workshhet is created in Chinese
            if columns_list[i] == "時間戳記":
                worksheet.update_cell(1, i + 1, "Timestamp")
                print("Updated column 'Timestamp'")

    def get_phone_number(customer):
        phone_number = responses.loc[customer]["聯絡電話〜(會whatsapp回覆訂單的)"]
        # add Hong Kong country code if phone number has 8 digits
        if len(str(phone_number)) == 8:
            phone_number = "852" + str(phone_number)
        return phone_number

    def join_response_and_canned_message(customer, drop):
        df = responses[responses.index == customer]
        if drop == True:
            df = df.drop(columns=non_item_columns)
        df = pd.melt(df)
        df = df[df.value != ""]
        df = pd.merge(
            df, canned_message, how="inner", left_on="variable", right_on="Excel Name"
        )
        return df

    def get_message_middle(customer):
        message_middle = ""
        customer_level = join_response_and_canned_message(customer, True)
        for shop in pd.unique(customer_level.Shop):
            message_middle += "\n" + shop + "\n"
            shop_level = customer_level[customer_level.Shop == shop]
            for category in pd.unique(shop_level.Category):
                message_middle += category + "\n" if category != "" else ""
                category_level = shop_level[shop_level.Category == category]
                for item in category_level["Whatsapp Name"]:
                    message_middle += (
                        str(item)
                        + " x "
                        + str(
                            category_level[
                                category_level["Whatsapp Name"] == item
                            ].value.values[0]
                        )
                        + "\n"
                    )
        return message_middle

    def calculate_price(customer):
        delivery_fee = 0
        bulk_discount = 0
        df = join_response_and_canned_message(customer, True)
        # No charge on this motnh because of promotion
        # delivery_options = responses.loc[customer][delivery_column]
        # for option in delivery_options:
        #     # for pickups in MTR stations
        #     if "(+$5)" in option:
        #         delivery_fee += 5
        # for bulk discount
        for bulk_dict in bulk_list_dict:
            bulk_quantity = df[df[bulk_dict["type"]] == bulk_dict["item"]].value.sum()
            bulk_discount += (
                int(bulk_quantity / bulk_dict["quantity"]) * bulk_dict["discount"]
            )
        return sum(df.value * df.Price) + delivery_fee - bulk_discount

    def get_delivery_message_and_update_delivery_dict(customer):
        """remove delivery options when no corresponding items are selected"""

        def remove_blank_delivery():
            for delivery in deliveries:
                delivery_level = customer_level[customer_level.Delivery == delivery]
                if delivery_level.empty:
                    delivery_options[deliveries.index(delivery)] = ""

        # def merge_delivery(merge_value):
        #     if merge_value == "需要" and len(pickups) > 0:
        #         last_pickup = pickups[-1] if len(pickups) > 1 else pickups[0]
        #         unmerged_pickups = pickups[:-1] if len(pickups) > 1 else []
        #         for pickup in unmerged_pickups:
        #             # replace delivery values in joined table
        #             customer_level.loc[
        #                 customer_level.Delivery == pickup, ("Delivery")
        #             ] = last_pickup
        #             delivery_options[pickup - 1] = ""

        delivery_options = responses.loc[customer][delivery_column].tolist()
        customer_level = join_response_and_canned_message(customer, False)
        deliveries = pd.unique(customer_level.Delivery)
        remove_blank_delivery()
        # pickups = [
        #     delivery_options.index(option) + 1
        #     for option in delivery_options
        #     if option.startswith("工作室自取")
        # ]
        # merge_delivery(responses.loc[customer][merge_column].values[0])
        delivery_options_message = ""
        for option in delivery_options:
            if option != "":
                delivery_options_message += option + "\n"
                delivery_option_list[delivery_options.index(option)].update(
                    {customer: option}
                )
        # TODO remove null delivery options before iteration
        delivery_options = [option for option in delivery_options if option != ""]
        for delivery in deliveries:
            delivery_message = ""
            delivery_level = customer_level[customer_level.Delivery == delivery]
            for item in delivery_level["Whatsapp Name"]:
                delivery_message += (
                    demoji.replace(item, "")
                    + " x "
                    + str(
                        delivery_level[
                            delivery_level["Whatsapp Name"] == item
                        ].value.values[0]
                    )
                    + " + "
                )
            delivery_item_list[delivery - 1].update({customer: delivery_message[:-3]})
        return delivery_options_message

    def update_worksheet():
        # for delivery sheets
        deliveries = pd.unique(canned_message.Delivery).tolist()
        for i in range(len(deliveries)):
            sh.worksheet(str(i + 1)).clear()
            delivery_item = pd.DataFrame.from_dict(
                delivery_item_list[i], orient="index"
            )
            delivery_option = pd.DataFrame.from_dict(
                delivery_option_list[i], orient="index"
            )
            df = pd.merge(
                delivery_item, delivery_option, left_index=True, right_index=True
            )
            df = df.reset_index()
            df.columns = ["IG Name", "Items", "Delivery"]
            df = df.sort_values("Delivery")
            sh.worksheet(str(i + 1)).update(
                [df.columns.values.tolist()] + df.values.tolist()
            )
            print("Updated sheet " + str(i + 1))

        # for sheet Whatsapp
        sh.worksheet("Whatsapp").clear()
        df = pd.DataFrame.from_dict(message_dict, orient="index")
        df = df.reset_index()
        df.columns = ["IG Name", "Link"]
        sh.worksheet("Whatsapp").update(
            [df.columns.values.tolist()] + df.values.tolist()
        )
        print("Updated sheet Whatsapp")

    gc = gs.service_account(filename="credentials.json")
    print("Opening " + sheet_name)
    sh = gc.open(sheet_name)
    canned_message = get_df("Canned Message")
    initialise_worksheets()
    initialise_columns(responses_sheet_name)
    responses = get_df(responses_sheet_name)
    check_duplicate_customers(responses)
    responses = responses.set_index("IG 名稱~ (必需正確全名✅)")
    merge_column = [
        column for column in responses.columns if column.startswith("是否需要合併一同取貨")
    ]
    delivery_column = [
        column for column in responses.columns if column.startswith("您選擇的交收時間地點〜〜")
    ]
    non_item_columns = (
        ["Timestamp", "您是否同意以上事項說明? ", "聯絡電話〜(會whatsapp回覆訂單的)"]
        + [column for column in responses.columns if column.startswith("請問需要訂購")]
        + [
            "⚠️⚠️如訂不到某一家/某項產品 就全單不要的 請下單後馬上WHATSAPP通知~ (如不通知而棄單者 會列入黑名單!!)⚠️⚠️",
            "留言/查詢區~",
        ]
        + merge_column
        + delivery_column
    )
    delivery_item_list = [{} for _ in range(max(canned_message["Delivery"]))]
    delivery_option_list = [{} for _ in range(max(canned_message["Delivery"]))]
    message_dict = {}
    for customer in responses.index:
        print("Processing", customer)
        if join_response_and_canned_message(customer, True).empty:
            continue
        phone_number = get_phone_number(customer)
        message_middle = get_message_middle(customer)
        price = calculate_price(customer)
        delivery_message = get_delivery_message_and_update_delivery_dict(customer)
        message_full = message_template.format(
            message_middle, delivery_message, price, payment_deadline
        )
        whatsapp_link = "https://api.whatsapp.com/send/?phone={}&text={}".format(
            phone_number, message_full.replace("\n", "%0a").replace("&", "%26")
        )
        message_dict.update({customer: whatsapp_link})
    update_worksheet()
    print("Done!")


if __name__ == "__main__":
    main()
