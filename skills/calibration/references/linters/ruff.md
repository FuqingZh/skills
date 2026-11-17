# Ruff

When Ruff is appropriate for the repository, follow its existing rule selection.
If no repository-local selection exists, start with `E`, `F`, `I`, `UP`, `B`,
`SIM`, and `RUF`. Additional rule families, `ALL`, and preview rules are
repository-specific choices, not defaults.

This is calibration's fallback selection, not Ruff's built-in default. Consult
[Ruff's rule-selection documentation](https://docs.astral.sh/ruff/linter/#rule-selection)
for configuration behavior and
[the rules reference](https://docs.astral.sh/ruff/rules/) for individual rules.
