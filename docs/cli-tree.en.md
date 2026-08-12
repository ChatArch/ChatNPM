# CLI Tree

`chatnpm --tree` is generated from the real Click command registry so local gates, CI, and release readback lock the public interface.

```text
chatnpm  # ChatArch npm registry and publishing-evidence helper.
├── --help  # Show this help message.
├── --version  # Show the installed package version.
├── --tree  # Print the registered command tree.
├── package  # Inspect npm package registry metadata.
│   └── inspect PACKAGE [--version PACKAGE-VERSION] [--registry REGISTRY] [--format text|json]  # Read npm registry publisher/provenance metadata for PACKAGE.
└── trusted  # Audit npm Trusted Publishing evidence.
    └── audit [PATH] [--format text|json]  # Read local package/workflow evidence for npm Trusted Publishing.
```

## Acceptance commands

```bash
chatnpm --version
chatnpm --tree
chatnpm package inspect npm --format json
chatnpm trusted audit . --format json
```
