# tools/traceability.py
#
# Generates docs/evidence/traceability.md - the requirements traceability matrix that
# is the evidence for the assignment's "Automated Verification of Requirements"
# deliverable, and a figure in the technical report.
#
# D-038 is the reason this file reads two sources rather than one. Rows come from
# docs/REQUIREMENTS.md, not from the collected pytest markers. A matrix assembled from
# markers can only contain requirements that already have tests, so a requirement
# nobody covered vanishes from the document and the matrix silently asserts complete
# coverage. Driving the rows from the register turns an uncovered requirement into a
# visible row, which is the thing the deliverable is marked on.
#
# D-038 also records what the first run found: six requirements had no test, and three
# of those carried a status of VERIFIED or BUILT. None was unverified - each is checked
# by branch protection, by the deployment, or by the coverage gate. The register
# therefore carries a "Verified by" column naming the mechanism, and this script reports
# a missing test as a gap only where the register said to expect one.
#
# Collection is in-process - pytest.main with a plugin object - rather than a
# subprocess whose "--collect-only -q" output is parsed as text. Markers then arrive
# as objects with their arguments intact, instead of as output whose shape is free to
# change between pytest releases.
#
# The repository root is derived from this file's own location, never from the working
# directory, for the same reason every tools\ script derives it from $PSScriptRoot: an
# absolute path written into a script is a path that has to be maintained (D-027).

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_FILE = REPO_ROOT / "docs" / "REQUIREMENTS.md"
OUTPUT_FILE = REPO_ROOT / "docs" / "evidence" / "traceability.md"

# A requirement row is the only row in the register whose first cell is an ID. The file
# also holds a mechanism-token table and a "Mapping to the assignment's functional
# brief" table, and matching on the ID shape keeps both out without this script needing
# to know where the requirement tables start or stop.
REQ_ROW = re.compile(
    r"^\|\s*(REQ-[FN]-\d{3})\s*\|(.+?)\|\s*(\d+)\s*\|\s*([A-Z]+)\s*\|\s*(.+?)\s*\|\s*$"
)

# The marker names that record what kind of test it is. The assignment assesses unit
# tests and integration tests as separate criteria, so the matrix reports the split
# per requirement rather than a single count.
KIND_MARKERS = ("unit", "integration")

# The mechanism token that means "a pytest test is expected to exist for this". A
# requirement naming any other mechanism is verified somewhere this script cannot see,
# and its empty test list is a fact rather than a finding.
SUITE = "suite"

# A requirement in this state is cut on purpose, with a dated reason in the register.
# It is not a coverage gap and --check must not fail on it.
DEFERRED = "DEFERRED"


@dataclass
class Requirement:
    """One row of the register, with whatever tests were found for it."""

    req_id: str
    text: str
    tier: int
    status: str
    mechanisms: tuple
    tests: list = field(default_factory=list)

    @property
    def is_covered(self) -> bool:
        return bool(self.tests)

    @property
    def expects_tests(self) -> bool:
        return SUITE in self.mechanisms

    @property
    def is_gap(self) -> bool:
        """A gap is a requirement that named the suite and then had no test in it.

        A requirement verified by the pipeline, by branch protection, by the coverage
        gate or by the deployment is not a gap for having no test - it was never going
        to have one, and reporting it as missing is what the first version of this
        script got wrong.
        """
        if self.is_covered or self.status == DEFERRED:
            return False
        return self.expects_tests


@dataclass
class CollectedTest:
    """One test function, with the markers that matter to this report."""

    nodeid: str
    kinds: tuple
    reqs: tuple


class ReqMarkerCollector:
    """A pytest plugin that keeps the collected items instead of running them.

    pytest_collection_modifyitems fires after collection and before any test executes,
    which is exactly the point at which the marker data exists and nothing has cost
    anything to run.
    """

    def __init__(self) -> None:
        self.tests: list[CollectedTest] = []

    def pytest_collection_modifyitems(self, session, config, items) -> None:
        for item in items:
            reqs = []
            for mark in item.iter_markers("req"):
                # req(id) takes one argument, but reading all of them means a test
                # that verifies two requirements is recorded against both rather than
                # silently truncated.
                reqs.extend(str(arg) for arg in mark.args)
            kinds = tuple(
                name
                for name in KIND_MARKERS
                if any(mark.name == name for mark in item.iter_markers())
            )
            self.tests.append(
                CollectedTest(nodeid=item.nodeid, kinds=kinds, reqs=tuple(reqs))
            )


