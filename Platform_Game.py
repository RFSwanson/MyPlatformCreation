import pygame
import random
import os
"""This platform game sets up a starting series of platform and then sends a continuous stream of birds flying across the screen.
As the player hits the birds the birds are killed and score goes up by one for each bird killed. The score and high score are
drawn at the top of the screen."""

pygame.init()

clock = pygame.time.Clock()
FPS = 60

WIDTH = 1000
HEIGHT = 1500
score = 0

#define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
PANEL = (153,217,234)

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("My Platform Game")

if os.path.exists('score.txt'):
    with open('score.txt','r') as file:
        high_score = int(file.read())
else:
    high_score = 0

#define font
font_small = pygame.font.SysFont('Lucida Sans',40)
font_large = pygame.font.SysFont('Lucida Sans',44)

#load images
bg_img = pygame.image.load('assets/sunny.png')
bg_image = pygame.transform.scale(bg_img,(WIDTH,HEIGHT))

#function for drawing text to the screen
def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

#function for drawing info panel
def draw_panel():
    pygame.draw.rect(screen,PANEL,(0,0,WIDTH,30))
    pygame.draw.line(screen,WHITE,(0,30),(WIDTH,30),2)
    draw_text("SCORE: " + str(player.score),font_small,BLACK,0,0)
    draw_text("HIGH SCORE: " + str(high_score),font_large,BLACK,0,30)


class Player():
    def __init__(self,x,y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1,9):
            img_right = pygame.image.load(f"player-walk/player-walk{num}.png")
            img_right = pygame.transform.scale(img_right,(80,120))
            img_left = pygame.transform.flip(img_right,True,False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.score = 0
        self.in_air = True

    def update(self,high_score):
        dx = 0
        dy = 0
        walk_cooldown = 5

        #get keypresses
        key =  pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
            self.vel_y = -35
            self.jumped = True
            self.in_air = True
        if key[pygame.K_SPACE] == False:
            self.jumped = False
        if key[pygame.K_RIGHT]:
            dx += 5
            self.counter += 1
            self.direction = 1
        if key[pygame.K_LEFT]:
            dx -= 5
            self.counter += 1
            self.direction = -1
        if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
            self.counter = 0
            self.index = 0

        #handle animation
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]    

        #add gravity
        self.vel_y += 1
        dy += self.vel_y
        if self.vel_y > 10:
            self.vel_y = 10
        
        #check for platform ollisions
        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x,self.rect.y + dy,self.width,self.height):
                #if player above the platform
                if self.vel_y >= 0:
                    self.rect.bottom = platform.rect.top
                    dy = 0
                    self.in_air = False
                #if player below the platform
                if self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    dy = 0

        #check for bird collisions
        for bird in bird_group:
            if bird.rect.colliderect(self.rect):
                self.score += 1
                if score > high_score:
                    high_score = score
                bird.kill()
            if self.score > high_score:
                    high_score = self.score
                    with open('score.txt','w') as file:
                        file.write(str(high_score))
            
            

        #update player coordinates
        self.rect.x += dx
        self.rect.y += dy

        screen.blit(self.image,self.rect)

     #check for game_over condition
    def game_over(self,high_score):
        #update high_score
        if score > high_score:
            high_score = score
        
        if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.top > HEIGHT:
            screen.fill((255,0,0))
            draw_text("GAME_OVER",font_large,BLACK,WIDTH//2,HEIGHT//2)
            draw_text("SCORE: " + str(self.score),font_large,BLACK,WIDTH//2,HEIGHT//2 + 50)

class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y,width):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/wood.png")
        self.image = pygame.transform.scale(img,(width,20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Bird(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        for idx in range(1,5):
            img = pygame.image.load(f'Bird A/frame-{idx}.png')
            img = pygame.transform.scale(img,(80,80))
            self.animation_list.append(img)
            self.image = self.animation_list[0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.frame_index = 0
            self.counter = 0
            self.cool_down = 15

    def bird_animation(self):
        self.counter += 1
        if self.counter >= self.cool_down:
            self.frame_index +=1
            if self.frame_index >=3:
                self.frame_index = 0
            self.image = self.animation_list[self.frame_index]
            self.counter = 0


    def update(self):
        self.rect.x += random.randint(1,3)
        if self.rect.x > WIDTH:
            self.kill()
bird_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()  

platform = Platform(WIDTH//2 - 50,HEIGHT - 50,200)  
platform_group.add(platform)

player = Player(WIDTH//2,HEIGHT - 200)

#set up starting platforms
for plat in range(12):
    p_w = random.randint(80,100)
    p_x = random.randint(0,WIDTH - p_w)
    #p_y = random.randint(50,HEIGHT-100)
    p_y = platform.rect.y - 100
    platform = Platform(p_x,p_y,p_w)
    platform_group.add(platform) 

run = True
while run:
    clock.tick(FPS)
    #draw background
    screen.blit(bg_image,(0,0))

    #draw starting platforms
    platform_group.draw(screen)
    player.game_over(high_score)
    player.update(high_score)

    while len(bird_group) <= 2:
        b_x = random.randint(-300,0)
        b_y = random.randint(20,1000)
        bird = Bird(b_x,b_y)
        bird_group.add(bird)
    for bird in bird_group:
        bird.bird_animation()
    bird_group.update()
    bird_group.draw(screen)

    draw_panel()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()