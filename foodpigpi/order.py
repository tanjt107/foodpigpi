import jinja2
from typing import Optional, Union
from foodpigpi.discount import VolumeDiscount
from foodpigpi.item import Item
from foodpigpi.util import remove_emoji


class Order:
    def __init__(
        self,
        index: Union[str, tuple[str]],
        phone_number: str,
        items: dict[Item, int],
        delivery_options: dict[str, str],
    ):
        self.index = index
        self.phone_number = phone_number
        self.items = items
        self.delivery_options = delivery_options

    @property
    def items_by_shop(self) -> dict[dict[dict[Item, int]]]:
        "A dictionary of {shop: {category: {item: quantity}}}."
        shop_dict = {}
        for item, quantity in self.items.items():
            if item.shop not in shop_dict:
                shop_dict[item.shop] = {}
            if item.category not in shop_dict[item.shop]:
                shop_dict[item.shop][item.category] = []
            shop_dict[item.shop][item.category].append([item, quantity])
        return shop_dict

    def price(self, discounts: Optional[list[VolumeDiscount]] = None) -> int:
        total_discount = (
            sum(discount.amount(self.items) for discount in discounts)
            if discounts
            else 0
        )
        # TODO Check type
        return (
            sum(int(item.price * quantity) for item, quantity in self.items.items())
            - total_discount
        )

    def message(
        self,
        template: jinja2.Template,
        deadline: str,
        discounts: Optional[list[VolumeDiscount]] = None,
    ) -> str:
        "Message to send."
        return template.render(
            items_by_shop=self.items_by_shop,
            delivery_options=self.delivery_options,
            price=self.price(discounts),
            deadline=deadline,
        )

    @property
    def items_by_delivery(self) -> dict[str]:
        "A dictionary of {delivery group: 'item1 x quantity1 + item2 x quantity2 + ...'}."
        delivery_dict = {}
        for item, quantity in self.items.items():
            if item.delivery_group not in delivery_dict:
                delivery_dict[item.delivery_group] = []
            delivery_dict[item.delivery_group].append(
                f"{remove_emoji(item.name_in_whatsapp)} x {quantity}"
            )
        return {k: " + ".join(v) for k, v in delivery_dict.items()}

    @property
    def delivery_reports(self):
        "A dictionary of {delivery group: (delivery option, 'item1 x quantity1 + item2 x quantity2 + ...')}."
        return {
            group: (item, option)
            for (group, item), option in zip(
                self.items_by_delivery.items(), self.delivery_options.values()
            )
        }
