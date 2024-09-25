from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from _pytest.capture import CaptureFixture
import aiofiles
import pytest

from python_typing_update.__main__ import async_main
from python_typing_update.utils import async_restore_files

FIXTURE_PATH = "tests/fixtures/"


async def async_check_changes(filename: str, control: str) -> None:
    async with aiofiles.open(filename, 'r') as fp:
        content_modified: str = await fp.read()

    async with aiofiles.open(control, 'r') as fp:
        content_control: str = await fp.read()

    assert content_modified == content_control


@asynccontextmanager
async def async_restore_fixtures(file_list: list[str]) -> AsyncGenerator[None]:
    try:
        yield
    finally:
        await async_restore_files(file_list)


async def async_test_main(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
    capsys: CaptureFixture | None = None,
) -> None:
    filename = FIXTURE_PATH + filename
    control = FIXTURE_PATH + control
    if argv is None:
        argv = ["--disable-committed-check"]
    else:
        argv.append("--disable-committed-check")
    argv.append(filename)
    async with async_restore_fixtures([filename]):
        ret = await async_main(argv)
        assert returncode == ret
        await async_check_changes(filename, control)
    if ret in (1, 2) and capsys:
        assert filename in capsys.readouterr().out


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'changed.py', 'changed_fixed.py',
            ['--py38-plus'], 0,
            id="typing_updated",
        ),
        pytest.param(
            'empty_line.py', 'empty_line_fixed.py',
            None, 0,
            id="typing_updated_empty_line",
        ),
        pytest.param(
            'no_changes.py', 'no_changes_no_change.py',
            None, 0,
            id="no_changes",
        ),
        pytest.param(
            'changed.py', 'changed_no_change.py',
            ['--check'], 1,
            id="check_changes",
        ),
        pytest.param(
            'no_changes.py', 'no_changes_no_change.py',
            ['--check'], 0,
            id="check_no_changes",
        ),
        pytest.param(
            'changed.py', 'changed_full_reorder_38.py',
            ['--full-reorder', '--py38-plus'], 0,
            id="full_reorder_38",
        ),
        pytest.param(
            'changed.py', 'changed_full_reorder_39.py',
            ['--full-reorder', '--py39-plus'], 0,
            id="full_reorder_39",
        ),
        pytest.param(
            'changed.py', 'changed_fixed.py',
            ['-v', '--py38-plus'], 12,
            id="debug",
        ),
    ),
)
async def test_main(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
    capsys: CaptureFixture,
) -> None:
    await async_test_main(filename, control, argv, returncode, capsys)


