"""Assert that requirements.txt and the Nix Python environment agree.

Run by `checks.requirements-pins` in flake.nix.  ADR-004 keeps
requirements.txt as the supported path for a machine without Nix, which is
only safe while both paths install the same versions.  Nothing else makes
them agree, so this fails the build when they drift.

Takes the path to requirements.txt as its single argument, and resolves
versions from the environment it is run in.

A pin may carry extras, `mkdocs-material[imaging]==9.5.49`.  An extra is a
claim with no version in it, so what gets checked is that the extra exists
and that every dependency it would make pip install is present in the Nix
environment -- pythonEnv missing Pillow while requirements.txt promises it
is exactly the disagreement this check exists for, version or no version.
"""

import pathlib
import re
import sys
from importlib.metadata import PackageNotFoundError, metadata, requires, version

# A pinned direct dependency: `name==version` or `name[extra,...]==version`,
# comments and blanks skipped.  Extras carry no versions of their own -- pip
# resolves them like any other transitive dependency -- so for an extra the
# comparable claim is not "this version" but "the Nix environment provides
# this too", and check_extra below is what holds that.
PIN = re.compile(
    r"(?P<name>[A-Za-z0-9._-]+)"
    r"(?:\[(?P<extras>[A-Za-z0-9._,-]+)\])?"
    r"==(?P<version>[A-Za-z0-9.*+!-]+)"
)

# Inside a dependency's environment marker, the clause naming its extra:
# `extra == "imaging"`.  Quoting style varies between packaging tools.
EXTRA_MARKER = re.compile(r"""extra\s*==\s*['"](?P<extra>[^'"]+)['"]""")

DEP_NAME = re.compile(r"^[A-Za-z0-9._-]+")


def check_extra(name: str, extra: str, problems: list) -> list[str]:
    """Verify one extra of an installed package against this environment.

    Returns the names of the packages the extra pulled in, for the report.
    An unknown extra is an error rather than a silent no-match: a typo like
    [imagine] would otherwise select zero dependencies and pass vacuously.
    """
    provided = metadata(name).get_all("Provides-Extra") or []
    if extra not in provided:
        problems.append(
            f"{name}: requirements.txt names extra [{extra}], "
            f"which the package does not provide (has: {', '.join(provided)})"
        )
        return []

    found = []
    for req in requires(name) or []:
        spec, _, marker = req.partition(";")
        m = EXTRA_MARKER.search(marker)
        if not m or m.group("extra") != extra:
            continue
        dep = DEP_NAME.match(spec.strip()).group(0)
        try:
            found.append(f"{dep} {version(dep)}")
        except PackageNotFoundError:
            problems.append(
                f"{name}[{extra}]: pip would install {dep}, "
                "but it is missing from the Nix environment"
            )
    return found


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

        deps = []
        for extra in filter(None, (pin.group("extras") or "").split(",")):
            deps += check_extra(name, extra.strip(), problems)

        checked += 1
        print(f"{name} {got}" + (f"  (+ {', '.join(deps)})" if deps else ""))

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
