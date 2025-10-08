# Contributing to `motile`

:tada: Thank you for your interest in contributing to `motile`! :tada:

`motile` is a research library. While it is stable and in use in multiple projects, the time
available for the core developers to perform maintenance and feature requests is limited.
The preferred form of communication for bugs and requests is GitHub 
[Issues](https://github.com/funkelab/motile/issues/new) - if your issue does not get a 
response in a reasonable time, feel free to ping @cmalinmayor and I will take at least a quick look.

## New Costs and Constraints
To keep this library manageable to maintain, we intentionally keep the number of `Variables`,
`Costs`, and `Constraints` implemented here low, and highly encourage people with specific
needs to extend the base classes to implement their own components within the `motile`
framework.

Examples of complex workflows can be found in experimental libraries that use `motile`, such as:
- [`attrackt`](https://github.com/funkelab/attrackt)
- [`mhat` (Multi Hypothesis Affinity Tracking)](https://github.com/funkelab/mhat)

If you want to contribute a `Cost` or `Constraint` that is widely useful and should be part of
the core library, please open an [Issue](https://github.com/funkelab/motile/issues/new) or PR and we will review it. If we can't
commit to maintaining the code but think others can use it as inspiration, we might suggest
contributing it to the [`motile_toolbox`](https://github.com/funkelab/motile_toolbox) instead.

## Development Tools

We use `uv` for dependency management, `ruff` for formatting and linting, and `mypy` for type checking.
If set up correctly, the `pre-commit` configuration runs `ruff` and `mypy` before each commit.
To set it up, navigate to the root directory of this repository and run:
```bash
uv run pre-commit install
```

To run the tests from the root directory:
```bash
uv run pytest
```


