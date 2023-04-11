# Pre-commit binary

Pre-commit hook for downloading and running pre-built binaries with pre-commit.

This is a bit of an experiment, and I expect the hook config arguments to change a bit before stabilizing.

## Motivation

It takes me over 3 minutes to pull and compile Rust hooks ([example](https://github.com/sondrelg/printf-log-formatter)) from scratch. 
It seems better to not have every client perform this work. 
Instead, we can just download the pre-built binaries directly.

## General structure

- Identify client platform + arch
- Load binary URL from hook arguments, using platform + arch 
- Create URL checksum and construct cache path, and see if the binary exists
- If there is no cache for it, download the binary
- Run the binary, making sure to proxy in arguments

Clients can then run binaries directly by configuring their hooks like this, in their `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/sondrelg/pre-commit-binary
  rev: ""
  hooks:
    - id: pre-commit-binary
      alias: <name of the you're running>
      args:
        # Specify binary URLs for each platform/arch combination 
        # needed by the devs using your project
        - |
        --urls={
          "darwin-x86_64":  "<url>/darwin-x64_86.tar.gz",
          "darwin-arm64":  "<url>/darwin-arm64.tar.gz",
          "linux-x64_64":  "<url>/linux-x64_86.zip"
        }
        # Remaining arguments passed on to the binary
        - --log-level=error
        - --quotes=single
```
