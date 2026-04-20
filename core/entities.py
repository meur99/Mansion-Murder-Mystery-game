from world import Item, Room, Mansion

class Player:
    __name: str
    __inventory: dict[str, Item]
    __evidence_log: list[str]

    def __init__(self, name: str) -> None:
        self.__name = name
        self.__inventory = {}
        self.__evidence_log = []

    @property
    def name(self):
        return self.__name

    def add_to_inventory(self, item: Item) -> None:
        self.__inventory[item.id] = item
        return
    
    def has_item(self, item_id: str) -> bool:
        return item_id in self.__inventory
    
    def remove_from_inventory(self, item_id: str) -> Item | None:
        if self.has_item(item_id):
            return self.__inventory.pop(item_id)
    
    def get_inventory_ids(self) -> list[str]:
        return list(self.__inventory)
