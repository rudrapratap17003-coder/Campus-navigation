import json
from pathlib import Path

data_path = Path('data/jain_global_campus.json')
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

locations = data.get('locations', [])
connections = data.get('connections', [])

print(f"Total Locations: {len(locations)}")
print(f"Total Connections: {len(connections)}")

loc_ids = [l['id'] for l in locations]
print(f"Unique Location IDs: {len(set(loc_ids))} (Total: {len(loc_ids)})")

floors = {}
buildings = {}
categories = {}
for l in locations:
    fl = l.get('floor', 0)
    bld = l.get('building', 'Unknown')
    cat = l.get('category', 'Unknown')
    floors[fl] = floors.get(fl, 0) + 1
    buildings[bld] = buildings.get(bld, 0) + 1
    categories[cat] = categories.get(cat, 0) + 1

print("Floor distribution:", sorted(floors.items()))
print("Building distribution:", buildings)
print("Category distribution:", categories)

elevators = [l for l in locations if 'elevator' in l['id'].lower() or 'elevator' in l.get('name', '').lower()]
print(f"\nElevator nodes ({len(elevators)}):")
for e in sorted(elevators, key=lambda x: x.get('floor', 0)):
    print(f"  {e['id']}: floor={e.get('floor')}, x={e.get('x')}, y={e.get('y')}")

stairs = [l for l in locations if 'stair' in l['id'].lower() or 'stair' in l.get('name', '').lower()]
print(f"\nStair nodes ({len(stairs)}):")
for s in sorted(stairs, key=lambda x: (x.get('id', ''), x.get('floor', 0))):
    print(f"  {s['id']}: floor={s.get('floor')}, x={s.get('x')}, y={s.get('y')}")

loc_set = set(loc_ids)
invalid_refs = []
zero_dist = []
zero_time = []
edge_pairs = set()
duplicate_edges = []

for idx, c in enumerate(connections):
    src, dst = c.get('source'), c.get('destination')
    if src not in loc_set or dst not in loc_set:
        invalid_refs.append((idx, src, dst))
    dist = c.get('distance', 0)
    if dist <= 0:
        zero_dist.append((idx, dist))
    tm = c.get('estimated_time', 0)
    if tm <= 0:
        zero_time.append((idx, tm))
    pair = tuple(sorted([src, dst]))
    if pair in edge_pairs:
        duplicate_edges.append((idx, src, dst))
    else:
        edge_pairs.add(pair)

print(f"\nInvalid connection endpoint references: {len(invalid_refs)}")
print(f"Zero/negative distances: {len(zero_dist)}")
print(f"Zero/negative estimated times: {len(zero_time)}")
print(f"Duplicate undirected edges: {len(duplicate_edges)}")

print("\nSample location fields:", list(locations[0].keys()))
print("Sample connection fields:", list(connections[0].keys()))

# Check existing verification fields
loc_has_verif = sum(1 for l in locations if 'verification_status' in l)
conn_has_verif = sum(1 for c in connections if 'verification_status' in c)
print(f"\nLocations with verification_status: {loc_has_verif}/{len(locations)}")
print(f"Connections with verification_status: {conn_has_verif}/{len(connections)}")

# Check vertical alignment of staircases and elevators across floors
print("\n--- SPATIAL VERTICAL ALIGNMENT CHECK ---")
by_type = {}
for l in locations:
    name = l['name']
    fl = l['floor']
    coords = (l['x'], l['y'])
    # group by base name without floor prefix
    lid = l['id']
    if 'ELEVATOR' in lid:
        by_type.setdefault('ELEVATOR', []).append((fl, lid, coords))
    elif 'STAIRS_NORTH' in lid:
        by_type.setdefault('STAIRS_NORTH', []).append((fl, lid, coords))
    elif 'STAIRS_SOUTH' in lid:
        by_type.setdefault('STAIRS_SOUTH', []).append((fl, lid, coords))
    elif 'STAIRS_EAST' in lid:
        by_type.setdefault('STAIRS_EAST', []).append((fl, lid, coords))
    elif 'STAIRS_WEST' in lid:
        by_type.setdefault('STAIRS_WEST', []).append((fl, lid, coords))

for k, entries in by_type.items():
    print(f"\nVertical connector group: {k} ({len(entries)} floors)")
    base_coords = entries[0][2]
    all_aligned = True
    for fl, lid, coords in entries:
        is_match = coords == base_coords
        if not is_match:
            all_aligned = False
        print(f"  Floor {fl} ({lid}): coords={coords} -> {'Aligned' if is_match else 'MISALIGNED!'}")
    if all_aligned:
        print(f"  ==> PERFECT VERTICAL ALIGNMENT across all {len(entries)} floors at (X={base_coords[0]}, Y={base_coords[1]})")
