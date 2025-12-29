from enum import Enum

class Role(Enum):
    MANAGER = 1
    EMPLOYEE = 2

class AccountStatus(Enum):
    UNRESTRICTED = 0
    RESTRICTED = 1

class QuizStatus(Enum):
    UNCOMPLETED = 0
    COMPLETED = 1
    VISIBLE = 1
    NOT_VISIBLE = 0