def parse_mechanisms(cell: str) -> tuple:
    """Read the Verified by cell: comma-separated tokens, backticks optional."""
    tokens = []
    for raw in cell.split(","):
        token = raw.strip().strip("`").strip()
        if token:
            tokens.append(token)
    return tuple(tokens)


def parse_requirements(path: Path) -> list[Requirement]:
    """Read the register's requirement tables in file order."""
    requirements: list[Requirement] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = REQ_ROW.match(line.strip())
        if match is None:
            continue
        req_id, text, tier, status, mechanisms = match.groups()
        requirements.append(
            Requirement(
                req_id=req_id,
                text=text.strip(),
                tier=int(tier),
                status=status.strip(),
                mechanisms=parse_mechanisms(mechanisms),
            )
        )
    return requirements


def collect_tests() -> tuple[list[CollectedTest], int, str]:
    """Collect the suite without running it, capturing pytest's own output.

    --no-cov is not optional. addopts in pyproject.toml carries --cov-report=xml, so a
    collect-only run without it rewrites coverage.xml at the repository root with an
    empty report - destroying the real coverage evidence as a side effect of
    generating the traceability evidence.

    pytest's output is captured rather than printed so that this script keeps the
    two-line console contract in CLAUDE.md Section 4. It is returned so that a failed
    collection can still be shown.
    """
    import pytest

    collector = ReqMarkerCollector()
    buffer = io.StringIO()
    # pytest infers its rootdir from the ini file and the arguments; running from the
    # repository root removes the question of where this script was invoked from.
    os.chdir(REPO_ROOT)
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        exit_code = pytest.main(
            ["--collect-only", "--no-cov", "-q"], plugins=[collector]
        )
    return collector.tests, int(exit_code), buffer.getvalue()


def join(requirements: list[Requirement], tests: list[CollectedTest]) -> list[str]:
    """Attach tests to requirements. Returns any marker naming an unknown ID.

    A marker that names a requirement the register does not hold is worth reporting
    rather than dropping: it means a test cites an ID that was renamed, mistyped in a
    way --strict-markers cannot catch, or never existed.
    """
    by_id = {requirement.req_id: requirement for requirement in requirements}
    unknown: list[str] = []
    for test in tests:
        for req_id in test.reqs:
            if req_id in by_id:
                by_id[req_id].tests.append(test)
            else:
                unknown.append(f"{test.nodeid} -> {req_id}")
    return unknown


def kind_summary(requirement: Requirement) -> str:
    units = sum(1 for test in requirement.tests if "unit" in test.kinds)
    integrations = sum(1 for test in requirement.tests if "integration" in test.kinds)
    return f"{units} / {integrations}"


