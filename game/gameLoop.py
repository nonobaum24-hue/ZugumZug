from mechanicClasses import *
from random import randint

WAGGON_COLOURS = ["pink", "white", "blue", "yellow", "orange", "black", "red", "green"]

ALL_WAGGON_CARDS = []
for colour in WAGGON_COLOURS:
    ALL_WAGGON_CARDS.extend([colour] * 12)
ALL_WAGGON_CARDS.extend(["locomotive"] * 14)

ALL_ROUTE_CARDS = [
    {"cityA": "Athina", "cityB": "Angora", "points": 5},
    {"cityA": "Budapest", "cityB": "Sofia", "points": 5},
    {"cityA": "Frankfurt", "cityB": "Kobenhavn", "points": 5},
    {"cityA": "Rostov", "cityB": "Erzurum", "points": 5},
    {"cityA": "Sofia", "cityB": "Smyrna", "points": 5},
    {"cityA": "Kyiv", "cityB": "Petrograd", "points": 6},
    {"cityA": "Zurich", "cityB": "Brindisi", "points": 6},
    {"cityA": "Zurich", "cityB": "Budapest", "points": 6},
    {"cityA": "Warszawa", "cityB": "Smolensk", "points": 6},
    {"cityA": "Zagrab", "cityB": "Brindisi", "points": 6},
    {"cityA": "Paris", "cityB": "Zagrab", "points": 7},
    {"cityA": "Brest", "cityB": "Marseille", "points": 7},
    {"cityA": "London", "cityB": "Berlin", "points": 7},
    {"cityA": "Edinburgh", "cityB": "Paris", "points": 7},
    {"cityA": "Amsterdam", "cityB": "Pamplona", "points": 7},
    {"cityA": "Roma", "cityB": "Smyrna", "points": 8},
    {"cityA": "Palermo", "cityB": "Constantinople", "points": 8},
    {"cityA": "Sarajevo", "cityB": "Sevastopol", "points": 8},
    {"cityA": "Madrid", "cityB": "Dieppe", "points": 8},
    {"cityA": "Barcelona", "cityB": "Bruxelles", "points": 8},
    {"cityA": "Paris", "cityB": "Wien", "points": 8},
    {"cityA": "Barcelona", "cityB": "Munchen", "points": 8},
    {"cityA": "Brest", "cityB": "Venezia", "points": 8},
    {"cityA": "Smolensk", "cityB": "Rostov", "points": 8},
    {"cityA": "Marseille", "cityB": "Essen", "points": 8},
    {"cityA": "Kyiv", "cityB": "Sochi", "points": 8},
    {"cityA": "Madrid", "cityB": "Zurich", "points": 8},
    {"cityA": "Berlin", "cityB": "Bucuresti", "points": 8},
    {"cityA": "Bruxelles", "cityB": "Danzig", "points": 9},
    {"cityA": "Berlin", "cityB": "Roma", "points": 9},
    {"cityA": "Angora", "cityB": "Kharkov", "points": 10},
    {"cityA": "Riga", "cityB": "Bucuresti", "points": 10},
    {"cityA": "Essen", "cityB": "Kyiv", "points": 10},
    {"cityA": "Venezia", "cityB": "Constantinople", "points": 10},
    {"cityA": "London", "cityB": "Wien", "points": 10},
    {"cityA": "Athina", "cityB": "Wilno", "points": 11},
    {"cityA": "Stockholm", "cityB": "Wien", "points": 11},
    {"cityA": "Berlin", "cityB": "Moskva", "points": 12},
    {"cityA": "Amsterdam", "cityB": "Wilno", "points": 12},
    {"cityA": "Frankfurt", "cityB": "Smolensk", "points": 13},
    # -- die 6 langen Strecken --
    {"cityA": "Lisboa", "cityB": "Danzig", "points": 20},
    {"cityA": "Brest", "cityB": "Petrograd", "points": 20},
    {"cityA": "Palermo", "cityB": "Moskva", "points": 20},
    {"cityA": "Kobenhavn", "cityB": "Erzurum", "points": 21},
    {"cityA": "Edinburgh", "cityB": "Athina", "points": 21},
    {"cityA": "Cadiz", "cityB": "Stockholm", "points": 21},
]

