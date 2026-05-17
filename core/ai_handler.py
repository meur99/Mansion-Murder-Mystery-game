import os
import json
import urllib.request
import urllib.error

class DialogueManager:
    def __init__(self, char_id: str, name: str, role: str, backstory: str, system_instruction: str = "") -> None:
        self.__char_id = char_id
        self.__name = name
        self.__role = role
        self.__backstory = backstory
        
        # 1. Safely pull your key string using your explicit layout tag
        self.__api_key = self.__load_api_key_from_json()
        
        # 2. Target the exact Gemma 4 31B endpoint requested
        self.__model_name = "gemma-4-31b-it"
        self.__url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.__model_name}:generateContent?key={self.__api_key}"
        
        # 3. Few-Shot Pattern Training Architecture
        self.__base_instruction = (
            f"You are roleplaying as {self.__name}, the {self.__role}.\n"
            f"Your background context: {self.__backstory}\n"
            f"Style constraint: {system_instruction}\n\n"
            "CRITICAL: You must ONLY output the direct spoken words of your character. "
            "Do NOT write lists, do NOT show drafts, do NOT output your character traits, thoughts, or labels.\n\n"
            "--- START EXAMPLES OF PERFECT OUTPUT FORMAT ---\n"
            "Current situation: Friendliness level 5/10. Room mood: Quiet\n"
            "The player says to you: \"Hello there.\"\n"
            "Your direct verbal reply to the player: Ah, hello detective. Can I help you find something?\n\n"
            "Current situation: Friendliness level 2/10. Room mood: Tense\n"
            "The player says to you: \"Did you commit the murder?\"\n"
            "Your direct verbal reply to the player: What?! How dare you accuse me of such a horrific crime!\n"
            "--- END EXAMPLES OF PERFECT OUTPUT FORMAT ---"
        )
            
        # 4. Standard conversational memory tracker
        self.__history: list[dict] = []

    def __load_api_key_from_json(self) -> str:
        """Safely reads the custom NPC_BRAIN key from your exact data folder path location."""
        possible_paths = [
            "data/keys.json", 
            "core/data/keys.json", 
            "../data/keys.json",
            os.path.join(os.getcwd(), "data", "keys.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as file:
                    data = json.load(file)
                    key = data.get("NPC_BRAIN")
                    if key:
                        return key
                    raise KeyError("Found keys.json, but the key identifier 'NPC_BRAIN' was missing.")
                    
        raise FileNotFoundError("Could not locate keys.json anywhere.")

    def generate_reply(self, player_message: str, dynamic_context: str) -> str:
        """Assembles prompt payload, executes raw HTTP post, and extracts pure dialogue text."""
        
        contents_payload = []
        for turn in self.__history:
            contents_payload.append({
                "role": turn["role"],
                "parts": [{"text": turn["text"]}]
            })
            
        # Complete matching pattern layout matching the few-shot examples perfectly
        context_enforcer = (
            f"Current situation: {dynamic_context}\n"
            f"The player says to you: \"{player_message}\"\n"
            f"Your direct verbal reply to the player:"
        )
        
        contents_payload.append({
            "role": "user",
            "parts": [{"text": context_enforcer}]
        })
        
        body = {
            "contents": contents_payload,
            "systemInstruction": {
                "parts": [{"text": self.__base_instruction}]
            },
            "generationConfig": {
                "temperature": 0.5,  # Lowered for strict adherence to formatting rules
                "maxOutputTokens": 200
            }
        }
        
        data_bytes = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.__url,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                raw_reply = res_body["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # --- HEAVY DUTY CLEANUP FILTER ---
                lines = [line.strip() for line in raw_reply.split('\n') if line.strip()]
                final_reply = ""
                
                # Filter out any lingering metadata terms if the model goes off-track
                forbidden_keywords = [
                    "character:", "role:", "traits:", "constraints:", "current state:", 
                    "player input:", "draft", "refining", "context:", "output:"
                ]
                
                for line in lines:
                    if any(word in line.lower() for word in forbidden_keywords):
                        continue
                    # Clean up common formatting decorations applied by instruction models
                    cleaned = line.lstrip("* ").lstrip("- ").replace(f"{self.__name}:", "").strip()
                    cleaned = cleaned.strip('"')
                    if cleaned:
                        final_reply = cleaned
                        break
                
                # Ultimate fallback if everything was filtered out
                if not final_reply and lines:
                    final_reply = lines[-1].strip('"* ')
                
                # Commit memory records
                self.__history.append({"role": "user", "text": player_message})
                self.__history.append({"role": "model", "text": final_reply})
                
                return final_reply
                
        except urllib.error.HTTPError as e:
            return f"{self.__name} seems lost in thought... (HTTP Error: {e.code})"
        except Exception as e:
            return f"{self.__name} whispers incoherently... (Connection Error: {str(e)})"