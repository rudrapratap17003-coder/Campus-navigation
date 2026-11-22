"""Room-level destination intelligence, search ranking, and categorization engine.

Phase 16 Upgrade:
Provides comprehensive, case-insensitive fuzzy and semantic search across all campus
facilities, buildings, floors, laboratories, departments, and colloquial aliases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from modules.campus_map import CampusMap
from modules.navigation_instructions import format_floor_name


@dataclass
class DestinationSearchResult:
    """Structured search result for a matching campus destination."""

    location_id: str
    name: str
    building: str
    floor: int
    floor_name: str
    category: str
    department: str
    verification_status: str
    confidence_level: str
    match_type: str  # 'exact_id', 'exact_name', 'keyword', 'partial_name', 'category', 'building', 'floor'
    score: float
    wheelchair_accessible: bool = True
    amenities: List[str] = field(default_factory=list)
    search_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "location_id": self.location_id,
            "name": self.name,
            "building": self.building,
            "floor": self.floor,
            "floor_name": self.floor_name,
            "category": self.category,
            "department": self.department,
            "verification_status": self.verification_status,
            "confidence_level": self.confidence_level,
            "match_type": self.match_type,
            "score": round(self.score, 2),
            "wheelchair_accessible": self.wheelchair_accessible,
            "amenities": self.amenities,
            "search_keywords": self.search_keywords,
        }


def _normalize(text: str) -> str:
    """Normalize text for fuzzy matching."""
    return re.sub(r"[^\w\s]", " ", text.lower()).strip()


def search_destinations(
    query: str,
    campus_map: CampusMap,
    floor_filter: Optional[int] = None,
    category_filter: Optional[str] = None,
    max_results: int = 50,
    limit: Optional[int] = None,
) -> List[DestinationSearchResult]:
    """Search campus destinations using multi-field matching and relevance ranking.

    Args:
        query: User search string (e.g. 'HPC', 'AI Lab', 'Library', 'Mechanical').
        campus_map: CampusMap instance with populated locations.
        floor_filter: Optional floor number to restrict results (-1 to 4).
        category_filter: Optional category to filter (e.g. 'lab', 'classroom', 'library').
        max_results: Maximum results to return.
        limit: Optional alias for max_results.

    Returns:
        List of DestinationSearchResult ranked by relevance score (highest first).
    """
    if limit is not None:
        max_results = limit
    clean_query = query.strip()
    norm_query = _normalize(clean_query)
    query_tokens = set(norm_query.split()) if norm_query else set()

    results: List[DestinationSearchResult] = []
    locations = campus_map.locations.values()

    # Floor name mapping helper
    floor_aliases = {
        -1: ["outdoor", "ground grounds", "campus grounds", "outside", "yard"],
        0: ["ground", "ground floor", "level 0", "floor 0", "gf"],
        1: ["first", "first floor", "level 1", "floor 1", "1f"],
        2: ["second", "second floor", "level 2", "floor 2", "2f"],
        3: ["third", "third floor", "level 3", "floor 3", "3f"],
        4: ["fourth", "fourth floor", "level 4", "floor 4", "4f"],
    }

    for loc in locations:
        loc_id = loc.get("id", "")
        name = loc.get("name", "")
        floor = int(loc.get("floor", 0))
        building = loc.get("building", "")
        category = loc.get("category", "")
        dept = loc.get("department", "General Campus")
        verif_status = loc.get("verification_status", "APPROXIMATE")
        conf_level = loc.get("confidence_level", "Moderate")
        wc = bool(loc.get("wheelchair_accessible", True))
        amens = loc.get("amenities", [])
        keywords = loc.get("search_keywords", [])

        # Apply floor filter if provided
        if floor_filter is not None and floor != floor_filter:
            continue

        # Apply category filter if provided
        if category_filter and category_filter.lower() != "all":
            if category.lower() != category_filter.lower():
                continue

        # If query is empty, return all conforming to filters
        if not clean_query:
            results.append(
                DestinationSearchResult(
                    location_id=loc_id,
                    name=name,
                    building=building,
                    floor=floor,
                    floor_name=format_floor_name(floor),
                    category=category,
                    department=dept,
                    verification_status=verif_status,
                    confidence_level=conf_level,
                    match_type="all",
                    score=1.0,
                    wheelchair_accessible=wc,
                    amenities=amens,
                    search_keywords=keywords,
                )
            )
            continue

        score = 0.0
        match_type = "none"

        # 1. Exact ID match (highest priority)
        if clean_query.lower() == loc_id.lower():
            score = 100.0
            match_type = "exact_id"
        elif clean_query.lower() in loc_id.lower():
            score = max(score, 85.0)
            match_type = "partial_id"

        # 2. Exact or Alias / Keyword match
        norm_name = _normalize(name)
        if norm_query and norm_query == norm_name:
            score = max(score, 95.0)
            match_type = "exact_name"

        for kw in keywords:
            norm_kw = _normalize(kw)
            if norm_query == norm_kw:
                score = max(score, 90.0)
                match_type = "keyword_exact"
            elif norm_query in norm_kw or norm_kw in norm_query:
                score = max(score, 75.0)
                if match_type == "none":
                    match_type = "keyword_partial"

        # 3. Partial name matching
        if norm_query and norm_query in norm_name:
            score = max(score, 80.0)
            if match_type == "none":
                match_type = "partial_name"

        # 4. Token overlap matching in name, department, amenities
        searchable_text = f"{norm_name} {_normalize(dept)} {_normalize(building)} {_normalize(category)} {' '.join(_normalize(a) for a in amens)}"
        matched_tokens = sum(1 for t in query_tokens if t in searchable_text)
        if query_tokens and matched_tokens > 0:
            token_score = (matched_tokens / len(query_tokens)) * 60.0
            if token_score > score:
                score = token_score
                if match_type == "none":
                    match_type = "token_match"

        # 5. Floor-specific queries (e.g. 'Fourth Floor', 'Ground Floor', '1F')
        for fl_num, fl_terms in floor_aliases.items():
            if floor == fl_num and any(term in norm_query for term in fl_terms):
                if score < 40.0:
                    score = 40.0
                    if match_type == "none":
                        match_type = "floor_match"

        # 6. Category queries (e.g. 'lab', 'library', 'sports')
        if category and norm_query in _normalize(category):
            if score < 50.0:
                score = 50.0
                if match_type == "none":
                    match_type = "category_match"

        if score > 0.0:
            results.append(
                DestinationSearchResult(
                    location_id=loc_id,
                    name=name,
                    building=building,
                    floor=floor,
                    floor_name=format_floor_name(floor),
                    category=category,
                    department=dept,
                    verification_status=verif_status,
                    confidence_level=conf_level,
                    match_type=match_type,
                    score=score,
                    wheelchair_accessible=wc,
                    amenities=amens,
                    search_keywords=keywords,
                )
            )

    # Sort descending by score, then ascending by floor, then name
    results.sort(key=lambda r: (-r.score, r.floor, r.name))
    return results[:max_results]


def group_destinations_by_building_and_floor(
    results: List[Any],
) -> Dict[str, Dict[str, List[Any]]]:
    """Group search results or locations by Building and Floor level for organized UI presentation.

    Returns:
        Hierarchical dict: { building_name: { floor_name: [results...] } }
    """
    grouped: Dict[str, Dict[str, List[Any]]] = {}
    for r in results:
        if isinstance(r, dict):
            bld = r.get("building", "Academic Complex")
            fl = int(r.get("floor", 0))
            fl_name = format_floor_name(fl)
        else:
            bld = r.building
            fl_name = r.floor_name
        if bld not in grouped:
            grouped[bld] = {}
        if fl_name not in grouped[bld]:
            grouped[bld][fl_name] = []
        grouped[bld][fl_name].append(r)
    return grouped


def get_search_suggestions(
    query: str,
    campus_map: CampusMap,
    limit: int = 8,
) -> List[str]:
    """Generate search autocomplete suggestion phrases based on partial input.

    Args:
        query: Current user text typed into search input.
        campus_map: CampusMap instance.
        limit: Max suggestion phrases.

    Returns:
        List of suggestion strings.
    """
    if not query.strip():
        # Default prominent suggestions
        return [
            "HPC Supercomputing Cluster",
            "Computer Science & AI Lab 101",
            "Departmental Library",
            "Robotics & Autonomous Systems",
            "Sir M. Visvesvaraya Seminar Hall",
            "Main Campus Entrance Gate",
            "Accessible Restroom",
            "The Colosseum Sports Arena",
        ][:limit]

    results = search_destinations(query, campus_map, max_results=limit)
    suggestions: List[str] = []
    seen = set()

    for r in results:
        # Suggest shortest clear identifier
        sug = r.name
        if sug not in seen:
            seen.add(sug)
            suggestions.append(sug)
        if len(suggestions) >= limit:
            break

    return suggestions
