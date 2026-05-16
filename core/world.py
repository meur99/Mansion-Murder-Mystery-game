class Item:
    def __init__(self, id: str, name: str, description: str, is_clue: bool, is_hidden: bool) -> None:
        self.__id = id
        self.__name = name
        self.__description = description
        self.__is_clue = is_clue
        
        self.is_hidden = is_hidden

    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def is_clue(self) -> bool:
        return self.__is_clue
    
    def reveal(self) -> None:
        self.is_hidden = False

    
class Room:
    id: str
    name: str
    description: str
    vibe: str
    items: dict[str, Item]
    is_locked: bool
    required_item_id: str | None

    def add_item(self, item: Item) -> None:
        self.items[item.id] = item
        return
    
    def remove_item(self, item_id: str) -> Item | None:
        try:
            return self.items.pop(item_id)
        except KeyError:
            print(f"No item called {item_id} in this room")
        return
    
    def is_accessible(self, player_inventory_ids: list) -> bool:
        if (self.required_item_id in player_inventory_ids) or (not self.is_locked):
            return True
        return False
    
    # TODO: define function logic
    def get_details(self) -> str:
        return
    
class Mansion:
    rooms: dict[str, Room]
    floor: dict[str, list[str]]
    current_room_id: str # always main hall at the start of the game

    def get_connected_rooms(self) -> list[str]:
        return self.floor[self.current_room_id]
    
    def is_valid_move(self, room_id) -> bool:
        if room_id not in self.rooms:
            return False
        
        if room_id not in self.floor.get(self.current_room_id, []):
            return False
        
        # TODO: replace placeholder with actual logic
        inv = None
        return self.rooms[room_id].is_accessible(inv)
    
    # TODO: define function logic
    def load_world_data(self, path):
        return
    
    # IDEA: find_item_location(), searches all rooms