class Game:
    def __init__(self, pManager, board):
        """pManager already owns the waggon/public/route card stacks - Game
        must never create its own, or the game state would silently split
        into two disconnected worlds."""
        self.pManager = pManager
        self.board = board

    def startGame(self, initialDrawCount=4, minimumKept=2):
        """Each player draws `initialDrawCount` destination tickets and must
        keep at least `minimumKept`. Re-asks about the SAME drawn cards if
        the player didn't keep enough - never draws fresh replacement cards,
        so nothing gets lost."""
        for player in self.pManager.players:
            drawn = player.takeRouteCards(self.pManager.routeCardStack, count=initialDrawCount)
            while True:
                kept = []
                for card in drawn:
                    choice = input(f"{player.name}, do you want to keep the route card {card}? (y/n): ").strip().lower()
                    if choice == 'y':
                        kept.append(card)
                if len(kept) >= minimumKept:
                    player.keepRouteCards(drawn, kept, self.pManager.routeCardStack)
                    break
                print(f"{player.name}, you must keep at least {minimumKept} route cards "
                      f"(you kept {len(kept)}). Please decide again.")

        self.pManager.currentPlayerIndex = randint(0, len(self.pManager.players) - 1)

    def _handleDrawWaggonCards(self, currentPlayer):
        drawsMade = 0
        while drawsMade < 2:
            source = input(f"Draw {drawsMade + 1}/2 - from (d)eck or (p)ublic display? ").strip().lower()

            if source == 'p':
                print(f"Public display: {self.pManager.publicCardStack.stack}")
                try:
                    index = int(input("Choose a card index (0-4): "))
                except ValueError:
                    print("Please enter a number.")
                    continue
                card, turnMustEnd = self.pManager.handleDrawWaggonCard(index=index)
                if card is False:
                    print("Invalid index, try again.")
                    continue
            else:
                card, turnMustEnd = self.pManager.handleDrawWaggonCard()
                if card is False:
                    print("The deck and discard pile are both empty - can't draw.")
                    break

            print(f"You drew: {card}")
            drawsMade += 1

            if turnMustEnd:
                print("That was an open locomotive - your turn ends now.")
                break

    def _handleDrawRouteCards(self, currentPlayer):
        drawn = self.pManager.handleDrawRouteCards()
        print(f"You drew the following route cards: {drawn}")
        while True:
            kept = []
            for card in drawn:
                choice = input(f"Do you want to keep the route card {card}? (y/n): ").strip().lower()
                if choice == 'y':
                    kept.append(card)
            if len(kept) >= 1:
                self.pManager.handleKeepRouteCards(drawn, kept)
                return
            print("You must keep at least one route card. Please decide again.")

    def _handleClaimRoute(self, currentPlayer):
        """Returns True if a route was successfully claimed (turn consumed),
        False if the player should be asked to choose an action again."""
        claimChoice = input("Claim via (w)aggons or (s)tation? ").strip().lower()
        if claimChoice == 's':
            print("Claiming via a station isn't implemented yet - choose a different action.")
            return False

        available = self.board.getAvailableRoutes(numPlayers=len(self.pManager.players))
        if not available:
            print("No routes left to claim.")
            return False

        for i, route in enumerate(available):
            tags = []
            if route.isTunnel:
                tags.append("Tunnel")
            if route.numFerryIcons:
                tags.append(f"{route.numFerryIcons} ferry icon(s)")
            tagText = f" [{', '.join(tags)}]" if tags else ""
            print(f"{i}: {route.cityA.name} - {route.cityB.name} "
                  f"({route.colour}, length {route.length}){tagText}")

        try:
            routeIndex = int(input("Choose a route index: "))
            routeToClaim = available[routeIndex]
        except (ValueError, IndexError):
            print("Invalid route index.")
            return False

        print(f"Your hand: {currentPlayer.waggonCards}")
        cardsInput = input(f"Which {routeToClaim.length} card(s) do you want to use (comma-separated)? ")
        chosenCards = [c.strip() for c in cardsInput.split(",") if c.strip()]

        result = self.pManager.handleClaimRoute(routeToClaim, chosenCards)

        if result['isTunnel'] and not result['success'] and result.get('reason') == 'extra_cards_required':
            print(f"Tunnel! Revealed cards: {result['drawnCards']} "
                  f"- you need {result['extraNeeded']} more matching card(s) to complete the claim.")
            extraInput = input(f"Which extra card(s) do you want to use (from {currentPlayer.waggonCards}), "
                                f"or leave empty to cancel? ")
            extraCards = [c.strip() for c in extraInput.split(",") if c.strip()]
            if not extraCards:
                print("Tunnel claim cancelled - your original cards stay in your hand.")
                return False
            result = self.pManager.handleClaimRoute(routeToClaim, chosenCards, extraCards=extraCards)

        if result['success']:
            print(f"Route claimed: {routeToClaim.cityA.name} - {routeToClaim.cityB.name}!")
            return True

        print("Could not claim that route - check the cards you chose and try again.")
        return False

    def run(self):
        while not self.pManager.checkEndCondition():
            currentPlayer = self.pManager.getCurrentPlayer()
            print(f"\nIt's {currentPlayer.name}'s turn.")
            print(f"Your waggon cards: {currentPlayer.waggonCards}")
            print(f"Your route cards: {currentPlayer.routeCards}")
            print(f"Your remaining waggons: {currentPlayer.waggonCount}")

            actionChoice = input("Choose an action: (1) Draw waggon card, "
                                  "(2) Draw route card, (3) Claim route: ").strip()

            if actionChoice == '1':
                self._handleDrawWaggonCards(currentPlayer)
                self.pManager.nextPlayer()
            elif actionChoice == '2':
                self._handleDrawRouteCards(currentPlayer)
                self.pManager.nextPlayer()
            elif actionChoice == '3':
                if self._handleClaimRoute(currentPlayer):
                    self.pManager.nextPlayer()
                # on failure, same player gets to choose again - no turn consumed
            else:
                print("Please choose 1, 2 or 3.")

        print("\nGame over! Wagon counts have triggered the final round logic "
              "(final-round-then-score isn't implemented yet).")
