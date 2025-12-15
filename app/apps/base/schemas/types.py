from typing import Annotated

from pydantic import StringConstraints

SearchField = Annotated[
    str,
    StringConstraints(
        min_length=3,
    ),
]