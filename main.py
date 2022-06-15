from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'EXCEPT: Shooting out of range!'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'EXCEPT: You have already shot at these coordinates!'


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, bow, long, orient):
        self.long = long
        self.bow = bow
        self.orient = orient
        self.lives = long

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.long):
            current_x = self.bow.x
            current_y = self.bow.y

            if self.orient == 0:
                current_x += i

            elif self.orient == 1:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots

    def shooting(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.field = [['0'] * size for t in range(size)]

        self.count = 0

        self.busy = []
        self.ships = []

    def __str__(self):
        string = ''
        string += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for a, row in enumerate(self.field):
            string += f'\n{a + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            string = string.replace('█', '0')
        return string

    def outboard(self, out):
        return not((0 <= out.x < self.size) and (0 <= out.y < self.size))

    def contour(self, ship, verb=False):
        area = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for _ in ship.dots:
            for _x, _y in area:
                current = Dot(_.x + _x, _.y + _y)
                if not(self.outboard(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = '•'
                    self.busy.append(current)

    def add_ship(self, ship):
        for _ in ship.dots:
            if self.outboard(_) or _ in self.busy:
                raise BoardWrongShipException()
        for _ in ship.dots:
            self.field[_.x][_.y] = '█'
            self.busy.append(_)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, _):
        if self.outboard(_):
            raise BoardOutException()
        if _ in self.busy:
            raise BoardUsedException()

        self.busy.append(_)

        for ship in self.ships:
            if ship.shooting(_):
                ship.lives -= 1
                self.field[_.x][_.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Ship destroyed!')
                    return False
                else:
                    print('Hit!')
                    return True

        self.field[_.x][_.y] = '•'
        print('Miss!')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, enemy, board):
        self.enemy = enemy
        self.board = board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        _ = Dot(randint(0, 5), randint(0, 5))
        print(f'AI moving: {_.x + 1}, {_.y + 1}')
        return _


class User(Player):
    def ask(self):
        while True:
            cords = input('You moving: ').split()

            if len(cords) != 2:
                print('Enter 2 coordinates!')
                continue

            x, y = cords

            if not(x.isdigit()):
                print('X must be a number!')
                continue

            if not(y.isdigit()):
                print('Y must be a number!')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        a_int = self.random_board()
        player.hid = True

        self.ai = AI(a_int, player)
        self.us = User(player, a_int)

    def board_generate(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for long in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), (randint(0, self.size))), long, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.board_generate()
        return board

    def greet(self):
        print('--------------------')
        print('-------Welcome------')
        print('-----to-the-game----')
        print('-----Sea Battle-----')
        print('--------------------')
        print('-INSTRUCTION:-------')
        print('-x - line number----')
        print('-y - column number--')
        print('--------------------')

    def loop(self):
        num = 0
        while True:
            print('-' * 20)
            print('User board:')
            print(self.us.board)
            print('-' * 20)
            print('AI board:')
            print(self.ai.board)
            print('-' * 20)
            if num % 2 == 0:
                print('User moving!')
                repeat = self.us.move()
            else:
                print('AI moving!')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print('-' * 20)
                print('User board:')
                print(self.us.board)
                print('AI board:')
                print(self.ai.board)
                print('User win!')
                break
            if self.us.board.count == len(self.us.board.ships):
                print('-' * 20)
                print('User board:')
                print(self.us.board)
                print('AI board:')
                print(self.ai.board)
                print('AI win!')
                break
            num += 1

    def start_game(self):
        self.greet()
        self.loop()


g = Game()
g.start_game()
