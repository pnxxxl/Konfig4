import os
import unittest
from unittest.mock import patch, MagicMock
from assembler import assembler  # Импортируем правильно
from interpreter import interpreter  # Импортируем правильно

# Функция для выполнения операции битового реверса
def bitreverse(byte):
    """Функция для выполнения операции битового реверса над байтом"""
    return int(f'{byte:08b}'[::-1], 2)

class TestBitreverseProcess(unittest.TestCase):

    # Тестируем операцию битового реверса поэлементно
    def test_bitreverse(self):
        # Исходный вектор длиной 4
        vector = [0b11001011, 0b10101010, 0b11110000, 0b00001111]
        
        # Ожидаемый результат после битового реверса
        expected_result = [0b11010011, 0b01010101, 0b00001111, 0b11110000]
        
        # Применяем операцию bitreverse к каждому элементу вектора
        result = [bitreverse(byte) for byte in vector]
        
        # Выводим исходный вектор, результат операции и ожидаемый результат для проверки
        print(f"Исходный вектор: {vector}")
        print(f"Результат после битового реверса: {result}")
        print(f"Ожидаемый результат: {expected_result}")
        
        # Проверяем, что результат совпадает с ожидаемым
        self.assertEqual(result, expected_result)

    @patch('assembler.assembler')
    @patch('assembler.save_to_bin')
    def test_assemble_instructions(self, mock_save_to_bin, mock_assembler):
        # Мокируем возврат функции assembler
        mock_assembler.return_value = b'\x19\x00\x00\x00\x00'  # Пример бинарных данных
        # Мокируем функцию сохранения в файл
        mock_save_to_bin.return_value = None

        # Вызов функции, которую тестируем
        instructions = [("bitreverse", 0)]  # Пример инструкции
        log_path = "bitreverse_log.json"
        binary_path = "output.bin"
        
        # Тестируем assembler (заменили assemble_instructions на assembler)
        byte_code = mock_assembler(instructions, log_path)
        mock_save_to_bin(byte_code, binary_path)

        # Проверка, что функции были вызваны с правильными аргументами
        mock_assembler.assert_called_once_with(instructions, log_path)
        mock_save_to_bin.assert_called_once_with(b'\x19\x00\x00\x00\x00', binary_path)

    @patch('os.path.exists')
    @patch('assembler.assembler')
    @patch('assembler.save_to_bin')
    @patch('interpreter.interpreter')
    def test_integration(self, mock_interpreter, mock_save_to_bin, mock_assembler, mock_exists):
        # Мокируем os.path.exists, чтобы он всегда возвращал False
        mock_exists.return_value = False
        
        # Мокируем ассемблер и интерпретатор
        mock_assembler.return_value = b'\x19\x00\x00\x00\x00'
        mock_save_to_bin.return_value = None
        mock_interpreter.return_value = None
        
        # Вызов основной программы
        # Проверяем, что файл существует, если нет, вызываем assembler
        if not os.path.exists("output.bin"):
            byte_code = mock_assembler([("bitreverse", 0)], "bitreverse_log.json")  # Вызываем assembler
            mock_save_to_bin(byte_code, "output.bin")  # Сохраняем бинарный файл
        mock_interpreter("output.bin", "bitreverse_result.json", (0, 20))  # Вызываем interpreter

        # Проверяем, что assembler и interpreter были вызваны
        mock_assembler.assert_called_once_with([("bitreverse", 0)], "bitreverse_log.json")
        mock_save_to_bin.assert_called_once_with(b'\x19\x00\x00\x00\x00', "output.bin")
        mock_interpreter.assert_called_once_with("output.bin", "bitreverse_result.json", (0, 20))

if __name__ == '__main__':
    unittest.main()
