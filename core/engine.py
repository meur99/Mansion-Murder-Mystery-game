import json
import os
import config
from .world import Mansion
from .entities import Player, HumanNPC, NonHumanNPC
from .ai_handler import DialogueManager

class GameEngine:
    def __init__(self) -> None:
        self.mansion = Mansion()
        self.player = Player(name="Detective")
        self.npcs: dict[str, HumanNPC | NonHumanNPC] = {}

    def initialize_game_session(self) -> None:
        """Launches state-tracking configurations, binding world maps with AI scripts."""
        self.mansion.load_world_data(config.WORLD_DATA_PATH)
        self._instantiate_npc_profiles()

    def _instantiate_npc_profiles(self) -> None:
        if not os.path.exists(config.PROMPTS_DATA_PATH):
            return

        with open(config.PROMPTS_DATA_PATH, 'r') as file:
            data = json.load(file)

        for n_data in data.get("npcs", []):
            c_id, name, role, bstory, r_id = n_data["id"], n_data["name"], n_data["role"], n_data["backstory"], n_data["room_id"]
            
            if n_data["type"] == "human":
                npc = HumanNPC(c_id, name, role, bstory, r_id, friendliness=n_data.get("friendliness", 0))
            else:
                npc = NonHumanNPC(c_id, name, role, bstory, r_id, species=n_data["species"])

            # Hook dynamic native dialogue manager pipeline interfaces
            npc.dialogue_manager = DialogueManager(name, role, bstory, n_data["system_instruction"])
            self.npcs[c_id] = npc

    def package_current_state(self) -> dict:
        """Serializes current memory stats into real-time visual grid models."""
        room = self.mansion.get_room(self.mansion.current_room_id)
        if not room:
            return {}

        visible_items = [{"id": i.id, "name": i.name, "description": i.description, "is_clue": i.is_clue} 
                         for i in room.items.values() if not i.is_hidden]

        local_npcs = [{"id": n._id, "name": n._name, "role": n._role} 
                      for n in self.npcs.values() if n.current_room_id == room.id]

        connected_details = []
        for conn_id in self.mansion.get_connected_rooms():
            r_node = self.mansion.get_room(conn_id)
            if r_node:
                connected_details.append({"id": conn_id, "name": r_node.name})

        return {
            "room_id": room.id,
            "room_name": room.name,
            "description": room.description,
            "vibe": room.vibe,
            "items": visible_items,
            "npcs": local_npcs,
            "connections": connected_details,
            "inventory": self.player.get_inventory_ids(),
            "evidence_log": self.player.evidence_log
        }

    def execute_action_command(self, type_tag: str, parameter: str) -> str:
        type_tag = type_tag.strip().lower()
        parameter = parameter.strip()
        
        current_room = self.mansion.get_room(self.mansion.current_room_id)
        if not current_room:
            return "System Error: Lost inside an uninstantiated room coordinate map boundary."

        if type_tag == "go":
            if self.mansion.move_to_room(parameter, self.player.get_inventory_ids()):
                new_room = self.mansion.get_room(self.mansion.current_room_id)
                return f"👣 You walked into the {new_room.name}."
            else:
                target = self.mansion.get_room(parameter)
                if target:
                    return f"🔒 The door to the {target.name} is locked! Look for its designated access key object."
                return "❌ That vector does not map to a valid connected room node destination."

        elif type_tag == "take":
            item = current_room.items.get(parameter)
            if item and not item.is_hidden:
                current_room.remove_item(parameter)
                self.player.add_to_inventory(item)
                log = f"💼 Pocketed item asset: '{item.name}'."
                if item.is_clue:
                    self.player.add_evidence(f"{item.name}: {item.description}")
                    log += " ✨ Immutably committed to your Case Evidence Log!"
                return log
            return "❌ That item object cannot be found or gathered here."

        elif type_tag == "examine":
            item = current_room.items.get(parameter)
            if not item and parameter in self.player.get_inventory_ids():
                # Safe look up inside internal schema properties
                pass
            for r in self.mansion._Mansion__rooms.values():
                if parameter in r.items:
                    return f"🔍 [{r.items[parameter].name} Detail]: {r.items[parameter].description}"
            return "❌ No inspection properties available for that reference identifier."

        elif type_tag == "talk":
            npc = self.npcs.get(parameter)
            if not npc or npc.current_room_id != self.mansion.current_room_id:
                return "❌ That person isn't standing inside this location."
            reply = npc.interact("Hello there, officer. Tell me what details you know regarding the master.", current_room.vibe)
            return f"💬 {npc.name}: \"{reply}\""

        elif type_tag == "custom_talk":
            if ":" not in parameter:
                return "System tracking syntax format error on web transmission arrays."
            n_id, text = parameter.split(":", 1)
            npc = self.npcs.get(n_id.strip())
            if not npc or npc.current_room_id != self.mansion.current_room_id:
                return "❌ Suspect has moved or left your immediate visibility profile."
            
            reply = npc.interact(text.strip(), current_room.vibe)
            return f"💬 {npc.name}: \"{reply}\""

        return f"Unknown core operational action code received: '{type_tag}'."