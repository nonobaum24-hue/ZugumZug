from mechanicClasses import *
import os
from random import randint



class Game:
    def __init__(self, pManager, board):
        self.pManager = pManager
        self.board = board

        self.routeCardStack = RouteCardStack()
        self.waggonCardStack = WaggonStack()
        self.publicWaggonCardStack = PublicCardStack()

    def startGame(self):
        for player in self.pManager.players:
            finalChoice = []
            discardedCards = []
            while True:
                newCards = player.takeRouteCards(self.routeCardStack, count=4)
                for card in newCards:
                    choice=str(input(f"{player.name}, do you want to keep the route card {card}? (y/n): "))
                    if choice == 'y':
                        finalChoice.append(card)
                    else:
                        discardedCards.append(card)
                if len(finalChoice) >= 2:
                    player.routeCards = finalChoice
                    self.routeCardStack.append(discardedCards)
                    break
                else:
                    print(f"{player.name}, you must keep at least 2 route cards. You have kept {len(finalChoice)} cards.")
                    finalChoice = []
                    discardedCards = []
        
        #choose a random player to start
        self.pManager.currentPlayerIndex = randint(0, len(self.pManager.players) - 1)
                    
                
    
    def run(self):
        while self.pManager.checkEndCondition() == False:
            currentPlayer = self.pManager.getCurrentPlayer()
            print(f"\nIt's {currentPlayer.name}'s turn.")
            print(f"Your waggon cards: {currentPlayer.waggonCards}")
            print(f"Your route cards: {currentPlayer.routeCards}")
            print(f"Your remaining waggons: {currentPlayer.waggonCount}")
            print(f"Public waggon cards: {self.publicWaggonCardStack.cards}")

            actionChoice = input("Choose an action: (1) Draw waggon card, (2) Draw route card, (3) Claim route: ")
            if actionChoice == '1':
                cardChoice = input("Do you want to draw from the public display or the deck? {public (p)/deck (p)}: ")
                if cardChoice == 'public':
                    index = int(input(f"Choose a card index from the public display (0-{len(self.publicWaggonCardStack.cards)-1}): "))
                    drawnCard = currentPlayer.drawWaggonCard(self.publicWaggonCardStack, index=index)
                    if drawnCard == "locomotive":
                        print("You drew a locomotive card. You can only draw one card this turn.")
                    else:
                        while True:
                            cardChoice = input("Do you want to draw from the public display or the deck? {public (p)/deck (p)}: ")
                            if cardChoice == 'public':
                                index = int(input(f"Choose a card index from the public display (0-{len(self.publicWaggonCardStack.cards)-1}): "))
                                drawnCard = currentPlayer.drawWaggonCard(self.publicWaggonCardStack, index=index)
                            if drawnCard != "locomotive":
                                break
                            else:
                                print("You cant draw a second locomotive card. Please choose again.")
                else:
                    drawnCards = [currentPlayer.drawWaggonCard(self.waggonCardStack) for i in range(2)]
                currentPlayer.waggonCards.extend(drawnCards)
                print(f"You drew: {drawnCards}")
            
            elif actionChoice == '2':
                newRouteCards = currentPlayer.takeRouteCards(self.routeCardStack)
                print(f"You drew the following route cards: {newRouteCards}")
                keptCards = []
                while True:
                    keptCards = []
                    for card in newRouteCards:
                        choice = input(f"Do you want to keep the route card {card}? (y/n): ")
                        if choice == 'y':
                            keptCards.append(card)
                    if len(keptCards) >= 1:
                        currentPlayer.routeCards.extend(keptCards)
                        break
                    else:
                        print("You must keep at least one route card.")
                        keptCards = []
            
            else:
                claimChoice = input('Do you want to claim a route through waggons or through a station? (w/s): ')
                if claimChoice == 'w':
                    routeIndex = int(input(f"Choose a route index to claim (0-{len(self.board.routes)-1}): "))
                    routeToClaim = self.board.routes[routeIndex]
                    chosenCards = []
                    if route.isTunnel == True:
                        print("This is a tunnel route. You need to draw 3 cards to see if you can claim it.")
                        drawnCards = [self.waggonCardStack.drawCard() for i in range(3)]
                        print(f"You drew the following cards: {drawnCards}")
                        # Check if the drawn cards match the color of the route
                        matchingCards = [card for card in drawnCards if card == routeToClaim.color or card == "locomotive"]
                        if len(matchingCards) >= routeToClaim.length:
                            print("You have enough matching cards to claim the tunnel route.")
                            chosenCards = matchingCards[:routeToClaim.length]
                            currentPlayer.claimRoute(routeToClaim, chosenCards)
                        else:
                            print("You do not have enough matching cards to claim the tunnel route.")
