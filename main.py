import sys
from src.controllers.game_controller import GameController

def main():
    print("=== Network Codex ===")
    
    # En mode local sur le même ordi, on demande le nombre de joueurs au début
    player_count = 2
    """while player_count < 2 or player_count > 4:
        try:
            val = input("Entrez le nombre de joueurs (2-4) : ")
            player_count = int(val)
        except (ValueError, EOFError):
            # En cas d'erreur ou si l'input n'est pas possible, on met 2 par défaut
            player_count = 2
            print(f"Utilisation par défaut : {player_count} joueurs.")
            break"""

    controller = GameController()
    controller.start_new_game(player_count)

if __name__ == "__main__":
    main()
