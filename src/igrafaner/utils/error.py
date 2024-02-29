from pydantic import BaseModel
from typing import Union

class ErrorCompo(BaseModel):
    comp_id: Union[str, int]
    err_type: str
    message: str


class CModelNotFound(Exception):
    def __init__(self, message="cModel not found.") -> None:
        self.message = message
        super().__init__(self.message)


class PartNumberNotFound(Exception):
    def __init__(self, message="Part number not found") -> None:
        self.message = message
        super().__init__(self.message)
