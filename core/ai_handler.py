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
        # Utilize your local instance key verification safely
        if not self.__api_key:
            return f"{self.name} looks back at you silently. (API key token is missing configuration)"

        contents_payload = []
        
        # 1. Heavily sanitize existing history elements to guarantee zero schema leakage
        for turn in self.__history:
            # Safely extract values using defensive dict reading
            raw_role = turn.get("role", "user").lower()
            raw_text = turn.get("text", "")
            
            # Normalize strings into strict REST-compliant roles required by the API gate
            api_role = "model" if raw_role in ["model", "assistant", "npc"] else "user"
            
            contents_payload.append({
                "role": api_role,
                "parts": [{"text": str(raw_text)}]
            })

        # 2. Inject current state context variables cleanly inside the prompt
        context_wrapper = (
            f"State Variable Frame: {dynamic_context}\n"
            f"The Detective says to you: \"{player_message}\"\n"
            f"Your direct dialogue response:"
        )
        contents_payload.append({"role": "user", "parts": [{"text": context_wrapper}]})

        # 3. Formulate the explicit Gemma 4 JSON payload body
        body = {
            "contents": contents_payload,
            "systemInstruction": {
                "parts": [{
                    "text": (
                        f"Role: {self.role}\n"
                        f"Backstory: {self.backstory}\n"
                        f"Constraints: {self.system_instruction}\n"
                        f"CRITICAL: Answer inside character parameters only. "
                        f"Do not leak outline checklists or analytical logs."
                    )
                }]
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
                
                # Safely extract text through deep dictionary traversal to prevent KeyError crashes
                candidates = res_body.get("candidates", [])
                if not candidates:
                    return f"({self.name} keeps their mouth shut... Empty model candidate returned.)"
                    
                raw_reply = candidates[0]["content"]["parts"][0]["text"].strip()
                
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

                # 4. Save to history using your exact local storage dictionary schema
                self.__history.append({"role": "user", "text": player_message})
                self.__history.append({"role": "model", "text": final_reply})
                return final_reply

        except urllib.error.HTTPError as e:
            # Capture and show any specific REST error data leaked from the response
            error_details = e.read().decode("utf-8") if e.fp else ""
            print(f"DEBUG API ERROR RESPONSE: {error_details}")
            return f"({self.name} looks anxious... HTTP Connection Error code: {e.code})"
        except Exception as ex:
            print(f"DEBUG LOCAL EXCEPTION: {str(ex)}")
            return f"({self.name} seems lost out of reality... Check internet links.)"