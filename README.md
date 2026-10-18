## Usage

```bash
uvx pystrfreq
```

The tool will walk through the current directory, parse all `.py` file and then tabluate the frequency of string in the parsed files.

## Options

To check all usage options:

```bash
uvx pystrfreq -h
```

## Known Caveats

- Requires Python 3.10 to 3.15. Files are parsed with the running interpreter's grammar, so files using newer syntax (e.g. t-strings, 3.14+) are skipped when run on an older Python.
- `FormmatedValue` in `f-string` are not supported, while the `f-string` will be broken into its constant parts and tabulated.

## License

This project is licensed under the MIT License.
