from enum import Enum, IntEnum


class MethodEnum(Enum):
    POST = 0
    SUBSCRIBER = 1


class WeekDayEnum(IntEnum):
    monday = 1
    tuesday = 2
    wednesday = 3
    thursday = 4
    friday = 5
    saturday = 6
    sunday = 7

if __name__ == '__main__':
    print(WeekDayEnum(3).name)
