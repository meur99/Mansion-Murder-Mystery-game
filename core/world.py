import json

class Item:
    def __init__(self, item_id: str, name: str, description: str, is_clue: bool = False, is_hidden: bool = False) -> None:
        self.__id = item_id
        self.__name = name
        self.__description = description
        self.__is_clue = is_clue
        self.__is_hidden = is_hidden

    @property
    def id(self) -> str: return self.__id

    @property
    def name(self) -> str: return self.__name

    @property
    def description(self) -> str: return self.__description

    @property
    def is_clue(self) -> bool: return self.__is_clue

    @property
    def is_hidden(self) -> bool: return self.__is_hidden

    def reveal(self) -> None:
        self.__is_hidden = False


class Room:
    def __init__(self, room_id: str, name: str, description: str, vibe: str, is_locked: bool = False, required_item_id: str | None = None) -> None:
        self.__id = room_id
        self.__name = name
        self.__description = description
        self.__vibe = vibe
        self.__items: dict[str, Item] = {}
        self.__is_locked = is_locked
        self.__required_item_id = required_item_id

    @property
    def id(self) -> str: return self.__id

    @property
    def name(self) -> str: return self.__name

    @property
    def description(self) -> str: return self.__description

    @property
    def vibe(self) -> str: return self.__vibe

    @property
    def items(self) -> dict[str, Item]: return self.__items

    def add_item(self, item: Item) -> None:
        self.__items[item.id] = item

    def remove_item(self, item_id: str) -> Item | None:
        if item_id in self.__items:
            return self.__items.pop(item_id)
        return None

    def is_accessible(self, player_inventory_ids: list[str]) -> bool:
        if not self.__is_locked:
            return True
        return self.__required_item_id in player_inventory_ids

    def unlock(self, player_inventory_ids: list[str]) -> bool:
        if self.__is_locked and self.__required_item_id in player_inventory_ids:
            self.__is_locked = False
            return True
        return not self.__is_locked

    def get_details(self) -> str:
        details = f"\n=== {self.__name} ===\n"
        details += f"Description: {self.__description}\n"
        details += f"Vibe: {self.__vibe}\n"
        
        visible_items = [item.name for item in self.__items.values() if not item.is_hidden]
        if visible_items:
            details += f"Objects here: {', '.join(visible_items)}\n"
        else:
            details += "There are no obvious objects lying around.\n"
        return details


class Mansion:
    def __init__(self) -> None:
        self.__rooms: dict[str, Room] = {}
        self.__floor: dict[str, list[str]] = {}
        self.__current_room_id: str = ""

    @property
    def current_room_id(self) -> str: return self.__current_room_id

    def get_room(self, room_id: str) -> Room | None:
        return self.__rooms.get(room_id)

    def get_connected_rooms(self) -> list[str]:
        return self.__floor.get(self.__current_room_id, [])

    def is_valid_move(self, room_id: str, player_inventory_ids: list[str]) -> bool:
        if room_id not in self.get_connected_rooms():
            return False
        target_room = self.__rooms.get(room_id)
        if not target_room:
            return False
        return target_room.is_accessible(player_inventory_ids)

    def move_to_room(self, room_id: str, player_inventory_ids: list[str]) -> bool:
        if self.is_valid_move(room_id, player_inventory_ids):
            target_room = self.__rooms[room_id]
            target_room.unlock(player_inventory_ids) # Clear lock status if key present
            self.__current_room_id = room_id
            return True
        return False

    def find_item_location(self, item_id: str) -> str | None:
        for room_id, room in self.__rooms.items():
            if item_id in room.items:
                return room_id
        return None

    def load_world_data(self, path: str) -> None:
        with open(path, 'r') as file:
            data = json.load(file)
        
        # Build Rooms and Items
        for r_data in data.get("rooms", []):
            room = Room(
                room_id=r_data["id"],
                name=r_data["name"],
                description=r_data["description"],
                vibe=r_data["vibe"],
                is_locked=r_data.get("is_locked", False),
                required_item_id=r_data.get("required_item_id")
            )
            
            for i_data in r_data.get("items", []):
                item = Item(
                    item_id=i_data["id"],
                    name=i_data["name"],
                    description=i_data["description"],
                    is_clue=i_data.get("is_clue", False),
                    is_hidden=i_data.get("is_hidden", False)
                )
                room.add_item(item)
                
            self.__rooms[room.id] = room

        self.__floor = data.get("connections", {})
        self.__current_room_id = data.get("entry_room_id", "")