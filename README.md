# Zug um Zug — Isometric Recreation

## Project Overview

This project is a from-scratch recreation of **Zug um Zug** (the German edition of *Ticket to Ride*, based on the Europe map — hence the inclusion of tunnels, ferries, and train stations), rendered with **raylib (via the `pyray`/`raylib` Python bindings)**.

Development philosophy:
- Strict **object-oriented programming** in **pure Python**.
- The game *mechanics* (rules, state, validation) were built and verified completely independently of any rendering or UI code first — no graphics-specific code, no file formats, just testable core logic (see `mechanicClasses.py`).
- Map data (cities, routes) is loaded from an external map file (`mapData.json`, produced via the Tiled map editor pipeline in `Mapeditor/`) rather than hardcoded, so different maps can be swapped in without touching the core engine.
- The final UI lets the player pick which of their already-collected cards to spend (e.g. via clicking), rather than requiring manual text input.

---

## Game Rules

### Objective
Players score points by claiming train routes between cities on the map and by completing destination tickets (secret objectives connecting two cities). The player with the most points at the end wins.

### Setup
- Each player receives:
  - **45 train wagons** (pieces used to claim routes)
  - **3 stations** (used to "borrow" a route someone else hasn't claimed yet, for bonus purposes — see below)
  - **4 train cards** dealt from the deck
  - A hand of destination tickets (drawn as part of setup; must keep at least a minimum required number)
- A **train car deck** is shuffled; **5 cards** are placed face-up as a public display.
- A **destination ticket deck** is shuffled and set aside.

### Turn Structure
On their turn, a player chooses **exactly one** of the following actions:

1. **Draw train cards** — draw 2 cards total, from any combination of:
   - The top of the face-down deck (blind draw), or
   - One of the 5 face-up cards in the public display (open draw).
   - **Special rule:** if a player deliberately takes an **open locomotive** (wildcard) card from the public display, that counts as their entire turn — no second card may be drawn. A locomotive drawn *blindly* from the deck does **not** trigger this restriction; a second card may still be drawn normally.
   - **Reshuffle rule:** if 3 or more of the 5 face-up cards are locomotives at any point, all 5 are discarded and replaced with new cards from the deck.
   - If the deck runs out, the discard pile is shuffled to form a new deck.

2. **Claim a route** — build on one route segment between two adjacent cities:
   - Discard train cards matching the route's required colour and length (grey routes can be claimed with any single colour).
   - **Locomotives act as wildcards** and may substitute for any colour.
   - Place wagons equal to the route's length; the route now belongs to that player.
   - Score points immediately based on route length:

     | Length | Points |
     |--------|--------|
     | 1      | 1      |
     | 2      | 2      |
     | 3      | 4      |
     | 4      | 7      |
     | 5      | 10     |
     | 6      | 15     |

   - **Ferry routes**: some routes require a minimum number of locomotive cards (indicated by boat icons on the route) in addition to the normal colour-matching requirement.
   - **Tunnel routes**: after announcing the cards to be used, the top 3 cards of the deck are revealed. For every revealed card that matches the colour being used (or is itself a locomotive), the player must pay one additional matching card. If they can't or won't, the claim fails — the revealed cards are discarded regardless, and the player's original cards remain in hand.
   - **Duplicate (parallel) routes**: on some connections there are two parallel route segments. With **fewer than 4 players**, only one of the two may ever be claimed — once one is taken, its partner becomes unavailable.
   - A route, once claimed by any player, cannot be claimed by another.

3. **Draw destination tickets** — draw 3 tickets from the deck and keep **at least one** (more may be kept); unwanted tickets are returned to the bottom of the deck.

### Stations
Each player has 3 stations, which can be used (mechanic still to be implemented) to allow a player to use an opponent's claimed route as if it were their own for connectivity purposes, at the cost of giving up a station — typically also costing the opponent a bonus in return. (Exact implementation still open.)

### End of Game
The moment any player drops to **2 or fewer** remaining wagons, the current round finishes (every other player gets exactly one more turn), and then the game ends.

### Final Scoring
- Completed destination tickets: their point value is added.
- **Incomplete** destination tickets: their point value is **subtracted**.
- **Longest continuous route bonus**: the player with the single longest unbroken chain of their own claimed routes receives a bonus (commonly +10 points).
- Highest total score wins.

---

## Technical Architecture (current state)

### Core mechanics — `mechanicClasses.py`
Rendering-independent and fully covered by the logic layer:

- **`City`** — name, and grid coordinates (`gridX`, `gridY`) for isometric placement.
- **`Route`** — connects two `City` objects; stores length, colour, owner, duplicate-pairing (`pairedRoute`), ferry icon count, and tunnel flag. Provides `isClaimed()` and `calculatePointsForLength()`.
- **`Player`** — hand of train cards, destination tickets, owned routes, wagon/station counts, and points. Handles drawing cards, validating and executing route claims (including ferry and tunnel rules), and drawing/keeping destination tickets.
- **`PlayerManager`** — orchestrates turns across all players: draws (with the locomotive-ends-turn rule), route claims (including the two-phase tunnel reveal-then-pay flow), and destination ticket draws (`handleDrawRouteCards`, `handleKeepRouteCards`). Also checks the end-game trigger condition.
- **`Board`** — holds the full map (`cities`, `routes`), loads it from map data (`loadMap`), and answers graph-based questions:
  - `getRoutesForPlayer(player)`
  - `getAvailableRoutes(numPlayers)` (respecting the duplicate-route restriction)
  - `isConnected(player, cityA, cityB)` — breadth-first search over a player's own routes, used to check whether a destination ticket is fulfilled
  - `getLongestPath(player)` — depth-first search (tried from every owned city) to find the player's longest unbroken chain of routes, for the end-game bonus
- **`WaggonStack`** — the train card deck: draw pile, discard pile, reshuffle-on-empty, and the 3-card tunnel reveal.
- **`PublicCardStack`** — the 5 face-up train cards, including the 3-locomotives-triggers-reshuffle rule.
- **`RouteCardStack`** — the destination ticket deck.

### Settings & data — `settings.py`
Central config: raylib/pyray imports, wagon/station counts, points-per-length table, the full waggon card and destination ticket pools (with card image paths), window size, and font size.

### Map data
`mapData.json` (built via the Tiled-based pipeline in `Mapeditor/`) holds the real city/route layout and is loaded through `Board.loadMap()`.

### Game loops
Two parallel implementations of the turn loop currently exist, both built on top of the same `mechanicClasses` core:

- **`gameLoop.py`** — the original **terminal-based** loop (`Game` class). Fully working, driven entirely by `input()` prompts; used to validate the mechanics end-to-end before any graphics were involved. Not being extended further.
- **`gamloop_rl.py`** — the **raylib-based graphical** loop (`game` class), currently in active development. `rl` stands for raylib, not reinforcement learning.
  - Implemented so far: window setup, random starting player, and the **destination-ticket accept/discard screen** — each drawn card gets a clickable "Accept"/"Discard" button pair; once every displayed card has a choice, the kept cards are submitted via `handleKeepRouteCards` and play passes to the next player.
  - Internally split into `build_card_state` (called once per player turn — computes button rectangles and resets choices) and `draw_routecard_acceptance` (called every frame — only draws, never touches game state), so on-screen choices persist correctly across frames.
  - `run.py` and `button_test.py` are older/experimental helpers tied to `gameLoop.py` and are not part of the `gamloop_rl.py` path.

### Not yet implemented
- Station mechanic (borrowing an opponent's route)
- Route-claiming, waggon-card drawing, and map rendering inside `gamloop_rl.py` (currently only the destination-ticket screen exists)
- Enforcing the "keep at least one destination ticket" rule inside `gamloop_rl.py` (present in the terminal `gameLoop.py`, still a TODO in the raylib version)
- Full end-of-game scoring pass (ticket completion check + longest-route bonus tally across all players)
- Isometric board rendering
