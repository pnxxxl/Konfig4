import argparse
import struct
import json

# Функция для вывода в терминал в нужном формате
def print_operation(op_name, byte_code):
    hex_values = ', '.join(f'0x{byte:02X}' for byte in byte_code)
    print(f"{op_name} - {hex_values}")

# Функция для записи в лог файл в формате JSON и вывода в терминал
def log_operation(log_path, operation_code, byte_code):
    # Преобразуем байты в строку в шестнадцатеричном формате
    byte_code_hex = [f"0x{byte:02X}" for byte in byte_code]
    
    log_entry = {
        "Operation": operation_code,
        "ByteCode": byte_code_hex
    }
    
    # Печать в терминал
    print_operation(operation_code, byte_code)
    
    if log_path:
        with open(log_path, "a", encoding="utf-8") as log_file:
            json.dump(log_entry, log_file)
            log_file.write("\n")

# Функция для сериализации команды в бинарный формат
def serializer(cmd, fields, size):
    bits = 0
    bits |= cmd  # Устанавливаем биты для кода операции
    for value, offset in fields:
        bits |= (value << offset)  # Устанавливаем биты для операндов
    return bits.to_bytes(size, "little")  # Возвращаем байты команды

# Ассемблер для преобразования инструкций в бинарный код
def assembler(instructions, log_path=None):
    byte_code = []
    for operation, *args in instructions:
        if operation == "load":
            B = args[0]
            byte_code_part = serializer(25, [(B, 5)], 5)
            byte_code += byte_code_part
            log_operation(log_path, "load", byte_code_part)
        elif operation == "read":
            B = args[0]
            byte_code_part = serializer(18, [(B, 5)], 5)
            byte_code += byte_code_part
            log_operation(log_path, "read", byte_code_part)
        elif operation == "write":
            B = args[0]
            byte_code_part = serializer(9, [(B, 5)], 5)
            byte_code += byte_code_part
            log_operation(log_path, "write", byte_code_part)
        elif operation == "bitreverse":
            B = args[0]
            byte_code_part = serializer(90, [(B, 5)], 5)  # 0x5A = 90 в десятичной системе
            byte_code += byte_code_part
            log_operation(log_path, "bitreverse", byte_code_part)
    return byte_code

# Чтение инструкций и преобразование их в бинарный код
def assemble(instructions_path: str, log_path=None):
    with open(instructions_path, "r", encoding="utf-8") as f:
        instructions = [[j if not j.isdigit() else int(j) for j in i.split()] for i in f.readlines()]
    return assembler(instructions, log_path)

# Сохранение бинарного файла
def save_to_bin(assembled_instructions, binary_path):
    with open(binary_path, "wb") as binary_file:
        binary_file.write(bytes(assembled_instructions))

if __name__ == "__main__":
    # Обработка командной строки
    parser = argparse.ArgumentParser(description="Assemble the instruction file into byte-code.")
    parser.add_argument("instructions_path", help="Path to the instructions file (txt)")
    parser.add_argument("binary_path", help="Path to the binary file (bin)")
    parser.add_argument("log_path", help="Path to the log file (json)")
    args = parser.parse_args()

    # Инициализация лог файла с заголовками
    with open(args.log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"[\n")  # Начало JSON массива
    
    # Сборка программы
    result = assemble(args.instructions_path, args.log_path)
    
    # Сохранение в бинарный файл
    save_to_bin(result, args.binary_path)
    
    # Завершение записи в JSON лог
    with open(args.log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"]\n")  # Закрытие JSON массива
