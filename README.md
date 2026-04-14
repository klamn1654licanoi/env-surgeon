# env-surgeon

> A CLI tool to audit, merge, and diff `.env` files across multiple environments without leaking secrets.

---

## Installation

```bash
pip install env-surgeon
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install env-surgeon
```

---

## Usage

### Audit a `.env` file for missing or undefined keys

```bash
env-surgeon audit .env --reference .env.example
```

### Diff two environment files

```bash
env-surgeon diff .env.staging .env.production
```

### Merge multiple `.env` files (later files take precedence)

```bash
env-surgeon merge .env.base .env.local --output .env
```

> **Note:** By default, `env-surgeon` masks secret values in all output. Use `--reveal` only in trusted environments.

### Full options

```bash
env-surgeon --help
```

---

## Example Output

```
[audit] .env vs .env.example
  ✔  DB_HOST        defined
  ✔  DB_PORT        defined
  ✗  STRIPE_KEY     missing
  ⚠  DEBUG          extra (not in reference)
```

---

## License

[MIT](LICENSE) © 2024 env-surgeon contributors