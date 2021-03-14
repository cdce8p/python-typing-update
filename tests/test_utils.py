import io

import pytest

from python_typing_update.const import FileStatus
from python_typing_update.utils import check_comment_between_imports


@pytest.mark.parametrize(
    ('code', 'return_value'),
    (
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
# This is a comment
import sys
from typing import (
    Any, List,
    Union
)

var: Any = sys.version
""",
            FileStatus.COMMENT,
            id="comment_before_imports",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
# This is a comment
from typing import (
    Any, List,
    Union
)

var: Any = sys.version
""",
            FileStatus.COMMENT,
            id="comment_between_imports_1",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
\"\"\"Long comment (2)\"\"\"
from typing import (
    Any, List,
    Union
)

var: Any = sys.version
""",
            FileStatus.COMMENT,
            id="comment_between_imports_2",
        ),
    )
)
def test_comment_detection(code: str, return_value: FileStatus):
    fp = io.StringIO(code)
    assert check_comment_between_imports(fp) == return_value


@pytest.mark.parametrize(
    ('code', 'return_value'),
    (
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys  # comment

var: Any = sys.version
""",
            FileStatus.CLEAR,
            id="comment_inline_import_clear",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
from sys import version  # comment

var: Any = sys.version
""",
            FileStatus.CLEAR,
            id="comment_inline_from_clear",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
from sys import version, version_info  # comment

var: Any = sys.version
""",
            FileStatus.COMMENT,
            id="comment_inline_from_2",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
from sys import argv, version, version_info  # comment

var: Any = sys.version
""",
            FileStatus.COMMENT,
            id="comment_inline_from_3",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
from sys import (  # comment
    argv, version,
    version_info,
)

var: Any = sys.version
""",
            FileStatus.COMMENT,
            id="comment_inline_from_4",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
from sys import (
    argv, version,
    version_info  # comment
)

var: Any = sys.version
""",
            FileStatus.COMMENT,
            id="comment_inline_from_5",
        ),
    )
)
def test_comment_detection_comment_inline(code: str, return_value: FileStatus):
    fp = io.StringIO(code)
    assert check_comment_between_imports(fp) == return_value


@pytest.mark.parametrize(
    ('code', 'return_value'),
    (
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
import typing  # comment

var: Any = sys.version
""",
            FileStatus.COMMENT | FileStatus.COMMENT_TYPING,
            id="comment_typing_import",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
from typing import Any  # comment

var: Any = sys.version
""",
            FileStatus.COMMENT | FileStatus.COMMENT_TYPING,
            id="comment_typing_from_1",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
from typing import Any, List  # comment

var: Any = sys.version
""",
            FileStatus.COMMENT | FileStatus.COMMENT_TYPING,
            id="comment_typing_from_2",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
from typing import Any, List, Union  # comment

var: Any = sys.version
""",
            FileStatus.COMMENT | FileStatus.COMMENT_TYPING,
            id="comment_inline_3",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
from typing import (  # comment
    Any, List,
    Union
)

var: Any = sys.version
""",
            FileStatus.COMMENT | FileStatus.COMMENT_TYPING,
            id="comment_typing_from_4",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
from typing import (
    Any, List,
    Union  # comment
)

var: Any = sys.version
""",
            FileStatus.COMMENT | FileStatus.COMMENT_TYPING,
            id="comment_typing_from_5",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
from sys import argv, version # comment
from typing import Any  # comment

var: Any = sys.version
""",
            FileStatus.COMMENT | FileStatus.COMMENT_TYPING,
            id="comment_typing_multiple",
        ),
    )
)
def test_comment_detection_comment_typing(code: str, return_value: FileStatus):
    fp = io.StringIO(code)
    assert check_comment_between_imports(fp) == return_value


@pytest.mark.parametrize(
    ('code', 'return_value'),
    (
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
from typing import (
    Any, List,
    Union
)
# This is a comment

var: Any = sys.version
""",
            FileStatus.CLEAR,
            id="comment_after_imports",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys

# This is a comment
var: Any = sys.version

from typing import Any
""",
            FileStatus.CLEAR,
            id="comment_after_first_import_block",
        ),
    )
)
def test_comment_detection_ignore_comment(code: str, return_value: FileStatus):
    fp = io.StringIO(code)
    assert check_comment_between_imports(fp) == return_value
