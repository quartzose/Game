#ASTROCRASH THE GAME, сделано по исходникам из книги Майкла Доусона Python for beginners

import math, random
from livewires import games, color #Отвечает за графику, не робит без модуля pygame

games.init(screen_width = 640, screen_height = 480, fps = 50)


class Wrapper(games.Sprite):
    def update(self):
        """ Если перешёл сквозь границу экрана - появляешься с другой стороны (враппинг экрана) """    
        if self.top > games.screen.height:
            self.bottom = 0

        if self.bottom < 0:
            self.top = games.screen.height

        if self.left > games.screen.width:
            self.right = 0
            
        if self.right < 0:
            self.left = games.screen.width

    def die(self):
        """ СМЭЭЭЭЭЭЭЭЭЭЭРТЬ """
        self.destroy()


class Collider(Wrapper):
    """ Столкновения с астероидами """
    def update(self):
        """ Проверка на столкновение """
        super(Collider, self).update()

        
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die()
            self.die()               

    def die(self):
        """ СМЭРТЬ при касании """
        new_explosion = Explosion(x = self.x, y = self.y)
        games.screen.add(new_explosion)
        self.destroy()


class Asteroid(Wrapper):
    """ Статы для астероида """
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    images = {SMALL  : games.load_image("asteroid_small.bmp"),
              MEDIUM : games.load_image("asteroid_med.bmp"),
              LARGE  : games.load_image("asteroid_big.bmp") }

    SPEED = 2
    SPAWN = 2
    POINTS = 30
    
    total =  0
      
    def __init__(self, game, x, y, size):
        """ Картинка (спрайт) астероида """
        Asteroid.total += 1
        
        super(Asteroid, self).__init__(
            image = Asteroid.images[size],
            x = x, y = y,
            dx = random.choice([1, -1]) * Asteroid.SPEED * random.random()/size, 
            dy = random.choice([1, -1]) * Asteroid.SPEED * random.random()/size)

        self.game = game
        self.size = size

    def die(self):
        """ СМЭРТЬ астероида """
        Asteroid.total -= 1

        self.game.score.value += int(Asteroid.POINTS / self.size)
        self.game.score.right = games.screen.width - 10   
        
        # матрешка из астероидов (из большого падают маленькие)
        if self.size != Asteroid.SMALL:
            for i in range(Asteroid.SPAWN):
                new_asteroid = Asteroid(game = self.game,
                                        x = self.x,
                                        y = self.y,
                                        size = self.size - 1)
                games.screen.add(new_asteroid)

        # Если астероиды кончились - новый лвл  
        if Asteroid.total == 0:
            self.game.advance()

        super(Asteroid, self).die()


