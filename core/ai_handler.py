import google.genai as genai
from google.genai import types
import config

class DialogueManager:
    def __init__(self, name: str, role: str, backstory: str, system_instruction: str) -> None:
        self.name = name
        self.role = role
        self.backstory = backstory
        self.system_instruction = system_instruction
        self.__client = genai.Client(api_key=config.API_KEY)
        self.__history: list[dict] = []

    def generate_reply(self, player_message: str, dynamic_context: str) -> str:
        # Initialize history formatted for the SDK
        contents = []
        for turn in self.__history:
            api_role = "model" if turn.get("role", "").lower() in ["model", "assistant", "npc"] else "user"
            contents.append(types.Content(
                role=api_role,
                parts=[types.Part.from_text(text=str(turn.get("text", "")))]
            ))

        # Append current input
        context_wrapper = (
            f"State Variable Frame: {dynamic_context}\n\n"
            f"The Detective asks: \"{player_message}\"\n\n"
            f"Continue the scene as {self.name}. Write only the dialogue and immediate physical actions. "
            f"Do not include meta-commentary, headers, or repeated question prompts."
        )
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=context_wrapper)]))

        # Configure system instructions and parameters
        config_params = types.GenerateContentConfig(
            system_instruction=(
                f"Role: {self.role}\n"
                f"Backstory: {self.backstory}\n"
                f"Constraints: {self.system_instruction}\n"
                f"CRITICAL: Answer inside character parameters only. "
                f"Do not leak outline checklists or analytical logs."
            ),
            temperature=0.7,
            max_output_tokens=800
        )

        try:
            # Generate content using the client
            response = self.__client.models.generate_content(
                model=config.MODEL_NAME,
                contents=contents,
                config=config_params
            )
            
            raw_reply = response.text.strip()
            
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

            # Update history
            self.__history.append({"role": "user", "text": player_message})
            self.__history.append({"role": "model", "text": final_reply})
            return final_reply

        except Exception as ex:
            print(f"DEBUG SDK EXCEPTION: {str(ex)}")
            return f"({self.name} seems lost out of reality... Check connection settings.)"