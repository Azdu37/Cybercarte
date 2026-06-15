import sys
from src.controllers.game_controller import GameController

def main():
    # Dans une version finale, le nombre de joueurs serait demandé via un menu Pygame
    # Pour l'instant, on simule 2 joueurs pour tester l'architecture
    player_count = 2
    
    if len(sys.argv) > 1:
        try:
            player_count = int(sys.argv[1])
        except ValueError:
            pass

    controller = GameController()
    controller.start_new_game(player_count)

if __name__ == "__main__":
    main()
