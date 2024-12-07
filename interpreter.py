import argparse
import json

def bitreverse(value):
    """Побитовый реверс 32-битного числа."""
    result = 0
    for _ in range(32):  # Для 32-битного числа
        result = (result << 1) | (value & 1)  # Сдвигаем результат и добавляем младший бит
        value >>= 1  # Сдвигаем исходное число вправо
    return result

def interpreter(binary_path, result_path, memory_range, verbose=False):
    # Инициализация памяти и стека
    memory = [0] * 1024  # размер памяти (например, 1024 ячейки)
    stack = []
    memory[0] = 123456  # Например, начальное значение в памяти 0

    with open(binary_path, "rb") as binary_file:
        byte_code = binary_file.read()

    operations = []
    i = 0
    while i < len(byte_code):
        command = byte_code[i]

        if command == 0x19:  # Загрузка константы
            A = byte_code[i+1] & 0x1F  # 5 бит
            B = int.from_bytes(byte_code[i+1:i+4], "little")  # Биты 5-21
            stack.append(B)  # Помещаем значение в стек
            operations.append({"command": "0x19", "position": i})
            i += 5

        elif command == 0x32:  # Чтение из памяти
            A = byte_code[i+1] & 0x1F  # 5 бит
            B = int.from_bytes(byte_code[i+1:i+4], "little")  # Адрес
            if 0 <= B < len(memory):  # Проверка допустимости адреса
                value_from_memory = memory[B]  # Считываем значение из памяти
                stack.append(value_from_memory)
            operations.append({"command": "0x32", "position": i})
            i += 5

        elif command == 0x89:  # Запись в память
            A = byte_code[i+1] & 0x1F  # 5 бит
            B = int.from_bytes(byte_code[i+1:i+4], "little")  # Адрес
            if 0 <= B < len(memory):  # Проверка допустимости адреса
                value_to_write = stack.pop()  # Извлекаем значение из стека
                memory[B] = value_to_write  # Записываем значение в память
            operations.append({"command": "0x89", "position": i})
            i += 5

        elif command == 0x5A:  # Унарная операция bitreverse
            A = byte_code[i+1] & 0x1F  # 5 бит
            B = int.from_bytes(byte_code[i+1:i+4], "little")  # Адрес
            if 0 <= B < len(memory):  # Проверка допустимости адреса
                old_value = memory[B]
                new_value = bitreverse(memory[B])  # Применяем операцию
                memory[B] = new_value
            operations.append({"command": "0x5A", "position": i})
            i += 5

        else:
            # Если команда неизвестна
            raise ValueError(f"Неизвестная команда: {hex(command)} на позиции {i}")

        # Выводим информацию о выполненной команде, если verbose=True
        print(f"Выполнена команда: {hex(command)} на позиции {i}")

    # Сохранение результатов в JSON
    result = {
        "operations": operations,
        "memory": {i: memory[i] for i in range(memory_range[0], memory_range[1] + 1)}  # Сохранение памяти в заданном диапазоне
    }

    with open(result_path, "w", encoding="utf-8") as result_file:
        json.dump(result, result_file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Интерпретатор для учебной виртуальной машины (УВМ).")
    parser.add_argument("binary_path", help="Путь к бинарному файлу (bin)")
    parser.add_argument("result_path", help="Путь к файлу с результатами (json)")
    parser.add_argument("first_index", type=int, help="Первый индекс памяти для вывода")
    parser.add_argument("last_index", type=int, help="Последний индекс памяти для вывода")
    parser.add_argument("--verbose", action="store_true", help="Включить вывод информации о выполненных командах")

    args = parser.parse_args()

    # Проверка значений аргументов
    print(f"verbose: {args.verbose}")  # Выводим значение флага verbose
    interpreter(args.binary_path, args.result_path, (args.first_index, args.last_index), verbose=args.verbose)
