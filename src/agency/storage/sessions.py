"""Session persistence — save/load session state."""

from pathlib import Path

from agency.core.session import Session


class SessionStore:
    """Persists sessions to JSON files."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, session: Session) -> None:
        path = self.storage_dir / f"{session.id}.json"
        path.write_text(session.model_dump_json(indent=2))

    def load(self, session_id: str) -> Session | None:
        path = self.storage_dir / f"{session_id}.json"
        if not path.exists():
            return None
        return Session.model_validate_json(path.read_text())

    def list_recent(self, limit: int = 10) -> list[Session]:
        files = sorted(self.storage_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        sessions = []
        for f in files[:limit]:
            sessions.append(Session.model_validate_json(f.read_text()))
        return sessions
