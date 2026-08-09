from random import randint
from collections import Counter, deque

WAGGONS = 45
STATIONS = 3
POINTS_FOR_LENGTH = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}

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


class City:
    def __init__(self, title, x, y):
        self.name = str(title)
        self.gridX = int(x)
        self.gridY = int(y)


class Route:
    def __init__(self, cityA, cityB, length, trackColour, owningPlayer=None, duplicate=False,
                 numFerryIcons=0, isTunnel=False):
        self.cityA = cityA
        self.cityB = cityB
        self.length = int(length)
        self.colour = trackColour
        self.owner = owningPlayer
        self.isDuplicate = duplicate
        self.numFerryIcons = int(numFerryIcons)  # minimum number of locomotives required
        self.isTunnel = bool(isTunnel)
        self.pairedRoute = None  # set by Board.loadMap() for parallel duplicate routes

    def isClaimed(self):
        return self.owner is not None

    def calculatePointsForLength(self):
        return POINTS_FOR_LENGTH[self.length]


class Player:
    def __init__(self, name, playerColour, waggonCardStack):
        self.name = name
        self.colour = playerColour
        self.waggonCount = WAGGONS
        self.stationCount = STATIONS
        self.points = 0
        self.waggonCards = []
        self.routeCards = []
        self.ownedRoutes = []

        for _ in range(4):
            self.waggonCards.append(waggonCardStack.drawCard())

    def drawWaggonCard(self, waggonCardStack, publicCardStack=None, index=None):
        """Draws one waggon card, either blind from the deck or openly from the
        public display (publicCardStack + index). Returns the card, or False if
        an invalid public index was chosen."""
        if publicCardStack is not None and index is not None:
            card = publicCardStack.drawCard(waggonCardStack, index)
            if card is False:
                return False
            self.waggonCards.append(card)
            return card

        card = waggonCardStack.drawCard()
        self.waggonCards.append(card)
        return card

    def checkIfRouteCanBeClaimed(self, route, chosenCards, requiredExtraCards=0):
        """Checks whether chosenCards (a subset of the player's hand) may be
        used to claim this route: right amount of cards, right colour (or any
        single colour for grey routes), with locomotives acting as jokers.
        requiredExtraCards accounts for extra cards a tunnel demanded on top
        of route.length (0 for ordinary routes)."""
        expected_length = route.length + requiredExtraCards
        if len(chosenCards) != expected_length:
            return False

        hand_counts = Counter(self.waggonCards)
        chosen_counts = Counter(chosenCards)
        for card, count in chosen_counts.items():
            if hand_counts[card] < count:
                return False  # player doesn't actually own that many of this card

        locomotives = chosen_counts.get("locomotive", 0)
        non_locomotives = [c for c in chosenCards if c != "locomotive"]

        if route.numFerryIcons > locomotives:
            return False  # not enough locomotives to cover the ferry icons

        if not non_locomotives:
            return True  # claimed entirely with locomotives

        if route.colour == "grey":
            first_colour = non_locomotives[0]
            return all(c == first_colour for c in non_locomotives)
        else:
            return all(c == route.colour for c in non_locomotives)

    def computeTunnelExtraCardsNeeded(self, chosenCards, drawnCards):
        """After revealing 3 cards for a tunnel claim, returns how many extra
        matching cards the player must pay. A drawn card counts as a match if
        it's a locomotive, or shares the colour the player is building with
        (if the player built entirely with locomotives, only further
        locomotives count)."""
        non_locomotives = [c for c in chosenCards if c != "locomotive"]
        colour_used = non_locomotives[0] if non_locomotives else "locomotive"
        return sum(1 for c in drawnCards if c == "locomotive" or c == colour_used)

    def claimRoute(self, route, waggonCardStack, chosenCards, requiredExtraCards=0):
        if route.isClaimed():
            return False
        if self.waggonCount < route.length:
            return False
        if not self.checkIfRouteCanBeClaimed(route, chosenCards, requiredExtraCards):
            return False

        route.owner = self
        self.ownedRoutes.append(route)
        self.waggonCount -= route.length
        self.points += route.calculatePointsForLength()
        for card in chosenCards:
            self.waggonCards.remove(card)
            waggonCardStack.discardStack.append(card)
        return True

    def takeRouteCards(self, routeCardStack, count=3):
        """Draws up to `count` destination cards and returns them. The player
        must decide afterwards (via keepRouteCards) which ones to keep - at
        least one, per the rules."""
        drawn = []
        for _ in range(count):
            card = routeCardStack.drawCard()
            if card is not False:
                drawn.append(card)
        return drawn

    def keepRouteCards(self, drawnCards, keptCards, routeCardStack):
        """keptCards must be a non-empty subset of drawnCards. Everything not
        kept goes back into the destination card stack."""
        if len(keptCards) == 0 or len(keptCards) > len(drawnCards):
            return False
        self.routeCards.extend(keptCards)
        for card in drawnCards:
            if card not in keptCards:
                routeCardStack.stack.append(card)
        return True

    def hasTriggeredEndGame(self):
        return self.waggonCount <= 2


