"""Campus map representation, data validation, and NetworkX spatial graph engine."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

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

            edge_attrs = conn.copy()
            edge_attrs.update({
                "weight": distance,
                "distance": distance,
                "estimated_time": est_time,
                "wheelchair_accessible": bool(conn.get("wheelchair_accessible", True)),
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


def load_campus_map(file_path: Optional[Union[str, Path]] = None) -> CampusMap:
    """Helper function to instantiate and load a CampusMap.

    If file_path is omitted, loads data/campus_map.json relative to project root.
    """
    if file_path is None:
        file_path = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
    return CampusMap(file_path)