class Ship(Collider):
    """ Создание корабля """
    image = games.load_image("ship.bmp")
    sound = games.load_sound("thrust.wav")
    ROTATION_STEP = 3
    VELOCITY_STEP = .03
    VELOCITY_MAX = 3
    MISSILE_DELAY = 25

    def __init__(self, game, x, y):
        """ Спрайт корабля """
        super(Ship, self).__init__(image = Ship.image, x = x, y = y)
        self.game = game
        self.missile_wait = 0

    def update(self):
        """ Перемещение корабля """
        super(Ship, self).update()
    
        # повороты
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP

        # звук двигателей корабля при нажатии на стрелку вверх        
        if games.keyboard.is_pressed(games.K_UP):
            Ship.sound.play()
            
            # Изменение угла спрайта и угла пушки при повороте корабля
            angle = self.angle * math.pi / 180  # переводим в радианы...
            self.dx += Ship.VELOCITY_STEP * math.sin(angle)
            self.dy += Ship.VELOCITY_STEP * -math.cos(angle)

            # рассчет траектории перемещения
            self.dx = min(max(self.dx, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)
            self.dy = min(max(self.dy, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)
            
        # Задержка выстрела
        if self.missile_wait > 0:
            self.missile_wait -= 1
            
        # выстрел на пробел
        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:
            new_missile = Missile(self.x, self.y, self.angle)
            games.screen.add(new_missile)        
            self.missile_wait = Ship.MISSILE_DELAY

    def die(self):
        """ Очередная СМЭРТЬ """
        self.game.end()
        super(Ship, self).die()


class Missile(Collider):
    """ Выстрелы, создание выстрелов """
    image = games.load_image("missile.bmp")
    sound = games.load_sound("missile.wav")
    BUFFER = 40
    VELOCITY_FACTOR = 7
    LIFETIME = 40

    def __init__(self, ship_x, ship_y, ship_angle):
        """ Спрайты и музыка выстрелов """
        Missile.sound.play()
        
        # опять радианы
        angle = ship_angle * math.pi / 180  

        # начальная позиция выстрела(должна совпадать с носом корабля)
        buffer_x = Missile.BUFFER * math.sin(angle)
        buffer_y = Missile.BUFFER * -math.cos(angle)
        x = ship_x + buffer_x
        y = ship_y + buffer_y

        # направление выстрела, траектория
        dx = Missile.VELOCITY_FACTOR * math.sin(angle)
        dy = Missile.VELOCITY_FACTOR * -math.cos(angle)

        # создание выстрела
        super(Missile, self).__init__(image = Missile.image,
                                      x = x, y = y,
                                      dx = dx, dy = dy)
        self.lifetime = Missile.LIFETIME

    def update(self):
        """ Перемещение снаряда """
        super(Missile, self).update()

        # уничтожение выстрела при окончании времени его жизни
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()


class Explosion(games.Animation):
    """ Анимации бабаха """
    sound = games.load_sound("explosion.wav")
    images = ["explosion1.bmp",
              "explosion2.bmp",
              "explosion3.bmp",
              "explosion4.bmp",
              "explosion5.bmp",
              "explosion6.bmp",
              "explosion7.bmp",
              "explosion8.bmp",
              "explosion9.bmp"]

    def __init__(self, x, y):
        super(Explosion, self).__init__(images = Explosion.images,
                                        x = x, y = y,
                                        repeat_interval = 4, n_repeats = 1,
                                        is_collideable = False)
        Explosion.sound.play()


class Game(object):
    """ Создание игрового окружения """
    def __init__(self):
        """ Объявление игровых объектов """
        # Задание лвла
        self.level = 0

        # Подгрузка музла в начале игры
        self.sound = games.load_sound("level.wav")

        # СОздание счета
        self.score = games.Text(value = 0,
                                size = 30,
                                color = color.white,
                                top = 5,
                                right = games.screen.width - 10,
                                is_collideable = False)
        games.screen.add(self.score)

        # Создание корабля
        self.ship = Ship(game = self, 
                         x = games.screen.width/2,
                         y = games.screen.height/2)
        games.screen.add(self.ship)

    def play(self):
        """ Начало игры """
        # Подгрузка музла
        games.music.load("theme.mid")
        games.music.play(-1)

        # Подгрузка бэкграунда
        nebula_image = games.load_image("nebula.jpg")
        games.screen.background = nebula_image

        # Переход на 1 лвл
        self.advance()

        # Начало игры, цикл
        games.screen.mainloop()

    def advance(self):
        """ Переход на некст лвл """
        self.level += 1
        
        # Буфферная зона создания астероидов (безопасная зона, рядом с кораблем не появятся астероиды)
        BUFFER = 150
     
        # Создание астероидов
        for i in range(self.level):
            # Минимальная дистанция от корабля
            x_min = random.randrange(BUFFER)
            y_min = BUFFER - x_min

            # Генерация астероидов
            x_distance = random.randrange(x_min, games.screen.width - x_min)
            y_distance = random.randrange(y_min, games.screen.height - y_min)

            # рассчет положения корабля
            x = self.ship.x + x_distance
            y = self.ship.y + y_distance

            # Растягивает картинку по экрану
            x %= games.screen.width
            y %= games.screen.height
       
            # Создает астекроид
            new_asteroid = Asteroid(game = self,
                                    x = x, y = y,
                                    size = Asteroid.LARGE)
            games.screen.add(new_asteroid)

        # Номер левела
        level_message = games.Message(value = "Уровень " + str(self.level),
                                      size = 40,
                                      color = color.yellow,
                                      x = games.screen.width/2,
                                      y = games.screen.width/10,
                                      lifetime = 3 * games.screen.fps,
                                      is_collideable = False)
        games.screen.add(level_message)

        # Новый звук лвла (отличается только от звука в начале игры, на других лвлах один и тот же звук)
        if self.level > 1:
            self.sound.play()
            
    def end(self):
        """ Конец игры """
        # Показывает гейм овер на 5 секунд, после чего игра может зависнуть, потому что я не предусмотрела адекватный выход :)
        end_message = games.Message(value = "Игра окончена",
                                    size = 90,
                                    color = color.red,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = 5 * games.screen.fps,
                                    after_death = games.screen.quit,
                                    is_collideable = False)
        games.screen.add(end_message)
        


def main():
    astrocrash = Game()
    astrocrash.play()

#Просто традиционный запуск адекватных прог (через main() и вызов этой функции в общем поле видимости)
main()
