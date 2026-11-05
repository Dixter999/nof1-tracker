"""Agent rules must never tell an agent to kill processes by name or pattern.

A pattern kill (`pkill -f "jest|pytest"`) also SIGTERMs CI jobs and other
agents' tests on a shared host (veracrew#2296: exit 143 on dixter-org).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE_DIRS = ("rules", "quick-ref", "agents", "commands")
PATTERN_KILL = re.compile(r"\b(pkill|killall)\b")


def _agent_rule_files() -> list[Path]:
    files: list[Path] = []
    for name in RULE_DIRS:
        base = ROOT / ".claude" / name
        files += [p for p in base.rglob("*") if p.suffix in (".md", ".xml")]
    files += [p for p in (ROOT / "AGENTS.md", ROOT / "CLAUDE.md") if p.is_file()]
    return sorted(files)


def test_agent_rules_never_kill_processes_by_pattern():
    files = _agent_rule_files()
    # control: the scan actually sees the rule files, so an empty pass is impossible
    assert ROOT / ".claude" / "rules" / "test-execution.md" in files, (
        f"rule scan found no test-execution.md under {ROOT} ({len(files)} files)"
    )
    hits = [
        f"{p.relative_to(ROOT)}:{n}: {line.strip()}"
        for p in files
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
        if PATTERN_KILL.search(line) and not line.lstrip().startswith(">")
    ]
    assert not hits, "pattern-kill instructions in agent rules:\n" + "\n".join(hits)
