from abc import ABC, abstractmethod
import math
import operator
import shlex
import sys


def parse_number(text, field, positive=False):
    """Преобразует текст в число и проверяет допустимость значения."""
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"Поле {field} должно содержать число.")

    if not math.isfinite(value):
        raise ValueError(f"Поле {field} должно содержать конечное число.")

    if positive and value <= 0:
        raise ValueError(f"Поле {field} должно быть больше нуля.")

    return value


class SmartDevice(ABC):
    """Абстрактный базовый класс устройства умного дома."""

    def __init__(self, manufacturer):
        if not manufacturer.strip():
            raise ValueError("Производитель не может быть пустым.")

        self.manufacturer = manufacturer.strip()

    @abstractmethod
    def __str__(self):
        """Возвращает описание устройства."""
        pass


class SmartLamp(SmartDevice):
    device_type = "LAMP"

    def __init__(self, manufacturer, power, base):
        super().__init__(manufacturer)
        self.power = parse_number(power, "power", positive=True)

        if not base.strip():
            raise ValueError("Тип цоколя не может быть пустым.")

        self.base = base.strip()

    def __str__(self):
        return (
            f"Умная лампочка. Производитель: {self.manufacturer} | "
            f"Мощность: {self.power:g} Вт, Цоколь: {self.base}"
        )


class Thermostat(SmartDevice):
    device_type = "THERMOSTAT"

    def __init__(self, manufacturer, min_temp, max_temp):
        super().__init__(manufacturer)
        self.min_temp = parse_number(min_temp, "min_temp")
        self.max_temp = parse_number(max_temp, "max_temp")

        if self.min_temp > self.max_temp:
            raise ValueError(
                "Минимальная температура не может превышать максимальную."
            )

    def __str__(self):
        return (
            f"Термостат. Производитель: {self.manufacturer} | "
            f"Диапазон температур: от {self.min_temp:g} "
            f"до {self.max_temp:g}"
        )


class SmartSocket(SmartDevice):
    device_type = "SOCKET"

    def __init__(self, manufacturer, max_load):
        super().__init__(manufacturer)
        self.max_load = parse_number(max_load, "max_load", positive=True)

    def __str__(self):
        return (
            f"Умная розетка. Производитель: {self.manufacturer},"
            f"Максимальная нагрузка: {self.max_load:g} Вт"
        )


class SmartHome:
    """Хранит устройства в стандартном списке и обрабатывает команды."""

    OPERATORS = {
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
    }

    NUMERIC_FIELDS = {"power", "min_temp", "max_temp", "max_load"}
    TEXT_FIELDS = {"manufacturer", "type", "base"}

    DEVICE_TYPES = {
        "LAMP": (SmartLamp, 3, 'ADD LAMP "производитель" мощность цоколь'),
        "THERMOSTAT": (
            Thermostat,
            3,
            'ADD THERMOSTAT "производитель" min_temp max_temp'
            ),
        "SOCKET": (SmartSocket, 2, 'ADD SOCKET "производитель" max_load'),
    }

    def __init__(self):
        self.devices: list[SmartDevice] = []

    def add(self, arguments):
        if not arguments:
            raise ValueError("После ADD необходимо указать тип устройства.")

        device_type = arguments[0].upper()

        if device_type not in self.DEVICE_TYPES:
            raise ValueError(f"Неизвестный тип устройства: {device_type}.")

        device_class, parameter_count, syntax = self.DEVICE_TYPES[device_type]
        parameters = arguments[1:]

        if len(parameters) != parameter_count:
            raise ValueError(f"Неверные параметры. Формат: {syntax}")

        device = device_class(*parameters)
        self.devices.append(device)

    def remove(self, arguments):
        if len(arguments) != 3:
            raise ValueError("Формат удаления: REM поле оператор значение")

        field, operation, raw_value = arguments
        field = field.lower()

        if field not in self.NUMERIC_FIELDS and field not in self.TEXT_FIELDS:
            raise ValueError(f"Неизвестное поле: {field}.")

        if operation not in self.OPERATORS:
            raise ValueError(f"Неизвестный оператор: {operation}.")

        if field in self.NUMERIC_FIELDS:
            value = parse_number(raw_value, field)
        else:
            if operation not in {"==", "!="}:
                raise ValueError(
                    "Для текстовых полей допустимы только == и !=."
                )
            value = raw_value.upper() if field == "type" else raw_value

        attribute = "device_type" if field == "type" else field
        compare = self.OPERATORS[operation]

        def matches(device):
            actual_value = getattr(device, attribute, None)

            if actual_value is None:
                return False

            return compare(actual_value, value)

        self.devices = [
            device for device in self.devices if not matches(device)
        ]

    def print_devices(self):
        print(f"\nУстройств в контейнере: {len(self.devices)}")

        if not self.devices:
            print("Контейнер пуст.")
            return

        for index, device in enumerate(self.devices, start=1):
            print(f"{index}. {device}")

    def execute(self, line):
        # shlex сохраняет текст в кавычках как один параметр.
        parts = shlex.split(line, comments=True)

        if not parts:
            return

        command = parts[0].upper()
        arguments = parts[1:]

        if command == "ADD":
            self.add(arguments)
        elif command == "REM":
            self.remove(arguments)
        elif command == "PRINT":
            if arguments:
                raise ValueError("Команда PRINT не принимает параметры.")
            self.print_devices()
        else:
            raise ValueError(f"Неизвестная команда: {command}.")

    def process_file(self, filename):
        with open(filename, "r", encoding="utf-8-sig") as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    self.execute(line)
                except ValueError as error:
                    print(f"Ошибка в строке {line_number}: {error}")


def main():
    if len(sys.argv) != 2:
        return 1

    home = SmartHome()

    try:
        home.process_file(sys.argv[1])
    except (OSError, UnicodeError) as error:
        print(f"Не удалось прочитать файл: {error}")
        return 1

    return 0


if __name__ == "__main__":
    main()
