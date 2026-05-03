"""Project scanner — analyzes project structure for team context."""

import subprocess
from pathlib import Path

from pydantic import BaseModel, Field


class ProjectScan(BaseModel):
    """Result of scanning a project directory."""
    name: str = ""
    path: str = ""
    is_git: bool = False
    languages: dict[str, int] = Field(default_factory=dict, description="Language -> file count")
    total_files: int = 0
    total_dirs: int = 0
    has_readme: bool = False
    has_tests: bool = False
    has_ci: bool = False
    has_docker: bool = False
    frameworks: list[str] = []
    git_commits: int = 0
    recent_activity: str = ""
    file_tree: str = ""

    def summary(self) -> str:
        """Human-readable project summary."""
        lines = [f"📁 **{self.name}** ({self.path})"]
        lines.append(f"   Files: {self.total_files} | Dirs: {self.total_dirs}")

        if self.languages:
            top = sorted(self.languages.items(), key=lambda x: x[1], reverse=True)[:5]
            lang_str = ", ".join(f"{lang}: {count}" for lang, count in top)
            lines.append(f"   Languages: {lang_str}")

        if self.frameworks:
            lines.append(f"   Frameworks: {', '.join(self.frameworks)}")

        flags = []
        if self.is_git:
            flags.append(f"git ({self.git_commits} commits)")
        if self.has_tests:
            flags.append("tests")
        if self.has_ci:
            flags.append("CI/CD")
        if self.has_docker:
            flags.append("Docker")
        if flags:
            lines.append(f"   Features: {', '.join(flags)}")

        if self.recent_activity:
            lines.append(f"   Recent: {self.recent_activity}")

        return "\n".join(lines)


# Language detection by extension
LANG_MAP = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".jsx": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java",
    ".kt": "Kotlin", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
    ".c": "C", ".cpp": "C++", ".h": "C/C++", ".cs": "C#",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".md": "Markdown", ".yml": "YAML", ".yaml": "YAML",
    ".json": "JSON", ".toml": "TOML", ".sql": "SQL",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
}

# Framework detection
FRAMEWORK_MARKERS = {
    "package.json": "Node.js",
    "pyproject.toml": "Python",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "Gemfile": "Ruby",
    "pom.xml": "Java/Maven",
    "build.gradle": "Gradle",
    "next.config.js": "Next.js",
    "next.config.ts": "Next.js",
    "nuxt.config.ts": "Nuxt",
    "vite.config.ts": "Vite",
    "tailwind.config.js": "Tailwind",
    "tailwind.config.ts": "Tailwind",
    "django": "Django",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "requirements.txt": "Python",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    ".github/workflows": "GitHub Actions",
    ".gitlab-ci.yml": "GitLab CI",
    "Jenkinsfile": "Jenkins",
}

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".idea", ".vscode", "dist", "build", ".next", ".nuxt",
    "target", ".pytest_cache", ".ruff_cache", "matoi",
}


def scan_project(project_path: Path) -> ProjectScan:
    """Scan a project directory and return structured info."""
    scan = ProjectScan(
        name=project_path.name,
        path=str(project_path),
    )

    # Walk directory
    languages: dict[str, int] = {}
    total_files = 0
    total_dirs = 0
    frameworks: set[str] = set()
    tree_lines: list[str] = []

    for item in sorted(project_path.iterdir()):
        if item.name in IGNORE_DIRS or item.name.startswith("."):
            continue

        if item.is_file():
            total_files += 1
            ext = item.suffix.lower()
            if ext in LANG_MAP:
                lang = LANG_MAP[ext]
                languages[lang] = languages.get(lang, 0) + 1

            if item.name in FRAMEWORK_MARKERS:
                frameworks.add(FRAMEWORK_MARKERS[item.name])

            tree_lines.append(f"  {item.name}")

        elif item.is_dir():
            total_dirs += 1
            dir_name = item.name

            # Check framework markers in dirs
            if dir_name in FRAMEWORK_MARKERS:
                frameworks.add(FRAMEWORK_MARKERS[dir_name])

            # Count files in subdirs
            sub_count = 0
            for sub in item.rglob("*"):
                if sub.is_file() and not any(p in IGNORE_DIRS for p in sub.parts):
                    total_files += 1
                    sub_count += 1
                    ext = sub.suffix.lower()
                    if ext in LANG_MAP:
                        lang = LANG_MAP[ext]
                        languages[lang] = languages.get(lang, 0) + 1

                    # Check framework markers
                    if sub.name in FRAMEWORK_MARKERS:
                        frameworks.add(FRAMEWORK_MARKERS[sub.name])

            tree_lines.append(f"  {dir_name}/ ({sub_count} files)")

    scan.languages = languages
    scan.total_files = total_files
    scan.total_dirs = total_dirs
    scan.frameworks = sorted(frameworks)
    scan.file_tree = "\n".join(tree_lines[:20])

    # Check specific files
    scan.has_readme = (project_path / "README.md").exists() or (project_path / "readme.md").exists()
    scan.has_tests = (project_path / "tests").is_dir() or (project_path / "test").is_dir()
    scan.has_docker = (project_path / "Dockerfile").exists()
    scan.has_ci = (project_path / ".github" / "workflows").is_dir() or (project_path / ".gitlab-ci.yml").exists()

    # Git info
    if (project_path / ".git").exists():
        scan.is_git = True
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=project_path, capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                scan.git_commits = int(result.stdout.strip())

            result = subprocess.run(
                ["git", "log", "-1", "--format=%cr — %s"],
                cwd=project_path, capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                scan.recent_activity = result.stdout.strip()
        except (subprocess.TimeoutExpired, ValueError):
            pass

    return scan
