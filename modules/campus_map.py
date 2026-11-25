"""Campus map representation, data validation, and NetworkX spatial graph engine."""

from __future__ import annotations

from dataclasses import dataclass, field
import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx

# Global memory cache for parsed JSON data indexed by (resolved_path, mtime)
_FILE_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def invalidate_cache(file_path: Optional[Union[str, Path]] = None) -> None:
    """Invalidate in-memory JSON file cache for campus map datasets.

    Args:
        file_path: Specific file path to invalidate, or None to clear all.
    """
    if file_path is None:
        _FILE_CACHE.clear()
    else:
        _FILE_CACHE.pop(str(Path(file_path).resolve()), None)


class CampusDataValidationError(ValueError):
    """Raised when campus map data violates schema or integrity constraints."""

    def __init__(self, message: str, errors: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.errors: List[str] = errors or [message]


class CampusMap:
    """Manages campus spatial data, data integrity validation, and NetworkX graph generation."""

    REQUIRED_LOCATION_FIELDS: Tuple[str, ...] = (
        "id",
        "name",
        "floor",
        "building",
        "category",
        "x",
        "y",
    )

    REQUIRED_CONNECTION_FIELDS: Tuple[str, ...] = (
        "source",
        "destination",
        "distance",
    )

    ACCESSIBILITY_BOOLEAN_FIELDS: Tuple[str, ...] = (
        "wheelchair_accessible",
        "has_stairs",
        "has_ramp",
        "has_elevator",
    )

    def __init__(self, data_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize the CampusMap instance.

        Args:
            data_path: Optional filesystem path to a JSON dataset to load immediately.
        """
        self.data_path: Optional[Path] = Path(data_path) if data_path else None
        self._raw_data: Dict[str, Any] = {}
        self._locations_by_id: Dict[str, Dict[str, Any]] = {}
        self._connections: List[Dict[str, Any]] = []
        self._graph: nx.Graph = nx.Graph()

        if self.data_path:
            self.load_from_json(self.data_path)

    @property
    def graph(self) -> nx.Graph:
        """Return the underlying NetworkX graph representation."""
        return self._graph

    @property
    def locations(self) -> Dict[str, Dict[str, Any]]:
        """Return a mapping of location ID to location dictionary."""
        return self._locations_by_id

    @property
    def connections(self) -> List[Dict[str, Any]]:
        """Return raw list of connections."""
        return self._connections

    def clone(self) -> CampusMap:
        """Create an isolated, fast in-memory copy of this CampusMap instance."""
        new_map = CampusMap()
        new_map.data_path = self.data_path
        new_map._raw_data = copy.deepcopy(self._raw_data)
        new_map._locations_by_id = {k: v.copy() for k, v in self._locations_by_id.items()}
        new_map._connections = [conn.copy() for conn in self._connections]
        new_map._graph = self._graph.copy()
        return new_map

    def load_from_json(self, file_path: Union[str, Path], use_cache: bool = True) -> None:
        """Load, validate, and build graph from a JSON file with memory caching.

        Args:
            file_path: Path to the JSON data file.
            use_cache: If True, reuses in-memory cached JSON if file modification time matches.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            CampusDataValidationError: If the loaded data violates schema constraints.
        """
        target_path = Path(file_path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"Campus data file not found: {target_path}")

        mtime = target_path.stat().st_mtime
        cache_key = str(target_path)

        if use_cache and cache_key in _FILE_CACHE and _FILE_CACHE[cache_key][0] == mtime:
            data = copy.deepcopy(_FILE_CACHE[cache_key][1])
        else:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if use_cache:
                _FILE_CACHE[cache_key] = (mtime, copy.deepcopy(data))

        self.data_path = target_path
        self.load_from_dict(data)

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Validate dictionary data and build the campus graph.

        Args:
            data: Parsed dictionary conforming to campus map schema.

        Raises:
            CampusDataValidationError: If data fails integrity checks.
        """
        self.validate_data(data, raise_on_error=True)

        self._raw_data = data
        self._locations_by_id = {loc["id"]: loc.copy() for loc in data.get("locations", [])}
        self._connections = [conn.copy() for conn in data.get("connections", [])]
        self.build_graph()

    def validate_data(self, data: Dict[str, Any], raise_on_error: bool = True) -> List[str]:
        """Perform comprehensive validation of campus map dataset.

        Checks:
        - Type of locations and connections collections.
        - Duplicate location IDs.
        - Missing required location fields.
        - Numeric coordinate checks.
        - Duplicate or self-loop connections.
        - Connections referencing non-existent locations.
        - Distance checks (positive numeric).
        - Estimated travel time checks (non-negative numeric if present).
        - Boolean types for accessibility flags.
        - Valid status values.

        Args:
            data: Dictionary representation of campus map.
            raise_on_error: If True, raises CampusDataValidationError upon any failure.

        Returns:
            List of detected error descriptions.
        """
        errors: List[str] = []

        if not isinstance(data, dict):
            errors.append("Dataset root must be a JSON object (dictionary).")
            if raise_on_error:
                raise CampusDataValidationError("Invalid root structure", errors)
            return errors

        locations = data.get("locations")
        connections = data.get("connections")

        if locations is None or not isinstance(locations, list):
            errors.append("'locations' field is required and must be a list.")
        if connections is None or not isinstance(connections, list):
            errors.append("'connections' field is required and must be a list.")

        if errors:
            if raise_on_error:
                raise CampusDataValidationError("Schema structure validation failed", errors)
            return errors

        seen_location_ids: set[str] = set()

        for idx, loc in enumerate(locations):
            if not isinstance(loc, dict):
                errors.append(f"Location at index {idx} must be an object.")
                continue

            # Check missing location fields
            for field in self.REQUIRED_LOCATION_FIELDS:
                if field not in loc or loc[field] is None:
                    errors.append(f"Location at index {idx} is missing required field '{field}'.")

            loc_id = loc.get("id")
            if loc_id is not None:
                if not isinstance(loc_id, str) or not loc_id.strip():
                    errors.append(f"Location ID at index {idx} must be a non-empty string.")
                elif loc_id in seen_location_ids:
                    errors.append(f"Duplicate location ID detected: '{loc_id}'.")
                else:
                    seen_location_ids.add(loc_id)

            # Check coordinates numeric validity
            for coord in ("x", "y"):
                val = loc.get(coord)
                if val is not None and not isinstance(val, (int, float)):
                    errors.append(
                        f"Location '{loc_id or idx}' coordinate '{coord}' must be numeric (got {type(val).__name__})."
                    )

        # Validate connections
        for idx, conn in enumerate(connections):
            if not isinstance(conn, dict):
                errors.append(f"Connection at index {idx} must be an object.")
                continue

            for field in self.REQUIRED_CONNECTION_FIELDS:
                if field not in conn or conn[field] is None:
                    errors.append(f"Connection at index {idx} is missing required field '{field}'.")

            src = conn.get("source")
            dst = conn.get("destination")

            if src is not None and src not in seen_location_ids:
                errors.append(
                    f"Connection at index {idx} references non-existent source location ID: '{src}'."
                )

            if dst is not None and dst not in seen_location_ids:
                errors.append(
                    f"Connection at index {idx} references non-existent destination location ID: '{dst}'."
                )

            if src is not None and dst is not None and src == dst:
                errors.append(f"Connection at index {idx} is an invalid self-loop ({src} -> {dst}).")

            dist = conn.get("distance")
            if dist is not None:
                if not isinstance(dist, (int, float)) or isinstance(dist, bool):
                    errors.append(
                        f"Connection between '{src}' and '{dst}' has non-numeric distance: {dist}."
                    )
                elif dist <= 0:
                    errors.append(
                        f"Connection between '{src}' and '{dst}' has non-positive distance: {dist}."
                    )

            est_time = conn.get("estimated_time")
            if est_time is not None:
                if not isinstance(est_time, (int, float)) or isinstance(est_time, bool):
                    errors.append(
                        f"Connection between '{src}' and '{dst}' has non-numeric estimated_time: {est_time}."
                    )
                elif est_time < 0:
                    errors.append(
                        f"Connection between '{src}' and '{dst}' has negative estimated_time: {est_time}."
                    )

            # Validate boolean accessibility flags
            for flag in self.ACCESSIBILITY_BOOLEAN_FIELDS:
                if flag in conn:
                    val = conn[flag]
                    if not isinstance(val, bool):
                        errors.append(
                            f"Connection between '{src}' and '{dst}' has invalid accessibility value for '{flag}': {val!r} (must be boolean)."
                        )

            # Status validation
            status = conn.get("status")
            if status is not None and not isinstance(status, str):
                errors.append(
                    f"Connection between '{src}' and '{dst}' has non-string status: {status!r}."
                )

        if errors and raise_on_error:
            raise CampusDataValidationError(
                f"Data integrity validation failed with {len(errors)} error(s).", errors
            )

        return errors

    def build_graph(self) -> nx.Graph:
        """Construct the NetworkX graph from validated locations and connections.

        Returns:
            Configured NetworkX Graph instance.
        """
        graph = nx.Graph()

        # Add nodes with metadata attributes
        for loc_id, loc in self._locations_by_id.items():
            node_attrs = loc.copy()
            node_attrs.update({
                "id": loc_id,
                "name": loc["name"],
                "floor": loc["floor"],
                "building": loc["building"],
                "category": loc["category"],
                "x": float(loc["x"]),
                "y": float(loc["y"]),
                "coordinates": (float(loc["x"]), float(loc["y"])),
            })
            graph.add_node(loc_id, **node_attrs)

        # Add edges with attributes
        for conn in self._connections:
            src = conn["source"]
            dst = conn["destination"]
            distance = float(conn["distance"])
            est_time = float(conn.get("estimated_time", distance * 0.8))

            raw_wa = conn.get("wheelchair_accessible")
            wa_val: Optional[bool] = bool(raw_wa) if isinstance(raw_wa, bool) else None

            edge_attrs = conn.copy()
            edge_attrs.update({
                "weight": distance,
                "distance": distance,
                "estimated_time": est_time,
                "wheelchair_accessible": wa_val,
                "has_stairs": bool(conn.get("has_stairs", False)),
                "has_ramp": bool(conn.get("has_ramp", False)),
                "has_elevator": bool(conn.get("has_elevator", False)),
                "status": str(conn.get("status", "open")),
            })
            graph.add_edge(src, dst, **edge_attrs)

        self._graph = graph
        return graph

    def get_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve details of a single location by its unique ID.

        Args:
            location_id: Unique string identifier.

        Returns:
            Location dictionary if found, None otherwise.
        """
        return self._locations_by_id.get(location_id)

    def get_all_locations(self) -> List[Dict[str, Any]]:
        """Retrieve list of all location dictionaries."""
        return list(self._locations_by_id.values())

    def get_connected_paths(self, location_id: str) -> List[Dict[str, Any]]:
        """Retrieve all connected paths (edges) incident to a location.

        Args:
            location_id: Unique identifier of the location.

        Returns:
            List of dictionaries containing neighbor ID, neighbor details, and edge attributes.
        """
        if location_id not in self._graph:
            return []

        results: List[Dict[str, Any]] = []
        for neighbor in self._graph.neighbors(location_id):
            edge_data = self._graph.get_edge_data(location_id, neighbor) or {}
            neighbor_node = self._locations_by_id.get(neighbor, {})
            results.append(
                {
                    "from_location_id": location_id,
                    "to_location_id": neighbor,
                    "target_location": neighbor_node,
                    "attributes": edge_data,
                }
            )

        return results

    def get_edge_data(self, source: str, destination: str) -> Optional[Dict[str, Any]]:
        """Retrieve edge attributes between two locations.

        Args:
            source: Source location ID.
            destination: Destination location ID.

        Returns:
            Edge attribute dict if connection exists, None otherwise.
        """
        if not self._graph.has_edge(source, destination):
            return None
        return dict(self._graph.get_edge_data(source, destination))

    def get_graph_summary(self) -> Dict[str, Any]:
        """Provide a summary of the current campus graph structure."""
        return {
            "num_nodes": self._graph.number_of_nodes(),
            "num_edges": self._graph.number_of_edges(),
            "is_connected": nx.is_connected(self._graph) if len(self._graph) > 0 else False,
            "density": nx.density(self._graph) if len(self._graph) > 0 else 0.0,
        }

    def validate_graph(self) -> "GraphValidationReport":
        """Run comprehensive graph topology, transition, and metadata validation."""
        return validate_campus_graph(self)


@dataclass
class GraphValidationReport:
    """Comprehensive topology, transition, weight, and accessibility integrity report."""

    total_nodes: int
    total_edges: int
    valid_edges: int
    invalid_edges: List[str] = field(default_factory=list)
    duplicate_edges: List[Tuple[str, str]] = field(default_factory=list)
    connected_components: int = 0
    unreachable_locations: List[str] = field(default_factory=list)
    wheelchair_connected_components: int = 0
    wheelchair_unreachable_locations: List[str] = field(default_factory=list)
    missing_floor_transitions: List[str] = field(default_factory=list)
    invalid_accessibility_metadata: List[str] = field(default_factory=list)
    invalid_pathway_weights: List[str] = field(default_factory=list)
    unknown_accessibility_edges: List[Tuple[str, str]] = field(default_factory=list)
    blocked_edges: List[Tuple[str, str]] = field(default_factory=list)
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize report to a dictionary for UI, logging, or JSON output."""
        return {
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "valid_edges": self.valid_edges,
            "invalid_edges_count": len(self.invalid_edges),
            "invalid_edges": self.invalid_edges,
            "duplicate_edges_count": len(self.duplicate_edges),
            "duplicate_edges": self.duplicate_edges,
            "connected_components": self.connected_components,
            "unreachable_locations": self.unreachable_locations,
            "wheelchair_connected_components": self.wheelchair_connected_components,
            "wheelchair_unreachable_locations": self.wheelchair_unreachable_locations,
            "missing_floor_transitions": self.missing_floor_transitions,
            "invalid_accessibility_metadata": self.invalid_accessibility_metadata,
            "invalid_pathway_weights": self.invalid_pathway_weights,
            "unknown_accessibility_edges": self.unknown_accessibility_edges,
            "blocked_edges": self.blocked_edges,
            "is_valid": self.is_valid,
        }


def validate_campus_graph(campus_map: CampusMap) -> GraphValidationReport:
    """Validate topology, weights, transitions, and accessibility metadata of a CampusMap."""
    graph = campus_map.graph
    loc_ids = set(campus_map.locations.keys())
    total_nodes = graph.number_of_nodes()
    total_edges = graph.number_of_edges()

    invalid_edges: List[str] = []
    duplicate_edges: List[Tuple[str, str]] = []
    invalid_accessibility_metadata: List[str] = []
    invalid_pathway_weights: List[str] = []
    unknown_accessibility_edges: List[Tuple[str, str]] = []
    blocked_edges: List[Tuple[str, str]] = []

    # 1. Check raw connections for duplicates and missing endpoints
    seen_pairs: Set[Tuple[str, str]] = set()
    for idx, conn in enumerate(campus_map.connections):
        u = conn.get("source")
        v = conn.get("destination")
        if u not in loc_ids or v not in loc_ids:
            invalid_edges.append(f"Raw connection[{idx}] references missing endpoint: {u} -> {v}")
            continue
        if u == v:
            invalid_edges.append(f"Raw connection[{idx}] is a self-loop on {u}")
            continue
        pair = (min(u, v), max(u, v))
        if pair in seen_pairs:
            duplicate_edges.append(pair)
        seen_pairs.add(pair)

    # 2. Check graph edge weights, statuses, and accessibility attributes
    valid_edge_count = 0
    wg = nx.Graph()
    for nid in graph.nodes():
        wg.add_node(nid)

    for u, v, data in graph.edges(data=True):
        edge_ok = True
        dist = data.get("distance")
        est_time = data.get("estimated_time", 0.0)
        if not isinstance(dist, (int, float)) or isinstance(dist, bool) or dist <= 0:
            invalid_pathway_weights.append(f"{u} <-> {v}: invalid distance ({dist})")
            invalid_edges.append(f"{u} <-> {v}: non-positive/invalid distance")
            edge_ok = False
        if not isinstance(est_time, (int, float)) or isinstance(est_time, bool) or est_time < 0:
            invalid_pathway_weights.append(f"{u} <-> {v}: negative/invalid estimated_time ({est_time})")
            edge_ok = False

        wa = data.get("wheelchair_accessible")
        has_stairs = bool(data.get("has_stairs", False))
        has_ramp = bool(data.get("has_ramp", False))
        has_elevator = bool(data.get("has_elevator", False))
        status = str(data.get("status", "open")).lower()

        if wa is None and not has_stairs and not has_ramp and not has_elevator:
            unknown_accessibility_edges.append((u, v))
            invalid_accessibility_metadata.append(f"{u} <-> {v}: missing accessibility classification")
        elif not isinstance(wa, bool) and wa is not None:
            invalid_accessibility_metadata.append(f"{u} <-> {v}: non-boolean wheelchair_accessible ({wa!r})")
            edge_ok = False

        if has_stairs and wa is True and not has_elevator and not has_ramp:
            invalid_accessibility_metadata.append(f"{u} <-> {v}: contradictory has_stairs=True and wheelchair_accessible=True")
            edge_ok = False

        if status in ("blocked", "closed", "maintenance", "under_maintenance"):
            blocked_edges.append((u, v))
        elif wa is True and not has_stairs:
            wg.add_edge(u, v, **data)

        if edge_ok:
            valid_edge_count += 1

    # 3. Overall graph connectivity & unreachable nodes
    comps = list(nx.connected_components(graph)) if total_nodes > 0 else []
    unreachable: List[str] = []
    if len(comps) > 1:
        main_comp = max(comps, key=len)
        for comp in comps:
            if comp is not main_comp:
                unreachable.extend(sorted(comp))

    # 4. Wheelchair subgraph connectivity
    w_comps = list(nx.connected_components(wg)) if total_nodes > 0 else []
    w_unreachable: List[str] = []
    if len(w_comps) > 1:
        w_main = max(w_comps, key=len)
        for comp in w_comps:
            if comp is not w_main:
                w_unreachable.extend(sorted(comp))

    # 5. Floor transition continuity check per indoor building
    missing_transitions: List[str] = []
    building_floors: Dict[str, Set[int]] = {}
    for loc in campus_map.get_all_locations():
        fl = int(loc.get("floor", 0))
        bldg = str(loc.get("building", "Main"))
        if fl >= 0:
            building_floors.setdefault(bldg, set()).add(fl)

    for bldg, floors in building_floors.items():
        sorted_floors = sorted(floors)
        for idx in range(len(sorted_floors) - 1):
            f_low = sorted_floors[idx]
            f_high = sorted_floors[idx + 1]
            if f_high - f_low == 1:
                has_link = False
                for u, v in graph.edges():
                    lu = campus_map.get_location(u) or {}
                    lv = campus_map.get_location(v) or {}
                    fu, fv = int(lu.get("floor", 0)), int(lv.get("floor", 0))
                    if {fu, fv} == {f_low, f_high}:
                        has_link = True
                        break
                if not has_link:
                    missing_transitions.append(f"{bldg}: missing vertical link between Floor {f_low} and Floor {f_high}")

    is_valid = (
        len(invalid_edges) == 0
        and len(duplicate_edges) == 0
        and len(unreachable) == 0
        and len(missing_transitions) == 0
        and len(invalid_accessibility_metadata) == 0
        and len(invalid_pathway_weights) == 0
    )

    return GraphValidationReport(
        total_nodes=total_nodes,
        total_edges=total_edges,
        valid_edges=valid_edge_count,
        invalid_edges=invalid_edges,
        duplicate_edges=duplicate_edges,
        connected_components=len(comps),
        unreachable_locations=sorted(unreachable),
        wheelchair_connected_components=len(w_comps),
        wheelchair_unreachable_locations=sorted(w_unreachable),
        missing_floor_transitions=missing_transitions,
        invalid_accessibility_metadata=invalid_accessibility_metadata,
        invalid_pathway_weights=invalid_pathway_weights,
        unknown_accessibility_edges=unknown_accessibility_edges,
        blocked_edges=blocked_edges,
        is_valid=is_valid,
    )


def load_campus_map(file_path: Optional[Union[str, Path]] = None) -> CampusMap:
    """Helper function to instantiate and load a CampusMap.

    If file_path is omitted, loads data/campus_map.json relative to project root.
    """
    if file_path is None:
        file_path = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
    return CampusMap(file_path)
