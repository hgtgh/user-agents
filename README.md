# user-agents

Generate realistic, up-to-date User-Agent strings from official browser release feeds.

Ship ready-to-use JSON datasets for testing, scraping, and browser simulation workflows.

## Why this project?

Hardcoded User-Agent datasets become stale quickly and lead to unrealistic fingerprints.

This project keeps them current by:

- Fetching stable versions from official browser release feeds
- Rendering consistent User-Agent variants
- Generating both plain and metadata-rich JSON outputs
- Refreshing the dataset daily via GitHub Actions

## Supported Browsers and OS

Currently generated variants:

- **Chrome**: Windows, macOS, Linux
- **Firefox**: Windows, macOS, Linux, Ubuntu
- **Microsoft Edge**: Windows
- **Safari**: macOS

## Usage

Outputs:

- [`data/user-agents.json`](https://raw.githubusercontent.com/hgtgh/user-agents/main/data/user-agents.json): Plain list of User-Agent strings
- [`data/user-agents-metadata.json`](https://raw.githubusercontent.com/hgtgh/user-agents/main/data/user-agents-metadata.json): Detailed records with browser, version, source, and timestamp metadata

### From a checkout

Run the tool directly (no `PYTHONPATH` setup needed):

```bash
make test       # run the test-suite
make update     # regenerate the dataset into data/
make fixtures   # refresh the test fixtures from the live endpoints

# or call the scripts directly
python3 scripts/update_user_agents.py --output-dir data
python3 scripts/refresh_test_fixtures.py
```

### Install / console scripts

The project is pip-installable and ships two console commands:

```bash
pip install ".[dev]"        # or: make install

user-agents-update --output-dir data
user-agents-refresh-fixtures --output-dir tests/fixtures --keep-stale
```

- `user-agents-update` renders the dataset. `--output-dir` controls where
  `user-agents.json` and `user-agents-metadata.json` are written (defaults to
  the repo `data/` dir in a checkout, `./data` elsewhere).
- `user-agents-refresh-fixtures` re-downloads the HTML/JSON fixtures used by
  the test-suite. Pass `--keep-stale` to retain fixture files that are no
  longer produced by any provider.

`make lint` runs [ruff](https://docs.astral.sh/ruff/) over `src`, `tests`, and `scripts`.

## Development

```bash
make test       # unittest discovery (no third-party deps required)
python3 -m pytest  # same suite under pytest, if installed
ruff check src tests scripts
```

Dependencies are zero for the default install; `pytest` and `ruff` live in the
`dev` extra.

## License

Licensed under MIT. See [LICENSE](LICENSE).