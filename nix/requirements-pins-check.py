"""Assert that requirements.txt and the Nix Python environment agree.

Run by `checks.requirements-pins` in flake.nix.  ADR-004 keeps
requirements.txt as the supported path for a machine without Nix, which is
only safe while both paths install the same versions.  Nothing else makes
them agree, so this fails the build when they drift.

Takes the path to requirements.txt as its single argument, and resolves
versions from the environment it is run in.
"""

import pathlib
import re
import sys
from importlib.metadata import PackageNotFoundError, version

# A pinned direct dependency: `name==version`, comments and blanks skipped.
PIN = re.compile(r"(?P<name>[A-Za-z0-9._-]+)==(?P<version>[A-Za-z0-9.*+!-]+)")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <path to requirements.txt>")

    requirements = pathlib.Path(sys.argv[1])
    problems = []
    checked = 0

    for lineno, raw in enumerate(requirements.read_text().splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        pin = PIN.fullmatch(line)
        if pin is None:
            # An unpinned or range-specified requirement cannot be compared,
            # and silently skipping it would hide exactly the drift this
            # check is for.
            problems.append(f"line {lineno}: {line!r} is not a `name==version` pin")
            continue

        name, want = pin.group("name"), pin.group("version")
        try:
            got = version(name)
        except PackageNotFoundError:
            problems.append(
                f"{name}: requirements.txt pins {want}, "
                "but it is missing from the Nix environment"
            )
            continue

        if got != want:
            problems.append(
                f"{name}: requirements.txt pins {want}, the Nix environment has {got}"
            )
            continue

        checked += 1
        print(f"{name} {got}")

    if problems:
        print(
            "\nrequirements.txt and flake.nix disagree:\n  "
            + "\n  ".join(problems)
            + "\n\nFix by bumping requirements.txt, or by adjusting the override "
            "in flake.nix so both paths install the same versions.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if checked == 0:
        sys.exit(f"no pins found in {requirements}: the check would pass vacuously")

    print(f"\n{checked} pinned dependencies match the Nix environment")


if __name__ == "__main__":
    main()
