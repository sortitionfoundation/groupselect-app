import re
import subprocess


# Get runtime packages from uv export
export = subprocess.run(
    ["uv", "export", "--no-dev", "--no-hashes", "--format=requirements-txt"],
    capture_output=True, text=True, check=True
)

all_packages = []
for line in export.stdout.splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name = re.split(r'[@=><\s]', line)[0]
    if name:
        all_packages.append(name)

pyside_packages = [p for p in all_packages if p.lower().startswith("pyside6") or p.lower() == "shiboken6"]
other_packages = [p for p in all_packages if p not in pyside_packages]

subprocess.run(
    [
        "uv", "run", "pip-licenses",
        "--with-authors", "--with-urls", "--with-license-file", "--no-license-path",
        "--format=plain-vertical",
        "--packages", *other_packages,
        "--output-file=THIRD_PARTY_LICENSES.txt",
    ],
    check=True
)
