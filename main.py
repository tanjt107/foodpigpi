from foodpigpi.discount import VolumeDiscount
from foodpigpi.spreadsheet import Spreadsheet
from foodpigpi.util import get_config, get_template, get_whatsapp_link


def main():
    config = get_config("config/config.json")
    template = get_template(config["template"])
    deadline = config["payment_deadline"]
    discounts = [VolumeDiscount(**discount) for discount in config["bulk_list_dict"]]
    sh = Spreadsheet(config["sheet_name"], "config/service_account.json")
    responses = sh.FormResponses
    canned_msg = sh.CannedMessage

    whatsapp_links = {}
    delivery_reports = {f"{i + 1}": {} for i in range(canned_msg.number_of_deliveries)}

    for order in responses.orders(canned_msg.items_map):
        print(f"Processing customer '{order.index[1]}' at '{order.index[0]}'...")
        whatsapp_links[order.index] = get_whatsapp_link(
            order.phone_number, order.message(template, deadline, discounts)
        )
        for k, v in order.delivery_reports.items():
            delivery_reports[k][order.index] = v

    sh.update_worksheet("Whatsapp", whatsapp_links)
    for i, report in delivery_reports.items():
        sh.update_worksheet(i, report)


if __name__ == "__main__":
    main()
