"""Serialization service — object↔dict conversion for all UI models.

Avoids duplicated serialization logic across services.
All serializers are pure functions — no side effects.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


# ------------------------------------------------------------------
# Project
# ------------------------------------------------------------------

def serialize_project(project: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": project.get("id", ""),
        "name": project.get("name", ""),
        "description": project.get("description", ""),
        "source": project.get("source", ""),
        "tags": project.get("tags", []),
        "status": project.get("status", "active"),
        "version": project.get("version", 1),
        "created": _serialize_dt(project.get("created")),
        "modified": _serialize_dt(project.get("modified")),
    }


def deserialize_project(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": data.get("id", ""),
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "source": data.get("source", ""),
        "tags": data.get("tags", []),
        "status": data.get("status", "active"),
        "version": data.get("version", 1),
        "created": _deserialize_dt(data.get("created")),
        "modified": _deserialize_dt(data.get("modified")),
    }


def serialize_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [serialize_project(p) for p in projects]


def deserialize_projects(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [deserialize_project(p) for p in data]


# ------------------------------------------------------------------
# Connection
# ------------------------------------------------------------------

def serialize_connection(conn: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": conn.get("id", ""),
        "name": conn.get("name", ""),
        "conn_type": conn.get("conn_type", "local"),
        "path": conn.get("path", ""),
        "description": conn.get("description", ""),
        "status": conn.get("status", "disconnected"),
        "favorite": conn.get("favorite", False),
        "connected_at": _serialize_dt(conn.get("connected_at")),
        "created": _serialize_dt(conn.get("created")),
    }


def deserialize_connection(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": data.get("id", ""),
        "name": data.get("name", ""),
        "conn_type": data.get("conn_type", "local"),
        "path": data.get("path", ""),
        "description": data.get("description", ""),
        "status": data.get("status", "disconnected"),
        "favorite": data.get("favorite", False),
        "connected_at": _deserialize_dt(data.get("connected_at")),
        "created": _deserialize_dt(data.get("created")),
        "file_count": 0,
    }


def serialize_connections(conns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [serialize_connection(c) for c in conns]


def deserialize_connections(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [deserialize_connection(c) for c in data]


# ------------------------------------------------------------------
# WorkspaceContext / Session
# ------------------------------------------------------------------

def serialize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "current_project_id": context.get("current_project_id"),
        "current_connection_id": context.get("current_connection_id"),
        "current_workspace": context.get("current_workspace", "home"),
        "navigation_history": context.get("navigation_history", []),
        "theme": context.get("theme", "light"),
        "sidebar_collapsed": context.get("sidebar_collapsed", False),
        "inspector_visible": context.get("inspector_visible", True),
        "window_size": context.get("window_size", ""),
        "splitter_position": context.get("splitter_position", 300),
        "version": 1,
    }


def deserialize_context(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "current_project_id": data.get("current_project_id"),
        "current_connection_id": data.get("current_connection_id"),
        "current_workspace": data.get("current_workspace", "home"),
        "navigation_history": data.get("navigation_history", []),
        "theme": data.get("theme", "light"),
        "sidebar_collapsed": data.get("sidebar_collapsed", False),
        "inspector_visible": data.get("inspector_visible", True),
        "window_size": data.get("window_size", ""),
        "splitter_position": data.get("splitter_position", 300),
        "version": data.get("version", 1),
    }


# ------------------------------------------------------------------
# User preferences
# ------------------------------------------------------------------

def serialize_preferences(prefs: Dict[str, Any]) -> Dict[str, Any]:
    return dict(prefs)


def deserialize_preferences(data: Dict[str, Any]) -> Dict[str, Any]:
    return dict(data)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _serialize_dt(dt: Any) -> Optional[str]:
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)


def _deserialize_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
    return None