def render(
    requirements: list[Requirement],
    tests: list[CollectedTest],
    unknown: list[str],
) -> str:
    """Build the matrix document. ASCII only, per D-018."""
    covered = [r for r in requirements if r.is_covered]
    gaps = [r for r in requirements if r.is_gap]
    elsewhere = [r for r in requirements if not r.is_covered and not r.expects_tests]
    unmapped = [t for t in tests if not t.reqs]

    lines: list[str] = []
    lines.append("# QVS Requirements Traceability Matrix")
    lines.append("")
    lines.append(
        "Generated by `tools/traceability.py` on "
        f"{date.today().isoformat()}. Do not edit by hand - it is regenerated."
    )
    lines.append("")
    lines.append(
        "Rows come from `docs/REQUIREMENTS.md`; tests come from the `req` markers "
        "pytest collects. D-038 explains why the rows are driven by the register "
        "rather than by the markers: a requirement with no test has to be visible, "
        "and a matrix assembled from markers alone cannot show one."
    )
    lines.append("")
    lines.append(
        "`Verified by` is the register's own account of how each requirement is "
        "checked without a human deciding to check it. Only a requirement naming "
        "`suite` is expected to have a test here; the others are verified by branch "
        "protection, by a pipeline job, by the coverage threshold or by the running "
        "deployment, and are listed with no test because that is correct rather than "
        "because something is missing."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Measure | Value |")
    lines.append("|---|---|")
    lines.append(f"| Requirements in the register | {len(requirements)} |")
    lines.append(f"| Requirements with at least one test | {len(covered)} |")
    lines.append(f"| Requirements verified outside the test suite | {len(elsewhere)} |")
    lines.append(f"| Gaps - named `suite`, no test | {len(gaps)} |")
    lines.append(f"| Tests collected | {len(tests)} |")
    lines.append(f"| Tests carrying no req marker | {len(unmapped)} |")
    lines.append("")
    lines.append("## Matrix")
    lines.append("")
    lines.append("`Unit / Integration` counts the two markers the assignment assesses")
    lines.append("separately. A test may carry neither, and is still counted in Tests.")
    lines.append("")
    lines.append("| ID | Tier | Status | Verified by | Tests | Unit / Integration |")
    lines.append("|---|---|---|---|---|---|")
    for requirement in requirements:
        mechanisms = ", ".join(requirement.mechanisms)
        if requirement.tests:
            count = str(len(requirement.tests))
        elif requirement.is_gap:
            count = "GAP"
        else:
            count = "n/a"
        lines.append(
            f"| {requirement.req_id} | {requirement.tier} | {requirement.status} "
            f"| {mechanisms} | {count} | {kind_summary(requirement)} |"
        )
    lines.append("")
    lines.append("## Requirements and the tests that verify them")
    lines.append("")
    for requirement in requirements:
        lines.append(f"### {requirement.req_id} - {requirement.text}")
        lines.append("")
        mechanisms = ", ".join(requirement.mechanisms)
        lines.append(
            f"Tier {requirement.tier}. Status {requirement.status}. "
            f"Verified by {mechanisms}."
        )
        lines.append("")
        if requirement.tests:
            for test in sorted(requirement.tests, key=lambda t: t.nodeid):
                kinds = ", ".join(test.kinds) if test.kinds else "unmarked"
                lines.append(f"- `{test.nodeid}` ({kinds})")
        elif requirement.status == DEFERRED:
            lines.append("- Deferred on purpose - see `docs/REQUIREMENTS.md`.")
        elif requirement.is_gap:
            lines.append("- GAP. This requirement names `suite` and no test cites it.")
        else:
            lines.append(f"- No test, and none expected. Verified by {mechanisms}.")
        lines.append("")

    lines.append("## Tests carrying no req marker")
    lines.append("")
    if unmapped:
        lines.append(
            "These tests run and pass, and no requirement claims them. Each is either "
            "a requirement the register is missing or a test that should cite one."
        )
        lines.append("")
        for test in sorted(unmapped, key=lambda t: t.nodeid):
            lines.append(f"- `{test.nodeid}`")
    else:
        lines.append("None. Every collected test cites a requirement.")
    lines.append("")

    if unknown:
        lines.append("## Markers naming an unknown requirement")
        lines.append("")
        lines.append(
            "A test cites an ID the register does not hold. --strict-markers catches "
            "a misspelled marker name, not a wrong argument to a correct one."
        )
        lines.append("")
        for entry in sorted(unknown):
            lines.append(f"- `{entry}`")
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the QVS requirements traceability matrix."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Exit non-zero when a requirement naming the suite has no test. The "
            "matrix is written either way."
        ),
    )
    args = parser.parse_args(argv)

    requirements = parse_requirements(REQUIREMENTS_FILE)
    if not requirements:
        print("TRACEABILITY FAILED - no requirements parsed from the register")
        print(str(REQUIREMENTS_FILE))
        return 2

    tests, exit_code, output = collect_tests()
    # pytest returns 0 for a clean collection and 5 when it collected nothing. Any
    # other code means collection itself failed - most often ImproperlyConfigured,
    # because tools\Set-Env.ps1 was not run in this terminal.
    if exit_code != 0:
        print(f"TRACEABILITY FAILED - pytest collection exited {exit_code}")
        print(str(REQUIREMENTS_FILE))
        sys.stderr.write(output)
        return 2

    unknown = join(requirements, tests)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" is explicit. Python would otherwise translate to CRLF on Windows
    # and the file would arrive contradicting .gitattributes (D-012).
    with open(OUTPUT_FILE, "w", encoding="ascii", newline="\n") as handle:
        handle.write(render(requirements, tests, unknown))

    gaps = [r for r in requirements if r.is_gap]
    unmapped = [t for t in tests if not t.reqs]
    verdict = "TRACEABILITY OK"
    if gaps:
        gap_ids = ", ".join(r.req_id for r in gaps)
        verdict = (
            f"TRACEABILITY GAPS - {len(gaps)} named the suite with no test: {gap_ids}"
        )
    print(
        f"{verdict} ({len(requirements)} requirements, {len(tests)} tests collected, "
        f"{len(unmapped)} citing nothing)"
    )
    print(str(OUTPUT_FILE))

    if args.check and gaps:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
