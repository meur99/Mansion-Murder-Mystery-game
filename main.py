from core.engine import GameEngine

def main():
    engine = GameEngine()
    # Initialize pointing directly to your local data blueprint configurations
    engine.initialize_game(world_json_path="data/mansion_data.json")
    engine.start_loop()

if __name__ == "__main__":
    main()