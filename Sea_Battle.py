from random import randint
import time


class BoardException(Exception):
    pass


# класс для обработки исключения, при выстреле за пределы доски
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь сделать выстрел за пределы доски"


# класс для обработки исключения, при повторном выстреле в координаты которые уже был произведен выстрел
class BoardRepeatException(BoardException):
    def __str__(self):
        return "Вы уже делали данный выстрел"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, nose, length, orientation):
        self.nose = nose
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    # Метод для определения точек корабля
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.nose.x
            cur_y = self.nose.y

            # Если корабль расположен вертикально
            if self.orientation == 0:
                cur_x += i

            # Если корабль расположен горизонтально
            elif self.orientation == 1:
                cur_y += i

            # Добавляем координаты в список ship_dots
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self. size = size
        self.hid = hid

        # Счетчик для подсчета подбитых кораблей
        self.count = 0

        # Двумерный список для поля
        self.field = [["0"] * size for _ in range(size)]

        # Список с занятыми точками (либо стоит корабль, либо в нее уже стреляли)
        self.busy = []

        # Список всех кораблей на доске
        self.ships = []

    # Метод для вывода доски в консоль
    def __str__(self):
        # Создаем переменную в которой будет храниться доска
        res = " "
        # В res кладем первую строку
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |"

        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " | "

        if self.hid:
            res = res.replace("■", "0")
        return res

    # Метод для проверки, лежит ли точка за пределами доски
    def out(self, dot):
        return not (0 <= dot.x < self.size) or not (0 <= dot.y < self.size)

    # Метод для обводки контура вокруг корабля
    def contour(self, ship, verb=False):
        # Список точек, соседних с кораблем
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dot in ship.dots:
            for dot_x, dot_y in near:
                cur = Dot(dot.x + dot_x, dot.y + dot_y)
                # Если точка не за пределами поля и не занята, то добавляем ее в список занятых
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "T"
                    self.busy.append(cur)

    # Метод для добавления корабля на доску
    def add_ship(self, ship):
        for dot in ship.dots:
            # Отлавливаем исключение, если точка за пределами поля или уже занята
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        # Добавляем корабль на доску, а также добавляем его точки в список busy
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        # добавляем корабль в список ships
        self.ships.append(ship)
        # выполняем метод contour для корабля
        self.contour(ship)

    # Метод для выстрела
    def shot(self, dot):
        # Отлавливаем исключение, если выстрел произведен за границы доски
        if self.out(dot):
            raise BoardOutException()

        # Отлавливаем исключение, если уже стреляли в эту точку
        if dot in self.busy:
            raise BoardRepeatException()

        # Если в эту точку не стреляли, добавляем ее в список busy
        self.busy.append(dot)

        for ship in self.ships:
            # Если корабль был подстрелен, то отнимаем одну жизнь, и помечаем попадание
            if ship.shooten(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
            # Если жизни закончились, то увеличиваем счетчик убитых кораблей
                if ship.lives == 0:
                    self.count += 1
                    # и обводим его по контуру (verb=True для того чтобы по контуру проставить точки)
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    # Возвращаем True, чтобы произвести еще один ход после ранения
                    return True

        # Если не попали в корабль
        self.field[dot.x][dot.y] = "T"
        print("Мимо!")
        return False

    # Метод для обнуления списка busy в начале игры
    def begin(self):
        self.busy = []

    # метод для высчитывания поражения
    def defeat(self):
        # возвращает True если количество уничтоженных кораблей равно количеству кораблей игрока на доске,
        # False - если не равно
        return self.count == len(self.ships)


# Класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    # Метод пустой, потому что мы будем его определять у потомков этого класса
    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                # Спрашиваем координаты выстрела
                target = self.ask()
                # Если выстрел прошел хорошо, то возвращаем то, нужно ли повторять ход
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# класс игрока-компьютера
class AI(Player):
    def ask(self):
        # с помощью randint генерируем случайную точку
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x+1} {dot.y+1}")
        return dot


# Класс игрока пользователя
class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()

            if len(coords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


# класс игры
class Game:
    # метод, который пытается сгенерировать доску
    # мы пытаемся каждый корабль поставить на доску

    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]

        self.size = size
        # генерируем 2 доски (для игрока и компьютера)
        player = self.random_board()
        comp = self.random_board()
        # скрываем корабли компьютера
        comp.hid = True

        # создаем двух игроков
        self.ai = AI(comp, player)
        self.user = User(player, comp)

    def try_board(self):
        # список с длинами кораблей
        board = Board(size=self.size)
        attempts = 0
        for _ in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size - 1), randint(0, self.size - 1)), _, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # метод который гарантированно создает случайную доску
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    # Приветственное сообщение
    @staticmethod
    def greet():
        print("Добро пожаловать в игру 'Морской бой'.".center(100, "_"))
        print("В ней участвуют два игрока: пользователь и компьютер.".center(100, "_"))
        print("Формат ввода: x y".center(100, "_"))
        print("x - номер строки".center(100, "_"))
        print("y - номер столбца".center(100, "_"))

    def print_boards(self):
        print("-"*30)
        print(f"Доска пользователя:\n{self.user.board}".center(100))
        # print(f"{self.user.board}".center(100))
        print(f"Доска компьютера:\n{self.ai.board}".center(100))
        # print(f"{self.ai.board}".center(100))
        print("-"*30)

    # метод с циклом игры
    def loop(self):
        # счетчик номера хода
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит пользователь!")
                # вызываем метод, отвечающий за ход пользователя
                repeat = self.user.move()
            else:
                print("Ходит компьютер!")
                # вызываем метод, отвечающий за ход компьютера
                time.sleep(15)
                repeat = self.ai.move()
            # данная проверка нужна, чтобы при повторе хода, ход оставался за тем же игроком
            if repeat:
                num -= 1
            # если метод defeat возвращает True, то победа за соперником
            if self.ai.board.count == len(self.ai.board.ships):
                self.print_boards()
                print("-"*20)
                print("Пользователь выиграл!")
                break
            # если метод defeat возвращает True, то победа за соперником
            if self.user.board.defeat():
                self.print_boards()
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    # метод старта игры
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
