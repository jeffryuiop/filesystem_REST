import pydantic
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class OrderByOptions(str, Enum):
    lastModified = "lastModified"
    fileSize = "size"
    fileName = "fileName"

class DirOptions(str, Enum):
    ascending = "ascending"
    descending = "descending"

class InputQuery(BaseModel):
    orderBy: Optional[OrderByOptions] = Field(default=None, example=OrderByOptions.fileName,
        description="[OPTIONAL] Set how to order the search result(s)")
    orderByDirection: Optional[DirOptions] = Field(default=DirOptions.ascending, example=DirOptions.ascending,
        description="[OPTIONAL] Set the result(s) to be in ascending/descending order")
    filterByName: Optional[str] = Field(default=None, example="name",
        description="[OPTIONAL] Will only return result(s) that have this string (not case-sensitive)")