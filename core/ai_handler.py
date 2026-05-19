import json
import os
import urllib.request
import urllib.error
import config

class DialogueManager:
    def __init__(self, name: str, role: str, backstory: str, system_instruction: str) -> None:
        self.name = name
        self.role = role
        self.backstory = backstory
        self.system_instruction = system_instruction
        self.__api_key = config.API_KEY
        self.__url = config.API_URL
        self.__history: list[dict] = []

    def generate_reply(self, player_message: str, dynamic_context: str) -> str:
        if not self.__api_key:
            return f"{self.name} looks back at you silently. (API key token is missing configuration)"

        contents_payload = []
        for turn in self.__history:
            contents_payload.append({
                "role": turn["role"],
                "parts": [{"text": turn["text"]}]
            })

        context_wrapper = (
            f"State Variable Frame: {dynamic_context}\n"
            f"The Detective says to you: \"{player_message}\"\n"
            f"Your direct dialogue response:"
        )
        contents_payload.append({"role": "user", "parts": [{"text": context_wrapper}]})

        body = {
            "contents": contents_payload,
            "systemInstruction": {
                "parts": [{"text": f"Role: {self.role}\nBackstory: {self.backstory}\nConstraints: {self.system_instruction}\nCRITICAL: Answer inside character parameters only. Do not leak outline checklists or analytical logs."}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200
            }
        }

        try:
            data_bytes = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(self.__url, data=data_bytes, headers={"Content-Type": "application/json"})
            
            with urllib.request.urlopen(req, timeout=12) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                raw_reply = res_body["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # --- REVERSED BOTTOM-UP REASONING PARSING SYSTEM VALVE ---
                lines = [line.strip() for line in raw_reply.split('\n') if line.strip()]
                final_reply = ""
                forbidden_headers = ["style:", "note:", "character:", "role:", "thought:", "constraints:", "refinement:"]

                for line in reversed(lines):
                    line_low = line.lower()
                    if line_low.endswith(":") or any(word in line_low for word in forbidden_headers):
                        continue
                    
                    cleaned = line.lstrip("* ").lstrip("- ").replace(f"{self.name}:", "").strip().strip('"')
                    if cleaned:
                        final_reply = cleaned
                        break

                if not final_reply and lines:
                    final_reply = lines[-1].strip('"* ')

                # Track conversation memory structures safely
                self.__history.append({"role": "user", "text": player_message})
                self.__history.append({"role": "model", "text": final_reply})
                return final_reply

        except urllib.error.HTTPError as e:
            return f"({self.name} looks anxious... HTTP Connection Error code: {e.code})"
        except Exception:
            return f"({self.name} seems lost out of reality... Check internet links.)"