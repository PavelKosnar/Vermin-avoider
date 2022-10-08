import pygame
from sys import exit
from random import randint, choice


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/Player/jump.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0
        self.face_right = True

        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.01)

    def apply_physics(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom > 300:
            self.rect.bottom = 300
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800

    def movement(self):
        # GROUND MOVEMENT
        if pygame.key.get_pressed()[pygame.K_d] and not pygame.key.get_pressed()[pygame.K_a]:
            self.face_right = True
            self.rect.left += 5
            if self.rect.bottom == 300:
                self.player_index += 0.1
                if self.player_index >= len(self.player_walk):
                    self.player_index = 0
                self.image = self.player_walk[int(self.player_index)]
        elif pygame.key.get_pressed()[pygame.K_a] and not pygame.key.get_pressed()[pygame.K_d]:
            self.face_right = False
            self.rect.left -= 5
            if self.rect.bottom == 300:
                self.player_index += 0.1
                if self.player_index >= len(self.player_walk):
                    self.player_index = 0
                self.image = self.player_walk[int(self.player_index)]
                self.image = pygame.transform.flip(self.image, True, False)
        elif self.rect.bottom == 300:
            if self.face_right:
                self.image = self.player_walk[0]
            else:
                self.image = pygame.transform.flip(self.player_walk[0], True, False)

        # AIR MOVEMENT
        if self.rect.bottom < 300:
            if self.face_right:
                self.image = self.player_jump
            else:
                self.image = pygame.transform.flip(self.player_jump, True, False)
        if pygame.key.get_pressed()[pygame.K_SPACE] and self.rect.bottom == 300:
            self.gravity = -20
            self.jump_sound.play()
        if pygame.key.get_pressed()[pygame.K_s] and self.gravity > -10:
            self.gravity += 2

    def reset_position(self):
        if not game_active:
            self.rect = self.image.get_rect(midbottom=(80, 300))

    def update(self):
        self.movement()
        self.apply_physics()
        self.reset_position()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()

        if obstacle_type == 'fly':
            fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 210
        else:
            snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0

        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(bottomleft=(randint(800, 1000), y_pos))

    def movement(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.movement()
        self.rect.x -= 4
        self.destroy()

    def destroy(self):
        if self.rect.right <= 0:
            self.kill()


class Menu(pygame.sprite.Sprite):
    def __init__(self, y_pos):
        super().__init__()

        self.image = pygame.image.load('menu/menu_text_bg.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 1.1)
        self.rect = self.image.get_rect(center=(400, y_pos))


class Shield(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        shield_image = pygame.image.load('consumables/shield.png').convert_alpha()
        self.shield_small = pygame.transform.rotozoom(shield_image, 0, 0.5)
        y_pos = 110

        self.image = shield_image
        self.rect = self.image.get_rect(bottomleft=(randint(800, 1000), y_pos))

    def player_shielded(self):
        if shield_active:
            self.image = self.shield_small
            self.rect = self.image.get_rect(midbottom=(player.sprite.rect.midtop[0], player.sprite.rect.midtop[1]))
        else:
            self.rect.x -= 4

    def reset_position(self):
        if not game_active:
            self.kill()

    def update(self):
        self.player_shielded()
        self.destroy()
        self.reset_position()

    def destroy(self):
        global random_shield_spawn
        if self.rect.right <= 0:
            self.kill()
            random_shield_spawn = randint(30, 60)


def display_score():
    global pause_duration
    pause_duration = unpause_time - pause_time
    current_time = pygame.time.get_ticks() - start_time - pause_duration
    score_surf = font.render('Score: ' + str(int(current_time / 100)), False, (32, 32, 32))
    score_rect = score_surf.get_rect(midleft=(330, game_name_rect.bottom + 20))
    screen.blit(score_surf, score_rect)
    return current_time


def collision():
    global shield_active, random_shield_spawn, start_shield_spawn_timer
    if shield_active and pygame.sprite.spritecollide(player.sprite, obstacle_group, True):
        shield.empty()
        shield_active = False
        random_shield_spawn = randint(30, 60)
        start_shield_spawn_timer = int(pygame.time.get_ticks() / 1000)
        return True
    elif pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True


def shield_pickup():
    try:
        if player.sprite.rect.colliderect(shield.sprite.rect):
            return True
        elif shield_active:
            return True
        else:
            return False
    except AttributeError:
        return False
    

def handle_menu_text():
    menu_text = ['PLAY', 'CONTROLS', 'EXIT THE GAME']
    menu_y_pos = 150
    for i in menu_text:
        menu_surface = font.render(i, False, 'Black')
        menu_rect = menu_surface.get_rect(center=(400, menu_y_pos + 4))
        menu_text_image.update({i: {'surf': menu_surface, 'rect': menu_rect}})
        menu_group.add(Menu(menu_y_pos))
        menu_y_pos += 70


# START AND SCREEN
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Avoid the vermin!')
fps = pygame.time.Clock()
game_active = False
menu = True
start_time = 0
pause_time = 0
unpause_time = 0
pause_duration = 0
score = 0

shield_active = False
start_shield_spawn_timer = 0
random_shield_spawn = randint(30, 60)

# BACKGROUND MODELS
sky = pygame.image.load('graphics/sky.png').convert()
ground = pygame.image.load('graphics/ground.png').convert()
font = pygame.font.Font('font/pixeltype.ttf', 50)
game_name = font.render('AVOID THE VERMIN!', False, 'Black')
game_name_rect = game_name.get_rect(center=(400, 60))

# MUSIC
background_music = pygame.mixer.Sound('audio/music.wav')
background_music.set_volume(0.03)
background_music.play(loops=-1)

# GROUPS
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

menu_group = pygame.sprite.Group()
menu_text_image = {}
handle_menu_text()

shield = pygame.sprite.GroupSingle()

# MENU
player_stand = pygame.image.load('graphics/Player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(400, 200))

start_the_game = font.render('Press ENTER to start the game', False, 'Black')
start_the_game_rect = start_the_game.get_rect(center=(400, player_stand_rect.bottom + 50))

# HIGHEST SCORE
f = open('highest_score.txt', 'r')
highest_score = f.readline()
score_index = highest_score.index(': ')
highest_score = int(highest_score[score_index + 2:])
f.close()
highest_score_surf = font.render('Highest score: ' + str(highest_score), False, '#FF33AA')
highest_score_surf = pygame.transform.rotozoom(highest_score_surf, 0, 0.7)
highest_score_rect = highest_score_surf.get_rect(topleft=(10, 10))

# TIMER
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

while True:
    for event in pygame.event.get():
        # QUIT
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # MENU
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if menu:
                menu = False
                unpause_time = pygame.time.get_ticks()
            else:
                menu = True
                pause_time = pygame.time.get_ticks()
        if menu:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for menu_button_text in menu_text_image:
                    menu_button = menu_text_image[menu_button_text]
                    rect = menu_button['rect']
                    if rect.collidepoint(event.pos):
                        if menu_button_text == 'PLAY':
                            menu = False
                            unpause_time = pygame.time.get_ticks()
                            if not game_active:
                                start_time = pygame.time.get_ticks()
                                game_active = True
                        elif menu_button_text == 'EXIT THE GAME':
                            pygame.quit()
                            exit()
        if game_active and not menu:
            # OBSTACLE SPAWN
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail'])))
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_active = True
                start_time = pygame.time.get_ticks()

    if menu:
        screen.fill((94, 129, 162))
        screen.blit(game_name, game_name_rect)

        # DRAW MENU TEXTS
        menu_group.draw(screen)
        menu_group.update()
        for x in menu_text_image:
            current_menu_text = menu_text_image[x]
            screen.blit(current_menu_text['surf'], current_menu_text['rect'])

    elif game_active:
        # BACKGROUND
        screen.blit(sky, (0, 0))
        screen.blit(ground, (0, 300))
        pygame.draw.rect(screen, '#c8e0ec',
                         (game_name_rect.left - 5,
                          game_name_rect.top - 5,
                          game_name_rect.width + 10,
                          game_name_rect.height + 5),
                         0, 5)
        screen.blit(game_name, game_name_rect)

        # SCORE
        score = display_score()
        score = int(score / 100)
        highest_score_surf = font.render('Highest score: ' + str(highest_score), False, '#FF33AA')
        highest_score_surf = pygame.transform.rotozoom(highest_score_surf, 0, 0.7)
        highest_score_rect = highest_score_surf.get_rect(topleft=(10, 10))
        screen.blit(highest_score_surf, highest_score_rect)

        # SHIELD SPAWNER
        try:
            if shield.sprite.rect:
                pass
        except AttributeError:
            if int(pygame.time.get_ticks() / 1000) > random_shield_spawn + start_shield_spawn_timer \
                    and not shield_active:
                start_shield_spawn_timer = int(pygame.time.get_ticks() / 1000) - 1
                shield.add(Shield())

        # DRAW OBJECTS
        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        shield.draw(screen)
        shield.update()

        # SHIELD
        shield_active = shield_pickup()

        # COLLISION
        game_active = collision()

    else:   # MENU
        player.update()
        shield.update()
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)
        screen.blit(game_name, game_name_rect)
        screen.blit(start_the_game, start_the_game_rect)

        start_shield_spawn_timer = int(pygame.time.get_ticks() / 1000)

        # SCORE
        score_message = font.render('Score: ' + str(score), False, 'Black')
        score_message_rect = score_message.get_rect(midleft=(330, game_name_rect.bottom + 20))

        if score != 0:
            screen.blit(score_message, score_message_rect)
        if score > highest_score:
            highest_score = score
            f = open('highest_score.txt', 'w')
            f.write('Highest score: ' + str(highest_score))
            f.close()
            highest_score_surf = font.render('Highest score: ' + str(highest_score), False, '#FF33AA')
            highest_score_surf = pygame.transform.rotozoom(highest_score_surf, 0, 0.7)
            highest_score_rect = highest_score_surf.get_rect(topleft=(10, 10))

        screen.blit(highest_score_surf, highest_score_rect)

    pygame.display.update()
    fps.tick(60)
