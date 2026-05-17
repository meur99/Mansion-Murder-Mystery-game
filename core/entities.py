from abc import ABC, abstractmethod
from .world import Item

class Player:
    def __init__(self, name: str) -> None:
        self.__name = name
        self.__inventory: dict[str, Item] = {}
        self.__evidence_log: list[str] = []

    @property
    def name(self) -> str:
        return self.__name

    @property
    def evidence_log(self) -> list[str]:
        return self.__evidence_log

    def add_to_inventory(self, item: Item) -> None:
        self.__inventory[item.id] = item

    def has_item(self, item_id: str) -> bool:
        return item_id in self.__inventory

    def remove_from_inventory(self, item_id: str) -> Item | None:
        if self.has_item(item_id):
            return self.__inventory.pop(item_id)
        return None

    def get_inventory_ids(self) -> list[str]:
        return list(self.__inventory)

    def add_evidence(self, clue: str) -> None:
        if clue not in self.__evidence_log:
            self.__evidence_log.append(clue)


class BaseCharacter(ABC):
    def __init__(self, char_id: str, name: str, role: str, backstory: str, room_id: str):
        self._id = char_id
        self._name = name
        self._role = role
        self._backstory = backstory
        self.current_room_id = room_id
        self.dialogue_manager = None  # Hooked up in Step 2

    @property
    def id(self) -> str: return self._id

    @property
    def name(self) -> str: return self._name

    @abstractmethod
    def interact(self, user_input: str, room_vibe: str) -> str:
        pass


class HumanNPC(BaseCharacter):
    def __init__(self, char_id: str, name: str, role: str, backstory: str, room_id: str, friendliness: int = 0):
        super().__init__(char_id, name, role, backstory, room_id)
        self.friendliness = friendliness  # Scale from -10 to 10

    def interact(self, user_input: str, room_vibe: str) -> str:
        if self.dialogue_manager:
            # Pass the relationship state dynamically as context to the AI
            context = f"Your current friendliness level with the player is {self.friendliness}/10. Atmosphere: {room_vibe}."
            return self.dialogue_manager.generate_reply(user_input, context)
        return f"{self._name} remains silent."


class NonHumanNPC(BaseCharacter):
    def __init__(self, char_id: str, name: str, role: str, backstory: str, room_id: str, species: str):
        super().__init__(char_id, name, role, backstory, room_id)
        self.species = species  # e.g., "Ghost" or "Cat"

    def interact(self, user_input: str, room_vibe: str) -> str:
        if self.dialogue_manager:
            context = f"You are a {self.species}. You must abide strictly by your behavioral constraints. Atmosphere: {room_vibe}."
            return self.dialogue_manager.generate_reply(user_input, context)
        return f"The {self.species} makes no sound."