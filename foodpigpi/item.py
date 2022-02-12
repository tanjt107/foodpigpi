from typing import Optional


class Item:
    def __init__(
        self,
        name_in_form: str,
        price: int,
        set_quantity: int,
        name_in_whatsapp: str,
        shop: str,
        category: Optional[str],
        delivery_group: str,
    ):
        self.name_in_form = name_in_form
        self.price = price
        self.set_quantity = set_quantity
        self.name_in_whatsapp = name_in_whatsapp
        self.shop = shop
        self.category = category
        self.delivery_group = str(delivery_group)

    def __hash__(self):
        return hash(self.name_in_form)

    def __eq__(self, other):
        return self.name_in_form == other.name_in_form

    def __getitem__(self, key):
        return getattr(self, key)