class PlayerManager:
    def __init__(self, players, waggonCardStack, publicCardStack, routeCardStack):
        self.players = players
        self.waggonCardStack = waggonCardStack
        self.publicCardStack = publicCardStack
        self.routeCardStack = routeCardStack
        self.currentPlayerIndex = 0

    def getCurrentPlayer(self):
        return self.players[self.currentPlayerIndex]

    def nextPlayer(self):
        self.currentPlayerIndex = (self.currentPlayerIndex + 1) % len(self.players)

    def handleDrawWaggonCard(self, index=None):
        """Call this once or twice per turn. index=None draws blind from the
        deck; index=0..4 draws the open card at that public display slot.
        Returns the drawn card, and a flag telling the caller whether the
        turn must end immediately (True only when an open locomotive was
        deliberately taken)."""
        currentPlayer = self.getCurrentPlayer()
        if index is not None:
            card = currentPlayer.drawWaggonCard(self.waggonCardStack, self.publicCardStack, index)
            turn_must_end = (card == "locomotive")
            return card, turn_must_end
        card = currentPlayer.drawWaggonCard(self.waggonCardStack)
        return card, False

    def handleClaimRoute(self, route, chosenCards, extraCards=None):
        """For ordinary routes, this claims it in one go. For tunnels, the
        first call (extraCards=None) reveals the 3 tunnel cards and reports
        back how many extra cards are needed (without spending anything yet
        if the player can't/won't pay). Call again with extraCards once the
        player has chosen which ones to add."""
        currentPlayer = self.getCurrentPlayer()

        if not route.isTunnel:
            success = currentPlayer.claimRoute(route, self.waggonCardStack, chosenCards)
            return {'success': success, 'isTunnel': False}

        drawnCards = self.waggonCardStack.revealTunnelCards()
        extraNeeded = currentPlayer.computeTunnelExtraCardsNeeded(chosenCards, drawnCards)

        if extraNeeded > 0 and (extraCards is None or len(extraCards) < extraNeeded):
            return {
                'success': False,
                'isTunnel': True,
                'reason': 'extra_cards_required',
                'extraNeeded': extraNeeded,
                'drawnCards': drawnCards,
            }

        totalCards = chosenCards + (extraCards[:extraNeeded] if extraNeeded > 0 else [])
        success = currentPlayer.claimRoute(route, self.waggonCardStack, totalCards, requiredExtraCards=extraNeeded)
        return {'success': success, 'isTunnel': True, 'drawnCards': drawnCards, 'extraCardsUsed': extraNeeded}

    def handleDrawRouteCards(self):
        currentPlayer = self.getCurrentPlayer()
        return currentPlayer.takeRouteCards(self.routeCardStack)

    def handleKeepRouteCards(self, drawnCards, keptCards):
        currentPlayer = self.getCurrentPlayer()
        return currentPlayer.keepRouteCards(drawnCards, keptCards, self.routeCardStack)

    def checkEndCondition(self):
        return any(p.hasTriggeredEndGame() for p in self.players)


