# Patches for upstream `base-app`

`0001-base-app-migrations-and-compression.patch` adds gzip compression,
app/schema compatibility checks, and a data-migration route to
`base_app.ProjectManager` / `base_app.AbstractProject` (see the app-side
usage in `../app/GSProject.py`, and `../AGENTS.md` if it documents the
project-file format). It is **not applied to any code in this repo** — this
repo only depends on `base-app` via git (see `pyproject.toml`'s
`[tool.uv.sources]`), so the change has to land in the `base-app` repo
itself and be released there before this app can use it.

Verified against the commit currently pinned in this repo's
`pyproject.toml` (`base-app` tag `v0.1.0`, commit `1bb503e`), which is also
that repo's current `main` HEAD.

To apply it there:

```sh
cd /path/to/base-app
git checkout -b add-migrations-compression main
git am /path/to/this/patch  # or: git apply --index, then commit yourself
```

Then bump `pyproject.toml`'s `version`, tag/release a new `base-app` version,
and update this repo's `[tool.uv.sources]` pin (`tag = "v0.1.0"`) to the new
tag so `uv sync` picks it up.

Once applied, no changes are needed in `GSProject` beyond what's already in
this repo (`SCHEMA_VERSION` / `migrations()`) for existing project files to
keep opening; add a migration there the next time `GSProject`'s saved data
shape changes.
