from dataclasses import dataclass
from foodpigpi.item import Item


@dataclass
class VolumeDiscount:
    "A volume discount. For example, buy $5 get $5 off."

    type: str
    item: str
    quantity: int
    discount: int

    def amount(self, items: dict[Item, int]) -> int:
        "Discounted amount."
        return (
            sum(
                quantity
                for item, quantity in items.items()
                if item[self.type] == self.item
            )
            // self.quantity
            * self.discount
        )