class Board:
    def __init__(self):
        self.cities = {}   # name -> City
        self.routes = []   # list of Route

    def loadMap(self, mapData):
        """mapData shape:
        {
            "cities": [{"name": ..., "x": ..., "y": ...}, ...],
            "routes": [{"cityA": ..., "cityB": ..., "length": ..., "colour": ...,
                        "numFerryIcons": 0, "isTunnel": False,
                        "duplicateGroup": None}, ...]
        }
        duplicateGroup: any hashable key shared by exactly two route entries
        that form a parallel pair; None if the route has no duplicate.
        """
        self.cities = {}
        self.routes = []

        for cityData in mapData["cities"]:
            city = City(cityData["name"], cityData["x"], cityData["y"])
            self.cities[city.name] = city

        duplicate_groups = {}
        for routeData in mapData["routes"]:
            cityA = self.cities[routeData["cityA"]]
            cityB = self.cities[routeData["cityB"]]
            route = Route(
                cityA, cityB,
                routeData["length"],
                routeData["colour"],
                numFerryIcons=routeData.get("numFerryIcons", 0),
                isTunnel=routeData.get("isTunnel", False),
                duplicate=routeData.get("duplicateGroup") is not None,
            )
            self.routes.append(route)

            group_key = routeData.get("duplicateGroup")
            if group_key is not None:
                if group_key in duplicate_groups:
                    partner = duplicate_groups[group_key]
                    partner.pairedRoute = route
                    route.pairedRoute = partner
                else:
                    duplicate_groups[group_key] = route

    def getRoutesForPlayer(self, player):
        return [route for route in self.routes if route.owner is player]

    def getAvailableRoutes(self, numPlayers=4):
        """Routes nobody owns yet. With fewer than 4 players, a route whose
        paired (duplicate) partner is already claimed is excluded too."""
        available = []
        for route in self.routes:
            if route.isClaimed():
                continue
            if numPlayers < 4 and route.pairedRoute is not None and route.pairedRoute.isClaimed():
                continue
            available.append(route)
        return available

    def _buildAdjacency(self, player):
        """city -> list of (neighbouring city, route) for routes this player owns."""
        adjacency = {}
        for route in self.getRoutesForPlayer(player):
            adjacency.setdefault(route.cityA, []).append((route.cityB, route))
            adjacency.setdefault(route.cityB, []).append((route.cityA, route))
        return adjacency

    def isConnected(self, player, cityA, cityB):
        """Breadth-first search through the player's own routes only."""
        if cityA == cityB:
            return True
        adjacency = self._buildAdjacency(player)
        visited = {cityA}
        queue = deque([cityA])
        while queue:
            current = queue.popleft()
            for neighbour, _route in adjacency.get(current, []):
                if neighbour == cityB:
                    return True
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
        return False

    def getLongestPath(self, player):
        """Longest chain of the player's own routes, edges used at most once,
        cities may be revisited. Tries every owned city as a starting point
        so the direction of travel never matters."""
        adjacency = self._buildAdjacency(player)
        if not adjacency:
            return 0

        best = 0

        def dfs(city, usedRoutes, length):
            nonlocal best
            if length > best:
                best = length
            for neighbour, route in adjacency.get(city, []):
                if route not in usedRoutes:
                    usedRoutes.add(route)
                    dfs(neighbour, usedRoutes, length + route.length)
                    usedRoutes.remove(route)

        for city in adjacency:
            dfs(city, set(), 0)

        return best


class WaggonStack:
    def __init__(self):
        self.stack = list(ALL_WAGGON_CARDS)
        self.discardStack = []

    def drawCard(self):
        if len(self.stack) == 0:
            if len(self.discardStack) == 0:
                return False  # deck and discard both empty
            self.stack, self.discardStack = self.discardStack, []
        return self.stack.pop(randint(0, len(self.stack) - 1))

    def revealTunnelCards(self):
        """Draws the top 3 cards for a tunnel-claim check and discards them
        immediately, regardless of the outcome (per the rules)."""
        drawn = []
        for _ in range(3):
            card = self.drawCard()
            if card is not False:
                drawn.append(card)
        self.discardStack.extend(drawn)
        return drawn


class PublicCardStack:
    def __init__(self, waggonCardStack):
        self.stack = []
        for _ in range(5):
            self.stack.append(waggonCardStack.drawCard())
        self.checkForThreeLocomotives(waggonCardStack)

    def drawCard(self, waggonCardStack, index):
        if index < 0 or index > 4:
            return False
        card = self.stack[index]
        self.stack[index] = waggonCardStack.drawCard()
        self.checkForThreeLocomotives(waggonCardStack)
        return card

    def checkForThreeLocomotives(self, waggonCardStack):
        count = self.stack.count("locomotive")
        if count >= 3:
            for i in range(5):
                waggonCardStack.discardStack.append(self.stack[i])
                self.stack[i] = waggonCardStack.drawCard()


class RouteCardStack:
    def __init__(self):
        self.stack = list(ALL_ROUTE_CARDS)

    def drawCard(self):
        if len(self.stack) == 0:
            return False
        return self.stack.pop(randint(0, len(self.stack) - 1))

