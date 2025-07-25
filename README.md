# Python typing update

[![PyPI](https://img.shields.io/pypi/v/python-typing-update?color=blue)](https://pypi.org/project/python-typing-update/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-typing-update)](https://github.com/cdce8p/python-typing-update)
[![GitHub](https://img.shields.io/github/license/cdce8p/python-typing-update)](https://github.com/cdce8p/python-typing-update/blob/main/LICENSE)
[![image](https://static.pepy.tech/badge/python-typing-update)](https://pepy.tech/project/python-typing-update)

Tool to update Python typing syntax.
It uses token analysis and
- [python-reorder-imports][pri]
- [pyupgrade][pyu]
- [isort][isort]
- [autoflake][autoflake]
- [black][black]
- [ruff][ruff]
- git

to try and update the typing syntax the best it can.

**Important**  
Every project uses a different formatting style,
so always check `git diff` before comitting any changes!
Since this tool uses [pyupgrade][pyu], it's best used for
projects that use it already.


## Limitations
Due to the way the tool works, it will reorder the imports multiple times.
By default the tool tries to detect if a comment was moved
and revert all changes to the file. This can be overwritten by using `--force`.

Currently, it's not possible to update aliases with a different name.
In particular, these need to be updated manually:
| Old typing name | New |
| --------------- | --- |
| `Deque` | `collections.deque` |
| `DefaultDict` | `collections.defaultdict` |
| `AbstractSet` | `collections.abc.Set` |
| `ContextManager` | `contextlib.AbstractContextManager` |
| `AsyncContextMananger` | `contextlib.AbstractAsyncContextManager` |


## How it works
1. Run [python-reorder-import][pri] to add
   `from __future__ import annotations` to each file.
2. Run [pyupgrade][pyu] to use generic aliases ([PEP 585][PEP585])
   and alternative union syntax ([PEP 604][PEP604]) where possible.
3. Run [autoflake][autoflake] to check if any typing import is now
   unused. If not, revert changes with `git restore`.
4. Remove unused imports with [autoflake][autoflake].
5. Run [isort][isort] to try to restore the previous formatting.
6. Optional: Run [black][black]. (Requires `black` to be added as `additional_dependency`)  
   OR: Run [ruff][ruff]. (Requires `ruff` to be added as `additional_dependency`)
7. Check `git diff` for modified comments.
   If one is detected, revert changes and print file name.
   Can be overwritten with `--force`.


## Setup pre-commit

Add this to the `.pre-commit-config.yaml` file

```yaml
repos:
  - repo: https://github.com/cdce8p/python-typing-update
    rev: <insert current tag here!>
    hooks:
      - id: python-typing-update
        stages: [manual]
```

Run with
```bash
pre-commit run --hook-stage manual python-typing-update --all-files
```

## Configuration

**`--verbose`**  
Always print verbose logging.

**`--limit`**  
Max number of files that should be changed. No performance improvements,
since the limit is only applied **after** all files have been processed.

**`--concurrent-files`**  
Number of files to process concurrently during initial load.

**`--full-reorder`**  
Use additional options from [python-reorder-imports][pri] to rewrite
- `--py38-plus` (default): Imports from `mypy_extensions` and `typing_extensions` when possible.
- `--py39-plus`: Rewrite [PEP 585][PEP585] typing imports. Additionally `typing.Hashable` and `typing.Sized` will also be replaced by their `collections.abc` equivalents.

**`--keep-updates`**  
Keep updates even if no import was removed. Use with caution, might result in more errors.

**`--black`**  
Run `black` formatting after updates.  
To use it, add `black` as `additional_dependency` in your `.pre-commit-config.yaml`.

```yaml
        additional_dependencies:
          - black==<insert current version here!>
```

**`--ruff`**  
Run `ruff check --fix` and `ruff format` after updates.  
To use it, add `ruff` as `additional_dependency` in your `.pre-commit-config.yaml`.

```yaml
        additional_dependencies:
          - ruff==<insert current version here!>
```

**`--disable-committed-check`**  
Don't abort with uncommitted changes. **Don't use it in production!**
Risk of losing uncommitted changes.


### Different mode options

**`--check`**  
Check if files would be modified. Return with exitcode `1` or `0` if not. Useful for CI runs.

**`--force`**  
Don't revert changes if a modified comment is detected.
Check `git diff` before committing!

**`--only-force`**  
Only update files which are likely to require extra work.
Check `git diff` before committing!


### Python version options

**`--py37-plus`**
Set the minimum Python syntax version to **3.7**. (Default: **3.9**)

**`--py38-plus`**  
Set the minimum Python syntax version to **3.8**. (Default: **3.9**)

**`--py39-plus`**  
Set the minimum Python syntax version to **3.9**. This is the default.

**`--py310-plus`**  
Set the minimum Python syntax version to **3.10**. (Default: **3.9**)

**`--py311-plus`**  
Set the minimum Python syntax version to **3.11**. (Default: **3.9**)

**`--py312-plus`**  
Set the minimum Python syntax version to **3.12**. (Default: **3.9**)

**`--py313-plus`**
Set the minimum Python syntax version to **3.13**. (Default: **3.9**)

**`--py314-plus`**
Set the minimum Python syntax version to **3.14**. (Default: **3.9**)


## License
This Project is licensed under the MIT license.
See [LICENSE][LICENSE_FILE] for the full license text.


[pri]: https://github.com/asottile/reorder_python_imports
[pyu]: https://github.com/asottile/pyupgrade
[isort]: https://github.com/PyCQA/isort
[autoflake]: https://github.com/PyCQA/autoflake
[black]: https://github.com/psf/black
[ruff]: https://github.com/astral-sh/ruff
[PEP585]: https://www.python.org/dev/peps/pep-0585/
[PEP604]: https://www.python.org/dev/peps/pep-0604/

[LICENSE_FILE]: https://github.com/cdce8p/python-typing-update/blob/main/LICENSE
