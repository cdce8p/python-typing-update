import io

import pytest

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
            True,
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
            True,
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
            True,
            id="comment_between_imports_2",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys  # comment
from typing import (
    Any, List,
    Union
)

var: Any = sys.version
""",
            True,
            id="comment_inline_1",
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
            True,
            id="comment_inline_2",
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
            True,
            id="comment_inline_3",
        ),
        pytest.param(
            """ \
\"\"\"Long comment\"\"\"
import sys
from typing import Any, List, Union  # comment

var: Any = sys.version
""",
            True,
            id="comment_inline_4",
        ),
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
            False,
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
            False,
            id="comment_after_first_import_block",
        ),
    )
)
def test_comment_detection(code: str, return_value: bool):
    fp = io.StringIO(code)
    assert check_comment_between_imports(fp) == return_value
