from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiofiles
import pytest
from _pytest.capture import CaptureFixture

from python_typing_update.__main__ import async_main
from python_typing_update.utils import async_restore_files

FIXTURE_PATH = "tests/fixtures/"


async def async_check_changes(filename: str, control: str):
    async with aiofiles.open(filename, 'r') as fp:
        content_modified: str = await fp.read()

    async with aiofiles.open(control, 'r') as fp:
        content_control: str = await fp.read()

    assert content_modified == content_control


@asynccontextmanager
async def async_restore_fixtures(file_list: list[str]) -> AsyncGenerator[None, None]:
    try:
        yield
    finally:
        await async_restore_files(file_list)


async def async_test_main(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
):
    filename = FIXTURE_PATH + filename
    control = FIXTURE_PATH + control
    if argv is None:
        argv = ["--disable-committed-check"]
    else:
        argv.append("--disable-committed-check")
    argv.append(filename)
    async with async_restore_fixtures([filename]):
        assert returncode == await async_main(argv)
        await async_check_changes(filename, control)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('filename', 'control', 'argv', 'returncode'),
    (
        pytest.param(
            'changed.py', 'changed_fixed.py',
            None, 0,
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
            'changed.py', 'changed_fixed.py',
            ['--full-reorder', '--py38-plus'], 0,
            id="full_reorder_38",
        ),
        pytest.param(
            'changed.py', 'changed_full_reorder.py',
            ['--full-reorder', '--py39-plus'], 0,
            id="full_reorder_39",
        ),
        pytest.param(
            'changed.py', 'changed_fixed.py',
            ['-v'], 12,
            id="debug",
        ),
    )
)
async def test_main(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
):
    await async_test_main(filename, control, argv, returncode)


@pytest.mark.asyncio
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
    )
)
async def test_main_type_alias(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
):
    await async_test_main(filename, control, argv, returncode)


@pytest.mark.asyncio
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
    )
)
async def test_main_comment(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
    capsys: CaptureFixture,
):
    await async_test_main(filename, control, argv, returncode)
    assert filename in capsys.readouterr().out


@pytest.mark.asyncio
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
    )
)
async def test_main_comment_no_issue(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
):
    await async_test_main(filename, control, argv, returncode)


@pytest.mark.asyncio
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
    )
)
async def test_main_comment_import_no_issue(
    filename: str,
    control: str,
    argv: list[str] | None,
    returncode: int,
):
    await async_test_main(filename, control, argv, returncode)
