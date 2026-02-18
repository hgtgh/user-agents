# hgtgh/user-agents
# User Agents Generator

Generate realistic, up-to-date User-Agent strings from official browser release feeds.

Ship ready-to-use JSON datasets for testing, scraping, and browser simulation workflows.

## Why this project?

Hardcoded User-Agent datasets become stale quickly and lead to unrealistic fingerprints.

This project keeps them current by:

- Fetches stable versions from official browser release feeds
- Renders consistent User-Agent variants
- Generates both plain and metadata-rich JSON outputs
- Refreshes the dataset daily via GitHub Actions

## Supported Browsers and OS

Currently generated variants:

- **Chrome**: Windows, macOS, Linux
- **Firefox**: Windows, macOS, Linux, Ubuntu
- **Microsoft Edge**: Windows
- **Safari**: macOS

## Usage

Outputs:

- `data/user-agents.json`: Plain list of User-Agent strings
- `data/user-agents-metadata.json`: Detailed records with browser, version, source, and timestamp metadata

Common commands:

```bash
make test       # Run test
make update     # Regenerate dataset
make fixtures   # Refresh test fixtures
```

## License

Licensed under MIT. See [LICENSE](LICENSE).