@pytest.mark.parametrize(
    ('argv',),
    (
        pytest.param(['--py37-plus']),
        pytest.param(['--py38-plus']),
        pytest.param(['--py39-plus']),
        pytest.param(['--py310-plus']),
        pytest.param(['--py311-plus']),
        pytest.param(['--py312-plus']),
        pytest.param(['--py313-plus']),
    ),
)
async def test_py_version(
    argv: list[str] | None,
    capsys: CaptureFixture,
) -> None:
    await async_test_main(
        filename='no_changes.py',
        control='no_changes_no_change.py',
        argv=argv,
        returncode=0,
        capsys=capsys,
    )


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'type_alias_39.py', 'type_alias_39_no_change.py',
            ['--py38-plus'], 0,
            id="type_alias_pep585_38_no_change",
        ),
        pytest.param(
            'type_alias_39.py', 'type_alias_39_fixed.py',
            ['--py39-plus'], 0,
            id="type_alias_pep585_39_updated",
        ),
        pytest.param(
            'type_alias_310.py', 'type_alias_310_no_change.py',
            ['--py38-plus'], 0,
            id="type_alias_pep604_38_no_change",
        ),
        pytest.param(
            'type_alias_310.py', 'type_alias_310_fixed.py',
            ['--py310-plus'], 0,
            id="type_alias_pep604_310_updated",
            marks=pytest.mark.xfail(reason="Not implented in mypy + pyupgrade (yet)"),
        ),
    ),
)
async def test_main_type_alias(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
) -> None:
    await async_test_main(filename, control, argv, returncode)


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'comment_1.py', 'comment_1_no_change.py',
            None, 2,
            id="comment_1_no_change",
        ),
        pytest.param(
            'comment_2.py', 'comment_2_no_change.py',
            None, 2,
            id="comment_2_no_change",
        ),
        pytest.param(
            'comment_3.py', 'comment_3_no_change.py',
            None, 2,
            id="comment_3_no_change",
        ),
        pytest.param(
            'comment_4.py', 'comment_4_no_change.py',
            None, 2,
            id="comment_4_no_change",
        ),
        pytest.param(
            'comment_5.py', 'comment_5_no_change.py',
            None, 2,
            id="comment_5_no_change",
        ),
        pytest.param(
            'comment_1.py', 'comment_1_forced.py',
            ['--force'], 2,
            id="comment_1_forced",
        ),
        pytest.param(
            'comment_2.py', 'comment_2_forced.py',
            ['--force'], 2,
            id="comment_2_forced",
        ),
        pytest.param(
            'comment_3.py', 'comment_3_forced.py',
            ['--force'], 2,
            id="comment_3_forced",
        ),
        pytest.param(
            'comment_4.py', 'comment_4_forced.py',
            ['--force'], 2,
            id="comment_4_forced",
        ),
        pytest.param(
            'comment_5.py', 'comment_5_forced.py',
            ['--force'], 2,
            id="comment_5_forced",
        ),
    ),
)
async def test_main_comment(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
    capsys: CaptureFixture,
) -> None:
    await async_test_main(filename, control, argv, returncode, capsys)


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'comment_no_issue_1.py', 'comment_no_issue_1_fixed.py',
            None, 0,
            id="comment_no_issue_1",
        ),
        pytest.param(
            'comment_no_issue_2.py', 'comment_no_issue_2_fixed.py',
            None, 0,
            id="comment_no_issue_2",
        ),
        pytest.param(
            'comment_no_issue_3.py', 'comment_no_issue_3_fixed.py',
            None, 0,
            id="comment_no_issue_3",
        ),
        pytest.param(
            'comment_no_issue_4.py', 'comment_no_issue_4_fixed.py',
            None, 0,
            id="comment_no_issue_4",
        ),
        pytest.param(
            'comment_no_issue_5.py', 'comment_no_issue_5_fixed.py',
            None, 0,
            id="comment_no_issue_5",
        ),
        pytest.param(
            'comment_no_issue_6.py', 'comment_no_issue_6_fixed.py',
            None, 0,
            id="comment_no_issue_6",
        ),
    ),
)
async def test_main_comment_no_issue(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
) -> None:
    await async_test_main(filename, control, argv, returncode)


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'comment_import_no_issue_1.py', 'comment_import_no_issue_1_fixed.py',
            None, 0,
            id="comment_import_no_issue_1",
        ),
        pytest.param(
            'comment_import_no_issue_2.py', 'comment_import_no_issue_2_fixed.py',
            None, 0,
            id="comment_import_no_issue_2",
        ),
        pytest.param(
            'comment_import_no_issue_3.py', 'comment_import_no_issue_3_fixed.py',
            None, 0,
            id="comment_import_no_issue_3",
        ),
        pytest.param(
            'comment_import_no_issue_4.py', 'comment_import_no_issue_4_fixed.py',
            None, 0,
            id="comment_import_no_issue_4",
        ),
    ),
)
async def test_main_comment_import_no_issue(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
) -> None:
    await async_test_main(filename, control, argv, returncode)


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'unused_import_1.py', 'unused_import_1_fixed.py',
            None, 0,
            id="unused_import_1_fixed",
        ),
        pytest.param(
            'unused_import_2.py', 'unused_import_2_fixed.py',
            None, 0,
            id="unused_import_2_fixed",
        ),
        pytest.param(
            'unused_import_3.py', 'unused_import_3_fixed.py',
            None, 0,
            id="unused_import_3_fixed",
        ),
        pytest.param(
            'unused_import_4.py', 'unused_import_4_fixed.py',
            None, 0,
            id="unused_import_4_fixed",
        ),
        pytest.param(
            'unused_import_5.py', 'unused_import_5_no_change.py',
            None, 2,
            id="unused_import_5_no_change",
        ),
        pytest.param(
            'unused_import_6.py', 'unused_import_6_no_change.py',
            None, 2,
            id="unused_import_6_no_change",
        ),
        pytest.param(
            'unused_import_7.py', 'unused_import_7_no_change.py',
            None, 2,
            id="unused_import_7_no_change",
        ),
        pytest.param(
            'unused_import_8.py', 'unused_import_8_no_change.py',
            None, 2,
            id="unused_import_8_no_change",
        ),
        pytest.param(
            'unused_import_5.py', 'unused_import_5_forced.py',
            ['--force'], 2,
            id="unused_import_5_forced",
        ),
        pytest.param(
            'unused_import_6.py', 'unused_import_6_forced.py',
            ['--force'], 2,
            id="unused_import_6_forced",
        ),
        pytest.param(
            'unused_import_7.py', 'unused_import_7_forced.py',
            ['--force'], 2,
            id="unused_import_7_forced",
        ),
        pytest.param(
            'unused_import_8.py', 'unused_import_8_forced.py',
            ['--force'], 2,
            id="unused_import_8_forced",
        ),
    ),
)
async def test_main_unused_import(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
    capsys: CaptureFixture,
) -> None:
    await async_test_main(filename, control, argv, returncode, capsys)


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'unused_import_comment_1.py', 'unused_import_comment_1_fixed.py',
            None, 0,
            id="unused_import_comment_1_fixed",
        ),
        pytest.param(
            'unused_import_comment_2.py', 'unused_import_comment_2_fixed.py',
            None, 0,
            id="unused_import_comment_2_fixed",
        ),
        pytest.param(
            'unused_import_comment_5.py', 'unused_import_comment_5_fixed.py',
            None, 0,
            id="unused_import_comment_5_fixed",
        ),
        pytest.param(
            'unused_import_comment_6.py', 'unused_import_comment_6_fixed.py',
            None, 0,
            id="unused_import_comment_6_fixed",
        ),
        pytest.param(
            'unused_import_comment_3.py', 'unused_import_comment_3_no_change.py',
            None, 2,
            id="unused_import_comment_3_no_change",
        ),
        pytest.param(
            'unused_import_comment_4.py', 'unused_import_comment_4_no_change.py',
            None, 2,
            id="unused_import_comment_4_no_change",
        ),
        pytest.param(
            'unused_import_comment_7.py', 'unused_import_comment_7_no_change.py',
            None, 2,
            id="unused_import_comment_7_no_change",
        ),
        pytest.param(
            'unused_import_comment_8.py', 'unused_import_comment_8_no_change.py',
            None, 2,
            id="unused_import_comment_8_no_change",
        ),
        pytest.param(
            'unused_import_comment_3.py', 'unused_import_comment_3_forced.py',
            ['--force'], 2,
            id="unused_import_comment_3_forced",
        ),
        pytest.param(
            'unused_import_comment_4.py', 'unused_import_comment_4_forced.py',
            ['--force'], 2,
            id="unused_import_comment_4_forced",
        ),
        pytest.param(
            'unused_import_comment_7.py', 'unused_import_comment_7_forced.py',
            ['--force'], 2,
            id="unused_import_comment_7_forced",
        ),
        pytest.param(
            'unused_import_comment_8.py', 'unused_import_comment_8_forced.py',
            ['--force'], 2,
            id="unused_import_comment_8_forced",
        ),
    ),
)
async def test_main_unused_import_comment(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
    capsys: CaptureFixture,
) -> None:
    await async_test_main(filename, control, argv, returncode, capsys)


@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'keep_updates.py', 'keep_updates_no_change.py',
            ['--py38-plus'], 0,
            id="no_import_removed",
        ),
        pytest.param(
            'keep_updates.py', 'keep_updates_fixed.py',
            ['--keep-updates', '--py38-plus'], 0,
            id="keep_updates",
        ),
    ),
)
async def test_main_keep_updates(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
) -> None:
    await async_test_main(filename, control, argv, returncode)
