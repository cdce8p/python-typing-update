# Python typing update

Small tool to update Python typing syntax.
It uses token analysis and
- [python-reorder-imports][pri]
- [pyupgrade][pyu]
- [isort][isort]
- [autoflake][autoflake]
- [black][black]
- git

to try and update the typing syntax the best it can.

**Important**  
Since every project uses a different formatting style,
always check `git diff` before committing any changes!  
Since this tool uses [pyupgrade][pyu], it's best used for
projects that use it already.


## Limitations
Due to the way the tool works, it will reorder the imports multiple times.
By default the tool tries to detect if a comment was moved
and revert all changes to the file. This can be overwritten by using `--force`.


## How it works
1. Run [python-reorder-import][pri] to add
   `from __future__ import annotations` to each file.
2. Run [pyupgrade][pyu] to use generic aliases ([PEP 585][PEP585])
   and alternative union syntax ([PEP 604][PEP604]) where possible.
3. Run [autoflake][autoflake] to check if any typing import is now
   unused. If not, revert changes with `git restore`.
4. Remove unused imports with [autoflake][autoflake].
5. Run [isort][isort] to try to restore the previous formatting.
6. Optional: Run [black][black]
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
- `--py39-plus`: Rewrite [PEP 585][PEP585] typing imports. Additionally `typing.Hashable` and `typing.Sized` will also be replace by their `collections.abc` equivalents.

**`--black`**  
Run `black` formatting after updates.

**`--check`**  
Check if files would be modified. Return with exitcode `1` or `0` if not. Useful for CI runs.

**`--force`**  
Don't revert changes if a modified comment is detected.
Check `git diff` before committing!

**`--only-force`**  
Only update files which are likely to require extra work.
Check `git diff` before committing!

**`--py39-plus`**  
Set the minimum Python syntax to **3.9**. (Default: **3.8**)

**`--py310-plus`**  
Set the minimum Python syntax to **3.10**. (Default: **3.10**)


## License
This Project is licensed under the MIT license.
See [LICENSE](LICENSE) for the full license text.


[pri]: https://github.com/asottile/reorder_python_imports
[pyu]: https://github.com/asottile/pyupgrade
[isort]: https://github.com/PyCQA/isort
[autoflake]: https://github.com/myint/autoflake
[black]: https://github.com/psf/black
[PEP585]: https://www.python.org/dev/peps/pep-0585/
[PEP604]: https://www.python.org/dev/peps/pep-0604/
