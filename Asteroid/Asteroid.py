# Import 
from random import randint, choice
from if3_game.engine import init, Game, Layer, Sprite , Text
from pyglet import window, font
from math import cos, sin, radians


#variable
RESOLUTION = (800, 600) # tuple de la taille de la fenêtre
LIFE_MAX = 5

# Classes

class SpaceItem(Sprite) :
    def __init__(self, image, position, anchor, speed = (0,0), rotation_speed = 0):
        super().__init__(image, position, anchor = anchor, collision_shape="circle")
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.keep_on_screen_value = 32
        
    def deplacement(self, dt):
        pos_x = self.position[0]
        pos_y = self.position[1]

        move = (self.speed[0]*dt, self.speed[1]*dt)
        self.position = (pos_x + move[0], pos_y + move[1])

    def keep_on_screen(self):
        value = self.keep_on_screen_value
        if self.position[0] > RESOLUTION[0] + value:
            self.position = (-value, self.position[1])
        
        elif self.position[0] < -value:
            self.position = (RESOLUTION[0] + value, self.position[1])

        if self.position[1] > RESOLUTION[1] + value:
            self.position = (self.position[0], -value)

        elif self.position[1] < -value:
            self.position = (self.position[0], RESOLUTION[1] + value)

    def turnable(self, dt):
        self.rotation += self.rotation_speed * dt

    

    def update(self, dt) :
        super().update(dt)
        self.deplacement(dt)
        self.keep_on_screen()
        self.turnable(dt)
        
  

class Spaceship(SpaceItem):
    def __init__(self, position):
        image = "images/spaceship2.png"
        anchor=(45,45)
        super().__init__(image, position, anchor )
        self.velocity = 0
        self.hp = 3
        self.invulnerability = False
        self.chrono = 0
        self.life = 3
        self.is_kamikaze = False
        self.power_chrono = 0

    def kamikaze(self):
        self.change_image("images/Kamikaze.png")
        self.is_kamikaze = True
        self.power_chrono = 0


    def on_key_press(self, key, modifiers):
        if key == window.key.RIGHT :
            self.rotation_speed =300
            if not self.is_kamikaze:
                self.change_image("images/spaceship2_R.png")
        
        if key == window.key.LEFT:
            self.rotation_speed =-300
            if not self.is_kamikaze:
                self.change_image("images/spaceship2_L.png")

        if key == window.key.UP:
            self.velocity = 5 

        if key ==  window.key.SPACE:
            self.spawn_bullet()    

    def on_key_release(self, key, modifiers):
        
        if key == window.key.RIGHT and self.rotation_speed > 0 :
            self.rotation_speed =0
            if not self.is_kamikaze :
                self.change_image("images/spaceship2.png")

        elif key == window.key.LEFT and self.rotation_speed < 0:
            self.rotation_speed =0
            if not self.is_kamikaze :
                self.change_image("images/spaceship2.png")
        
        if key == window.key.UP:
            self.velocity = 0

    def update(self, dt) :
        if self.invulnerability:
            self.opacity = 125
            self.chrono += dt

            if self.chrono >= 3:
                self.invulnerability = False
                self.chrono = 0

        else:
            self.opacity = 255

        if self.is_kamikaze:
            self.power_chrono += dt
            if self.power_chrono >= 10:
                self.invulnerability = False
                self.power_chrono = 0
                self.change_image("images/spaceship2.png")
                self.is_kamikaze = False

                

      
            
        


        dsx = cos(radians(self.rotation)) * self.velocity
        dsy = sin(radians(-self.rotation)) * self.velocity
        sx = self.speed[0] +dsx
        sy = self.speed[1] + dsy
        self.speed = (sx, sy)
        super().update(dt)

    def on_collision(self, other):
        if isinstance(other, Asteroid): 
            if self.is_kamikaze :
                other.destroy()
            else:
                self.destroy()

    def destroy(self):
        if not self.invulnerability:
            self.life -= 1
            self.invulnerability = True

        if self.life <=0:
            super().destroy()

        

    def spawn_bullet(self):
        bullet_velocity = 100
        sx = cos(radians(self.rotation)) * bullet_velocity
        sy = sin(radians(-self.rotation)) * bullet_velocity
        bullet_speed = (self.speed[0] + sx, self.speed[1] +sy)
        x = cos(radians(self.rotation)) * 40
        y = sin(radians(-self.rotation)) * 40
        bullet_position = (self.position[0] + x, self.position[1] + y)

        bullet = Bullet(bullet_position, bullet_speed)
        self.layer.add(bullet)



