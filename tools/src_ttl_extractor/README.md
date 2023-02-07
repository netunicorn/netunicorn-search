# Packets TTL Extractor

As TTL values in the same flow should always be the same for all incoming packets, this tool extracts TTL values from flows and combines them with Flow ID, created by CICFlowExtractor,
to produce a ttl-per-flow csv database.  

This is a specific tool for netunicorn-search project and should be used together with the project.  

Compilation instructions:
1. Install Rust
2. `cargo build -r`
