import os
import json
from .world import Mansion, Item
from .entities import Player, HumanNPC, NonHumanNPC

class GameEngine:
    def __init__(self) -> None:
        self.mansion = Mansion()
        self.player = Player(name="Detective")
        self.npcs: dict[str, HumanNPC | NonHumanNPC] = {}
        self.game_running = False

    def initialize_game(self, world_json_path: str, npcs_json_path: str = None) -> None:
        """Loads room geometry configurations and maps out suspect spawn locations."""
        # 1. Boot up structural architecture map configuration
        self.mansion.load_world_data(world_json_path)
        
        # 2. Spawn and map localized suspects/characters manually or via data file
        if npcs_json_path and os.path.exists(npcs_json_path):
            self._load_npc_data(npcs_json_path)
        else:
            # Fallback inline creation for rapid script verification execution
            self._spawn_default_suspects()

    def _spawn_default_suspects(self) -> None:
        """Fallback initialization generating the core game characters."""
        chef = HumanNPC(
            char_id="pierre",
            name="Chef Pierre",
            role="Mansion Cook",
            backstory="A highly strung French chef obsessed with precision and cutlery. Secretive about his movements.",
            room_id="lounge",
            friendliness=5
        )
        self.npcs[chef.id] = chef

    def _load_npc_data(self, path: str) -> None:
        with open(path, 'r') as file:
            data = json.load(file)
        for n in data.get("npcs", []):
            if n.get("type") == "non-human":
                npc = NonHumanNPC(
                    char_id=n["id"], name=n["name"], role=n["role"],
                    backstory=n["backstory"], room_id=n["room_id"], species=n["species"]
                )
            else:
                npc = HumanNPC(
                    char_id=n["id"], name=n["name"], role=n["role"],
                    backstory=n["backstory"], room_id=n["room_id"], friendliness=n.get("friendliness", 0)
                )
            self.npcs[npc.id] = npc

    def get_characters_in_current_room(self) -> list[HumanNPC | NonHumanNPC]:
        return [npc for npc in self.npcs.values() if npc.current_room_id == self.mansion.current_room_id]

    def process_command(self, raw_input: str) -> str:
        """Tokenizes user system commands and invokes structural engine transaction updates."""
        tokens = raw_input.strip().lower().split(maxsplit=1)
        if not tokens:
            return "Please type a command."

        action = tokens[0]
        argument = tokens[1] if len(tokens) > 1 else ""

        if action in ["go", "move", "walk"]:
            return self._execute_move(argument)
        elif action in ["take", "get", "grab"]:
            return self._execute_take(argument)
        elif action in ["look", "examine", "inspect"]:
            return self._execute_look(argument)
        elif action in ["talk", "speak", "interact"]:
            return self._execute_talk(argument)
        elif action in ["inv", "inventory"]:
            return self.player.get_inventory_details() if hasattr(self.player, 'get_inventory_details') else f"Carrying items: {self.player.get_inventory_ids()}"
        elif action in ["clues", "evidence", "log"]:
            return f"Evidence Log:\n" + "\n".join([f"- {c}" for c in self.player.evidence_log]) if self.player.evidence_log else "No clues registered yet."
        elif action == "help":
            return ("Available commands:\n"
                    "  go [room_id]       - Travel to a connected destination\n"
                    "  look               - Survey your immediate room surroundings\n"
                    "  look [item_id]     - Closely evaluate a specific object\n"
                    "  take [item_id]     - Pocket an item into your inventory stash\n"
                    "  talk [npc_id]      - Initiate dialogue with a room inhabitant\n"
                    "  inventory / clues  - Display current assets and case log details")
        else:
            return f"Unknown terminal action '{action}'. Type 'help' for systemic instructions."

    def _execute_move(self, target_room_id: str) -> str:
        if not target_room_id:
            return "Where do you want to go? (e.g., 'go lounge')"

        current_inv = self.player.get_inventory_ids()
        
        # Pull reference tracking prior to movement state execution
        connected_rooms = self.mansion.get_connected_rooms()
        if target_room_id not in connected_rooms:
            return f"You can't get to '{target_room_id}' from here. Connected: {', '.join(connected_rooms)}"

        target_room = self.mansion.get_room(target_room_id)
        if target_room and not target_room.is_accessible(current_inv):
            return f"The door to the {target_room.name} is firmly locked. You need a specific item to gain entry."

        if self.mansion.move_to_room(target_room_id, current_inv):
            new_room = self.mansion.get_room(self.mansion.current_room_id)
            output = f"You step into the {new_room.name}.\n"
            output += new_room.get_details()
            
            # Print present characters
            local_npcs = self.get_characters_in_current_room()
            if local_npcs:
                output += f"\nPeople present: {', '.join([f'{n.name} ({n.id})' for n in local_npcs])}\n"
            return output
        
        return "Movement execution failed."

    def _execute_take(self, item_id: str) -> str:
        if not item_id:
            return "What do you want to take? (e.g., 'take note')"

        current_room = self.mansion.get_room(self.mansion.current_room_id)
        item = current_room.items.get(item_id)

        if not item or item.is_hidden:
            return f"There is no item with ID '{item_id}' visible here."

        extracted_item = current_room.remove_item(item_id)
        if extracted_item:
            self.player.add_to_inventory(extracted_item)
            output = f"You picked up: {extracted_item.name}.\n"
            
            if extracted_item.is_clue:
                self.player.add_evidence(f"{extracted_item.name}: {extracted_item.description}")
                output += "✨ Clue added to your Case Evidence Log!"
            return output

        return "Failed to secure item tracking."

    def _execute_look(self, argument: str) -> str:
        current_room = self.mansion.get_room(self.mansion.current_room_id)
        
        if not argument:
            # Survey broad room
            output = current_room.get_details()
            local_npcs = self.get_characters_in_current_room()
            if local_npcs:
                output += f"Suspects here: {', '.join([f'{n.name} ({n.id})' for n in local_npcs])}\n"
            return output

        # Check item inspection paths
        item = current_room.items.get(argument)
        if not item and argument in self.player.get_inventory_ids():
            # Check inventory loop
            item = self.player._Player__inventory.get(argument) # Safe backup extract

        if item:
            if item.is_hidden:
                return f"There is no object labeled '{argument}' in sight."
            return f"[{item.name}]: {item.description}"

        return f"You don't see anything matching '{argument}'."

    def _execute_talk(self, npc_id: str) -> str:
        if not npc_id:
            return "Who do you want to talk to? (e.g., 'talk pierre')"

        local_npcs = {n.id: n for n in self.get_characters_in_current_room()}
        if npc_id not in local_npcs:
            return f"There is no one here named '{npc_id}'."

        npc = local_npcs[npc_id]
        print(f"\n[Engaging conversation with {npc.name}... Type 'exit' to stop talking]")
        current_room = self.mansion.get_room(self.mansion.current_room_id)
        
        while True:
            user_msg = input(f"You to {npc.name} > ").strip()
            if user_msg.lower() == "exit":
                return f"You walked away from conversation with {npc.name}."
            if not user_msg:
                continue
                
            reply = npc.interact(user_msg, current_room.vibe)
            print(f"\n{npc.name}: {reply}\n")


    def start_loop(self) -> None:
        """Launches the primary interactive system runtime console interface."""
        self.game_running = True
        print("=" * 60)
        print("         WELCOME TO THE MANSION MURDER MYSTERY ENGINE          ")
        print("=" * 60)
        
        start_room = self.mansion.get_room(self.mansion.current_room_id)
        print(start_room.get_details())
        local_npcs = self.get_characters_in_current_room()
        if local_npcs:
            print(f"Suspects present: {', '.join([f'{n.name} ({n.id})' for n in local_npcs])}")
        print("\nType 'help' to review basic control syntax instructions.\n")

        while self.game_running:
            try:
                cmd = input(f"[{start_room.name if self.mansion.get_room(self.mansion.current_room_id) is None else self.mansion.get_room(self.mansion.current_room_id).name}] > ")
                if cmd.strip().lower() in ["quit", "exit"]:
                    print("Exiting case file engine tracking configuration...")
                    self.game_running = False
                    break
                
                feedback = self.process_command(cmd)
                print(feedback)
                print("-" * 40)
            except (KeyboardInterrupt, EOFError):
                self.game_running = False
                break