class Asteroid(SpaceItem):
    def __init__(self, position, speed, level=3):

        self.level = level
        if level == 3:
            image = "images/asteroid128.png"
            anchor = (64,64)
        elif level ==2:
            image = "images/asteroid64_2.png"
            anchor = (32,32)
        else:
            image = "images/asteroid32.png"
            anchor = (16,16)

        
        rotation_speed = 50
        super().__init__(image, position, anchor, speed , rotation_speed)
        self.keep_on_screen_value = 64

    def destroy(self):
        if self.level >1:
            for _ in range(2):
                level = self.level-1
                asteroid = Asteroid(self.position, (randint(-200, 200 ),randint(-200, 200 )), level = level)
                self.layer.add(asteroid)
                self.layer.game.ui_layer.asteroids.append(asteroid)
        
        if randint(1,5) == 1:
            possibilities = [ OneUp(self.position), Kamikaze(self.position)]
            powerup = choice(possibilities)
            self.layer.add(powerup)

        super().destroy()            
            
            

    def update(self, dt) :
        super().update(dt)
        
class Bullet(SpaceItem):
    def __init__(self, position, speed):
        image = "images/bullet2.png"
        anchor = (8,8)
        super().__init__(image, position, anchor, speed)
        self.keep_on_screen_value = 8
        self.life_time =0

    def on_collision(self, other):
        if isinstance(other, Asteroid): 
            self.destroy()
            other.destroy()

    def update(self,dt):
        super().update(dt)
        self.life_time += dt
        if self.life_time >=5 :
            self.destroy()

class AsteroidGame(Game):
    def __init__(self):
        super().__init__()
        font.add_file("font/daydream_3/Daydream.ttf")

        #creation de layers
        self.bg_layer = Layer()
        self.add(self.bg_layer)

        self.game_layer = Layer()
        self.add(self.game_layer)

        self.ui_layer = UIlayer()
        self.add(self.ui_layer)

        #créer les éléments de jeu
        

        

        self.spaceship = Spaceship((RESOLUTION[0]/2, RESOLUTION[1]/2))
        self.game_layer.add(self.spaceship)
        self.ui_layer.spaceship = self.spaceship

        for _ in range(3):
            x = randint(0, RESOLUTION[0])
            while x >= 200 and x <=RESOLUTION[0]-200:
                x = randint(0, RESOLUTION[0])

            y = randint(0, RESOLUTION[1])
            while x >= 200 and x <=RESOLUTION[1]-200:
                y = randint(0, RESOLUTION[1])

            asteroid = Asteroid((x, y), (randint(-200, 200 ),randint(-200, 200 )))
            self.game_layer.add(asteroid)
            self.ui_layer.asteroids.append(asteroid)

        bg = Sprite("images/BG.png")
        self.bg_layer.add(bg)

        


class UIlayer(Layer):
    def __init__(self):
        super().__init__()
        self.spaceship = None
        self.asteroids = []

        
        self.text_game_over = Text("GAME OVER", (RESOLUTION[0]/2, 400), 36, anchor = "center", font_name="Daydream" , color =(255, 255, 255, 0))
        self.add(self.text_game_over)

        self.text_win = Text("YOU WIN", (RESOLUTION[0]/2, 400), 36, anchor = "center", font_name="Daydream" , color =(255, 255, 255, 0))
        self.add(self.text_win)
            
        

        # Point de vies
        self.hearts = []

        for n in range(LIFE_MAX):
            heart = Sprite("images/life.png", position = (775 + -(n*50),575), anchor = (8,8), scale = 2)
            self.hearts.append(heart)
            self.add(heart)

        
    
    def update(self, dt):
        super().update(dt)
        player_won = True
        for asteroid in self.asteroids:
            if asteroid.is_destroyed == False:
                player_won = False
        
        if player_won:
            self.text_win.opacity = 255
            self.spaceship.opacity = 0


        #affichage de la vie du vaisseau

        for index in range(len(self.hearts)):
            if index < self.spaceship.life:
                self.hearts[index].opacity = 255

            else:
                self.hearts[index].opacity = 0

        if self.spaceship.life == 0:
            self.text_game_over.opacity = 255

            

class PowerUp(SpaceItem):
    def __init__(self, image,position,  anchor, life_time):
        super().__init__(image, position, anchor)
        self.life_time = life_time


    def on_collision(self, other):
        if isinstance(other, Spaceship):
            self.apply_effect(other)
            self.destroy()

    def apply_effect(self, spaceship):
        pass


    def update(self,dt):
        super().update(dt)

        self.life_time -= dt
        if self.life_time <= 0 :
            self.destroy()

        
class OneUp(PowerUp):
    def __init__(self, position):
        image = "images/get_a_life.png"
        anchor = (16,16)
        life_time = 10
        super().__init__(image, position, anchor, life_time)

    def apply_effect(self, spaceship):
        if spaceship.life < LIFE_MAX:
            spaceship.life += 1

class Kamikaze(PowerUp):
    def __init__(self, position):
        image = "images/star_kamikaze.png"
        anchor = (32,32)
        life_time = 10
        super().__init__(image, position, anchor, life_time)

    def apply_effect(self, spaceship):
        spaceship.kamikaze()


        

            
        

        
                    




