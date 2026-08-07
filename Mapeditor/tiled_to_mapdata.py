"""
tiled_to_mapdata.py

Converts a Tiled map export (JSON) into the mapData dictionary format
expected by Board.loadMap() in mechanicClasses.py.

Expected Tiled structure:
- An object layer named "cities" containing point objects of class "City",
  each with a Name (the city's name) and x/y pixel coordinates.
- An object layer named "routes" containing objects of class "Route", each
  with these custom properties:
    - cityA (object reference to a City object)
    - cityB (object reference to a City object)
    - length (int)
    - colour (string)
    - numFerryIcons (int, optional, defaults to 0)
    - isTunnel (bool, optional, defaults to False)
    - duplicateGroup (string, optional, defaults to empty/None)

Usage:
    python tiled_to_mapdata.py map.json mapData.json
"""

import json
import sys


class TiledConversionError(Exception):
    """Raised when the Tiled file is missing something the converter needs."""
    pass


def _find_layer(tiled_data, name):
    for layer in tiled_data.get("layers", []):
        if layer.get("name") == name and layer.get("type") == "objectgroup":
            return layer
    raise TiledConversionError(f'No object layer named "{name}" found in the Tiled file.')


def _properties_dict(tiled_object):
    return {p["name"]: p.get("value") for p in tiled_object.get("properties", [])}


def convert(tiled_data):
    """Takes a parsed Tiled JSON dict and returns (mapData, warnings).
    mapData is ready to hand to Board.loadMap(). warnings is a list of
    human-readable strings describing anything that looked off but didn't
    stop the conversion."""
    warnings = []

    cities_layer = _find_layer(tiled_data, "cities")
    routes_layer = _find_layer(tiled_data, "routes")

    city_objects = cities_layer.get("objects", [])
    city_name_by_id = {}
    mapData_cities = []

    for obj in city_objects:
        if obj.get("type") != "City":
            warnings.append(f'Object "{obj.get("name")}" in the cities layer is not of class "City" - skipped.')
            continue
        name = obj.get("name", "").strip()
        if not name:
            raise TiledConversionError(f'City object with id {obj.get("id")} has no name set.')
        city_name_by_id[obj["id"]] = name
        mapData_cities.append({
            "name": name,
            "x": obj.get("x", 0),
            "y": obj.get("y", 0),
        })

    duplicate_names = {n for n in city_name_by_id.values() if list(city_name_by_id.values()).count(n) > 1}
    if duplicate_names:
        raise TiledConversionError(f"These city names are used more than once: {sorted(duplicate_names)}")

    mapData_routes = []
    errors = []

    for obj in routes_layer.get("objects", []):
        route_label = obj.get("name") or f"(id {obj.get('id')})"

        if obj.get("type") != "Route":
            warnings.append(f'Object "{route_label}" in the routes layer is not of class "Route" - skipped.')
            continue

        props = _properties_dict(obj)
        missing = [field for field in ("cityA", "cityB", "length", "colour") if field not in props or props[field] in (None, "")]
        if missing:
            errors.append(f'Route "{route_label}": missing required field(s) {missing}.')
            continue

        city_a_id = props["cityA"]
        city_b_id = props["cityB"]
        if city_a_id not in city_name_by_id or city_b_id not in city_name_by_id:
            errors.append(f'Route "{route_label}": cityA/cityB reference an object that is not a valid City.')
            continue

        duplicate_group = props.get("duplicateGroup") or None

        mapData_routes.append({
            "cityA": city_name_by_id[city_a_id],
            "cityB": city_name_by_id[city_b_id],
            "length": props["length"],
            "colour": props["colour"],
            "numFerryIcons": props.get("numFerryIcons", 0) or 0,
            "isTunnel": bool(props.get("isTunnel", False)),
            "duplicateGroup": duplicate_group,
        })

    if errors:
        raise TiledConversionError("Conversion stopped due to incomplete route data:\n  " + "\n  ".join(errors))

    # sanity check: every duplicateGroup value should appear on exactly 2 routes
    group_counts = {}
    for r in mapData_routes:
        if r["duplicateGroup"]:
            group_counts[r["duplicateGroup"]] = group_counts.get(r["duplicateGroup"], 0) + 1
    for group, count in group_counts.items():
        if count != 2:
            warnings.append(f'duplicateGroup "{group}" is used by {count} route(s) instead of exactly 2 - '
                             f'these will NOT be paired correctly by Board.loadMap().')

    mapData = {
        "cities": mapData_cities,
        "routes": mapData_routes,
    }
    return mapData, warnings


def main():
    if len(sys.argv) != 3:
        print("Usage: python tiled_to_mapdata.py <input_tiled.json> <output_mapData.json>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        tiled_data = json.load(f)

    try:
        mapData, warnings = convert(tiled_data)
    except TiledConversionError as e:
        print("Conversion failed:\n" + str(e))
        sys.exit(1)

    for w in warnings:
        print("Warning:", w)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapData, f, indent=2, ensure_ascii=False)

    print(f"Done: {len(mapData['cities'])} cities, {len(mapData['routes'])} routes -> {output_path}")


if __name__ == "__main__":
    main()
