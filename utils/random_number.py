import random


class NumberGenerate:
    @staticmethod
    def get_one_number():
        number = random.randint(0, 9999)
        return number

    @staticmethod
    def get_one_number_between(last_number: int, first_number: int = 0):
        number = random.randint(first_number, last_number)
        return number

    @staticmethod
    def get_one_number_list(repeat_numbers: bool, size: int):
        if repeat_numbers:
            numbers = [random.randint(0, 9999) for i in range(size)]
            return numbers

        else:
            numbers = []
            qtds = 0
            while qtds < size:
                number = random.randint(0, 9999)
                if number not in numbers:
                    numbers.append(number)
                    qtds += 1

            return numbers

    @staticmethod
    def get_one_number_list_between(repeat_numbers: bool, size: int, second_number: int, first_number: int = 0):
        if repeat_numbers:
            numbers = [random.randint(first_number, second_number) for i in range(size)]
            return numbers

        else:
            numbers = []
            qtds = 0
            while qtds < size:
                number = random.randint(first_number, second_number)
                if number not in numbers:
                    numbers.append(number)
                    qtds += 1

            return numbers


if __name__ == '__main__':
    aleatorio = NumberGenerate()
    print(aleatorio.get_one_number_list(False, 10))
