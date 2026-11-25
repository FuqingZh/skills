---
name: writing-code-docs
description: Use for writing, revising, or auditing docstrings and language-native documentation comments. Also use at public APIs and durable workflow or product boundaries when code documentation must explain usage, contracts, maintenance rationale, or compatibility-sensitive behavior.
---

# Writing Code Docs

For repository work, trace in-scope symbols through relevant code, call sites,
tests, schemas, or outputs until their contracts are clear to their readers.

For a standalone code snippet, work only from the supplied implementation and
requirements without searching an unrelated workspace. State material gaps
rather than inventing behavior.

A contract is clear to callers when they know what they may rely on, and to
maintainers when they know what they must preserve.

## Convention

Follow the repository's language-native documentation convention. Without one
(or for standalone snippets without a supplied format), use the official
language fallback:

- For Python, follow the
  [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings),
  using [doctest-style](https://docs.python.org/3/library/doctest.html)
  `Examples:` for caller-facing examples and `Notes:` for maintenance
  boundaries.
- For other languages without a local convention, use the official
  documentation convention when one is available. Do not transfer Python
  sections by analogy.

## Readers

Classify in-scope symbols as caller-facing, maintainer-facing, both, or
neither. Do not document symbols with no reader.

In prose, do not restate what names, signatures, types, schemas, or nearby code
already show.

For callers, show what they may rely on. Add short, locatable examples when
usage, parameter interactions, boundary results, exceptions, or side effects
are not obvious from the signature and brief summary, or when repository rules
explicitly require examples (such as executed doctests or per-symbol rules).
Simple properties, aliases, and symbols sharing a contract may point to a
shared example on their owning type or API, covering only distinct behavior the
shared example omits. Show each distinct public consequence once without
ceremonial or unverified examples.

For maintainers, name the protected boundary, why it exists, and the tempting
change that would break it.

When both apply, serve each reader without duplication.

## Boundaries

Keep domain terms unchanged unless the repository defines their translation.

Treat bad names, unclear boundaries, and mechanical wrappers as code problems,
not documentation problems; fix them when in scope and report them otherwise.

Do not substitute documentation for tests, validation, user guides, or
architecture records.
