from random import randint, choices
from sys import exit
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_walk = [pygame.transform.rotozoom(self.player_walk_1, 0, screen_height / 400),
                            pygame.transform.rotozoom(self.player_walk_2, 0, screen_height / 400)]
        self.player_index = 0
        self.jump_image = pygame.image.load('graphics/Player/jump.png').convert_alpha()
        self.player_jump = pygame.transform.rotozoom(self.jump_image, 0, screen_height / 400)

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(screen_width / 10, ground_position))
        self.gravity = 0
        self.face_right = True

    def apply_physics(self):
        self.gravity += shc
        self.rect.y += self.gravity
        if self.rect.bottom > ground_position:
            self.rect.bottom = ground_position
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > screen_width:
            self.rect.right = screen_width

    def movement(self):
        # GROUND MOVEMENT
        if pygame.key.get_pressed()[pygame.K_d] and not pygame.key.get_pressed()[pygame.K_a]:
            self.face_right = True
            self.rect.left += swc * 5
            if self.rect.bottom == ground_position:
                self.player_index += 0.1
                if self.player_index >= len(self.player_walk):
                    self.player_index = 0
                self.image = self.player_walk[int(self.player_index)]
        elif pygame.key.get_pressed()[pygame.K_a] and not pygame.key.get_pressed()[pygame.K_d]:
            self.face_right = False
            self.rect.left -= swc * 5
            if self.rect.bottom == ground_position:
                self.player_index += 0.1
                if self.player_index >= len(self.player_walk):
                    self.player_index = 0
                self.image = self.player_walk[int(self.player_index)]
                self.image = pygame.transform.flip(self.image, True, False)
        elif self.rect.bottom == ground_position:
            if self.face_right:
                self.image = self.player_walk[0]
            else:
                self.image = pygame.transform.flip(self.player_walk[0], True, False)

        # AIR MOVEMENT
        if self.rect.bottom < ground_position:
            if self.face_right:
                self.image = self.player_jump
            else:
                self.image = pygame.transform.flip(self.player_jump, True, False)
        if pygame.key.get_pressed()[pygame.K_SPACE] and self.rect.bottom == ground_position:
            self.gravity = -20 * shc
            if game_active:
                jump_sound.play()
        if pygame.key.get_pressed()[pygame.K_s] and self.gravity > -10 * shc:
            self.gravity += 2 * shc
        elif pygame.key.get_pressed()[pygame.K_w] and self.gravity > -5 * shc:
            self.gravity -= 0.6 * shc

    def reset_position(self):
        if not game_active:
            self.rect = self.image.get_rect(midbottom=(80, ground_position))

    def resolution_change(self, prev_w):
        self.player_walk = [pygame.transform.rotozoom(self.player_walk_1, 0, screen_height / 400),
                            pygame.transform.rotozoom(self.player_walk_2, 0, screen_height / 400)]
        self.player_jump = pygame.transform.rotozoom(self.jump_image, 0, screen_height / 400)
        self.image = self.player_walk[int(self.player_index)]
        self.rect = self.image.get_rect(midbottom=(screen_width / (prev_w / self.rect.centerx), ground_position))

    def update(self, change_res=False, previous_width=0):
        if change_res:
            self.resolution_change(previous_width)
        else:
            global adjust_shield
            self.movement()
            self.apply_physics()
            self.reset_position()
            shield_adjustment(self.face_right, self.rect.bottom < ground_position)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()
        self.obstacle_type = obstacle_type

        y_pos = ground_position
        if obstacle_type == 'fly':
            self.fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            self.fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [pygame.transform.rotozoom(self.fly_1, 0, screen_height / 400),
                           pygame.transform.rotozoom(self.fly_2, 0, screen_height / 400)]
            y_pos = ground_position / 1.43
        elif obstacle_type == 'snail':
            self.snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            self.snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [pygame.transform.rotozoom(self.snail_1, 0, screen_height / 400),
                           pygame.transform.rotozoom(self.snail_2, 0, screen_height / 400)]

        self.animation_index = 0

        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(bottomleft=(randint(screen_width, int(screen_width + screen_width / 4)), y_pos))

    def movement(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def resolution_change(self, prev_w):
        if self.obstacle_type == 'fly':
            self.frames = [pygame.transform.rotozoom(self.fly_1, 0, screen_height / 400),
                           pygame.transform.rotozoom(self.fly_2, 0, screen_height / 400)]
            y_pos = ground_position / 1.43
        else:
            self.frames = [pygame.transform.rotozoom(self.snail_1, 0, screen_height / 400),
                           pygame.transform.rotozoom(self.snail_2, 0, screen_height / 400)]
            y_pos = ground_position
        self.image = self.frames[int(self.animation_index)]
        self.rect = self.image.get_rect(bottomleft=(screen_width / (prev_w / self.rect.left), y_pos))

    def update(self, change_res=False, previous_width=0):
        if change_res:
            self.resolution_change(previous_width)
        else:
            self.movement()
            self.rect.x -= 4 * swc
            self.destroy()

    def destroy(self):
        if self.rect.right <= 0:
            self.kill()


class Shield(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.shield_image = pygame.image.load('consumables/shield.png').convert_alpha()
        self.shield_big = pygame.transform.rotozoom(self.shield_image, 0, screen_height / 400)
        self.shield_small = pygame.transform.rotozoom(self.shield_image, 0, screen_height / 800)
        y_pos = randint(int(screen_height / 8), int(screen_height / 4))

        self.image = self.shield_big
        self.rect = self.image.get_rect(bottomleft=(randint(screen_width, screen_width + 200), y_pos))

    def player_shielded(self):
        if shield_active:
            if self.image != self.shield_small:
                self.image = self.shield_small
            self.rect = self.image.get_rect(midbottom=(player.sprite.rect.midtop[0], player.sprite.rect.midtop[1]))
            if adjust_shield:
                if adjust_shield == 'left':
                    self.rect.x -= player.sprite.rect.width / 20
                elif adjust_shield == 'right':
                    self.rect.x += player.sprite.rect.width / 20
        else:
            self.rect.x -= 4 * swc

    def reset_position(self):
        if not game_active:
            self.kill()

    def resolution_change(self, prev_w, prev_h):
        self.shield_small = pygame.transform.rotozoom(self.shield_image, 0, screen_height / 800)
        self.shield_big = pygame.transform.rotozoom(self.shield_image, 0, screen_height / 400)
        if shield_active:
            self.image = self.shield_small
        else:
            self.image = self.shield_big
            self.rect = self.image.get_rect(bottomleft=(screen_width / (prev_w / self.rect.left),
                                                        screen_height / (prev_h / self.rect.bottom)))

    def update(self, change_res=False, previous_width=0, previous_height=0):
        if change_res:
            self.resolution_change(previous_width, previous_height)
        else:
            self.player_shielded()
            self.destroy()
            self.reset_position()

    def destroy(self):
        global random_shield_spawn
        if self.rect.right <= 0:
            self.kill()
            random_shield_spawn = randint(30, 60)


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
    if shield:
        if player.sprite.rect.colliderect(shield.sprite.rect):
            return True
        elif shield_active:
            return True
        else:
            return False


def shield_adjustment(player_is_right, player_is_in_air):
    global adjust_shield
    if not player_is_right and not player_is_in_air:
        adjust_shield = 'left'
    elif not player_is_right and player_is_in_air:
        adjust_shield = 'right'
    else:
        adjust_shield = None


def handle_menu():
    menu_text = ['PLAY', 'CONTROLS', 'OPTIONS', 'EXIT THE GAME']
    menu_y_pos = screen_height / 3
    for i in menu_text:
        menu_image = pygame.image.load('menu/menu_text_bg.png').convert_alpha()
        menu_image = pygame.transform.rotozoom(menu_image, 0, screen_height / 400)
        menu_image_rect = menu_image.get_rect(center=(screen_width / 2, menu_y_pos))

        menu_surface = font.render(i, False, 'Black')
        menu_text_rect = menu_surface.get_rect(center=(menu_image.get_width() / 2, menu_image.get_height() / 2 + 4))

        menu_images.update({i: {'surf': menu_image, 'rect': menu_image_rect}})
        menu_text_image.update({i: {'surf': menu_surface, 'rect': menu_text_rect}})
        menu_y_pos += screen_height / 8


def handle_controls():
    controls_text_and_buttons = {'SPACE:': 'Jump',
                                 'A / D:': 'Move left / right',
                                 'W:': 'Float',
                                 'S:': 'Downfall',
                                 'ESC:': 'Open menu',
                                 }
    controls_y_pos = screen_height / 4
    for i in controls_text_and_buttons:
        current_controls_text = controls_text_and_buttons[i]
        controls_button_surface = font.render(i, False, 'Black')
        controls_button_rect = controls_button_surface.get_rect(
            topright=(screen_width / 2 - screen_width / 40, controls_y_pos))
        controls_button_text.update({i: {'surf': controls_button_surface, 'rect': controls_button_rect}})

        controls_text_surface = font.render(current_controls_text, False, 'Black')
        controls_text_rect = controls_text_surface.get_rect(
            topleft=(screen_width / 2 + screen_width / 40, controls_y_pos))
        controls_text.update({i: {'surf': controls_text_surface, 'rect': controls_text_rect}})
        controls_y_pos += screen_height / 10


def handle_options():
    options_choices = ['Graphics', 'Audio']
    options_y_pos = screen_height * 0.3
    for i in options_choices:
        options_text_surface = font.render(i, False, 'Black')
        options_text_rect = options_text_surface.get_rect(topleft=(screen_height * 0.3, options_y_pos))
        options_text.update({i: {'surf': options_text_surface, 'rect': options_text_rect}})
        options_y_pos += screen_height / 10


def audio_options():
    progress_bar_outer = pygame.image.load('menu/progress_bar_outer.png').convert_alpha()
    progress_bar_outer = pygame.transform.rotozoom(progress_bar_outer, 0, screen_height / 800)
    progress_bar_outer_rect = progress_bar_outer.get_rect(
        center=(screen_width / 1.4545 + screen_width / 267, screen_height / 2.666666666666667 + 1))
    audio_items.update({'outer': {'surf': progress_bar_outer, 'rect': progress_bar_outer_rect}})

    progress_bar_outer_in = pygame.image.load('menu/progress_bar_outer.png').convert_alpha()
    progress_bar_outer_in = pygame.transform.rotozoom(progress_bar_outer_in, 0, screen_height / 800)
    progress_bar_outer_rect_in = progress_bar_outer_in.get_rect(topleft=(0, 0))
    audio_items.update({'outerIn': {'surf': progress_bar_outer_in, 'rect': progress_bar_outer_rect_in}})

    progress_bar_inner = pygame.image.load('menu/progress_bar_inner.png').convert_alpha()
    progress_bar_inner = pygame.transform.rotozoom(progress_bar_inner, 0, screen_height / 800)
    progress_bar_inner_rect = progress_bar_inner.get_rect(
        center=(progress_bar_outer_rect.width / 2 - progress_bar_outer_rect.width / (100 / (100 - volume_percentage)),
                progress_bar_outer_rect.height / 2))
    audio_items.update({'inner': {'surf': progress_bar_inner, 'rect': progress_bar_inner_rect}})

    progress_bar_frame = pygame.image.load('menu/progress_bar_frame.png').convert_alpha()
    progress_bar_frame = pygame.transform.rotozoom(progress_bar_frame, 0, screen_height / 800)
    progress_bar_frame_rect = progress_bar_frame.get_rect(
        center=(screen_width / 1.4545, screen_height / 2.666666666666667))
    audio_items.update({'frame': {'surf': progress_bar_frame, 'rect': progress_bar_frame_rect}})

    progress_bar_button = pygame.image.load('menu/progress_bar_button.png').convert_alpha()
    progress_bar_button = pygame.transform.rotozoom(progress_bar_button, 0, screen_height / 800)
    progress_bar_button_rect = progress_bar_button.get_rect(
        center=(progress_bar_outer_rect.midright[0] - progress_bar_outer_rect.width / (100 / (100 - volume_percentage)),
                progress_bar_outer_rect.midright[1]))
    audio_items.update({'button': {'surf': progress_bar_button, 'rect': progress_bar_button_rect}})

    volume_text = font.render(str(int(volume_percentage)) + ' %', False, 'Black')
    volume_text_rect = volume_text.get_rect(center=(progress_bar_frame_rect.left + progress_bar_frame_rect.width / 2,
                                                    progress_bar_frame_rect.bottom + screen_height / 10))
    audio_items.update({'volume': {'surf': volume_text, 'rect': volume_text_rect}})


def move_audio_bar(mouse_movement):
    global mouse_button_interaction, volume_percentage
    mouse_pos = pygame.mouse.get_pos()
    if mouse_button_interaction:
        bar_outer = audio_items['outer']['rect']
        button_rect = audio_items['button']['rect']
        progress_rect = audio_items['inner']['rect']
        # MOVE BUTTON
        button_rect.x += mouse_movement
        if button_rect.center[0] > bar_outer.right:
            button_rect.right = bar_outer.right + button_rect.width / 2
        elif button_rect.center[0] < bar_outer.left - 3:
            button_rect.left = bar_outer.left - button_rect.width / 2 - 3
        audio_items['button'].update({'rect': button_rect})

        # MOVE PROGRESS
        progress_rect.x += mouse_movement
        if progress_rect.right < progress_inner_center - progress_rect.width / 2:
            progress_rect.right = progress_inner_center - progress_rect.width / 2
        elif progress_rect.right > progress_inner_center + progress_rect.width / 2 - 3:
            progress_rect.right = progress_inner_center + progress_rect.width / 2 - 3
        audio_items['inner'].update({'rect': progress_rect})

        # VOLUME
        volume_percentage = ((button_rect.center[0] - bar_outer.left) * 100) / bar_outer.width
        if volume_percentage < 0:
            volume_percentage = 0
        volume_text = font.render(str(int(volume_percentage)) + ' %', False, 'Black')
        audio_items['volume'].update({'surf': volume_text})
        if volume_percentage == 0:
            background_music.set_volume(0)
            jump_sound.set_volume(0)
        else:
            background_music.set_volume(volume_percentage / 1000 + 0.01)
            jump_sound.set_volume(volume_percentage / 1000 + 0.1)

    if audio_items['button']['rect'].collidepoint(mouse_pos):
        mouse_button_interaction = True
    else:
        mouse_button_interaction = False


def handle_graphics():
    handle_menu()
    handle_controls()
    handle_options()
    audio_options()


def change_resolution(width=800, height=400, full_screen=False):
    global screen, screen_height, screen_width, shc, swc, ground_position, game_name, game_name_rect, font, \
        player_stand, player_stand_rect, start_the_game_rect, start_the_game, highest_score_surf, highest_score_rect

    if full_screen:
        screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    previous_screen_width = screen_width
    previous_screen_height = screen_height
    screen_height = height
    screen_width = width
    shc = height / 400
    swc = width / 800
    ground_position = round(screen_height / 1.3)

    font = pygame.font.Font('font/pixeltype.ttf', int((screen_width + screen_height) / 24))
    game_name = font.render('AVOID THE VERMIN!', False, 'Black')
    game_name_rect = game_name.get_rect(center=(screen_width / 2, screen_height / 7))

    player_stand = pygame.transform.rotozoom(player_stand_img, 0, screen_height / 200)
    player_stand_rect = player_stand.get_rect(center=(screen_width / 2, screen_height / 2))
    start_the_game = font.render('Press ENTER to start the game', False, 'Black')
    start_the_game_rect = start_the_game.get_rect(
        center=(screen_width / 2, player_stand_rect.bottom + screen_height / 8))
    highest_score_surf = pygame.transform.rotozoom(highest_score_surf, 0, screen_width / 1100)
    highest_score_rect = highest_score_surf.get_rect(topleft=(10, 10))

    handle_graphics()
    player.update(True, previous_screen_width)
    obstacle_group.update(True, previous_screen_width)
    shield.update(True, previous_screen_width, previous_screen_height)


# START AND SCREEN
pygame.init()
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screen = pygame.display.set_mode((800, 400), pygame.RESIZABLE)
pygame.display.set_caption('Avoid the vermin!')
fps = pygame.time.Clock()
game_active = False
menu = True
controls = False
options = False
score = 0
end_score = 0
mouse_down = False
volume_percentage = 0
screen_height = screen.get_height()
screen_width = screen.get_width()
shc = screen.get_height() / 400
swc = screen.get_width() / 800
ground_position = round(screen_height / 1.3)

shield_active = False
start_shield_spawn_timer = 0
random_shield_spawn = randint(30, 60)

# BACKGROUND MODELS
sky = pygame.image.load('graphics/sky.png').convert()
ground = pygame.image.load('graphics/ground.png').convert()
font = pygame.font.Font('font/pixeltype.ttf', int((screen_width + screen_height) / 24))
game_name = font.render('AVOID THE VERMIN!', False, 'Black')
game_name_rect = game_name.get_rect(center=(screen_width / 2, screen_height / 7))

# MUSIC
background_music = pygame.mixer.Sound('audio/music.wav')
jump_sound = pygame.mixer.Sound('audio/jump.wav')
if volume_percentage == 0:
    background_music.set_volume(0)
    jump_sound.set_volume(0)
else:
    background_music.set_volume(volume_percentage / 1000 + 0.01)
    jump_sound.set_volume(volume_percentage / 1000 + 0.01)
background_music.play(loops=-1)

# PLAYER
player = pygame.sprite.GroupSingle()
player.add(Player())

# OBSTACLE
obstacle_group = pygame.sprite.Group()
obstacles = {'snail': 66, 'fly': 33}

# MENU
menu_text_image = {}
menu_images = {}
handle_menu()

# CONTROLS
controls_text = {}
controls_button_text = {}
handle_controls()

# OPTIONS
options_text = {}
active_option = {}
handle_options()
fullscreen = False

audio_items = {}
audio_options()
audio = False
mouse_button_interaction = False
progress_inner_center = audio_items['outer']['rect'].width / 2

# SHIELD
shield = pygame.sprite.GroupSingle()
adjust_shield = False

# MENU
player_stand_img = pygame.image.load('graphics/Player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand_img, 0, screen_height / 200)
player_stand_rect = player_stand.get_rect(center=(screen_width / 2, screen_height / 2))

start_the_game = font.render('Press ENTER to start the game', False, 'Black')
start_the_game_rect = start_the_game.get_rect(center=(screen_width / 2, player_stand_rect.bottom + screen_height / 8))

# HIGHEST SCORE
f = open('highest_score.txt', 'r')
highest_score = f.readline()
score_index = highest_score.index(': ')
highest_score = int(highest_score[score_index + 2:])
f.close()
highest_score_surf = font.render('Highest score: ' + str(highest_score), False, '#FF33AA')
highest_score_surf = pygame.transform.rotozoom(highest_score_surf, 0, screen_width / 1100)
highest_score_rect = highest_score_surf.get_rect(topleft=(10, 10))

# TIMER
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)
score_timer = pygame.USEREVENT + 2
pygame.time.set_timer(score_timer, 100)

while True:
    for event in pygame.event.get():
        # QUIT
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # MENU
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if controls:
                controls = False
            elif options:
                options = False
            elif menu:
                menu = False
            else:
                menu = True

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False

        if event.type == pygame.VIDEORESIZE and not fullscreen:
            change_resolution(event.w, event.h)

        if options:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for options_button in options_text:
                    current_options_button = options_text[options_button]
                    options_rect = current_options_button['rect']
                    if options_rect.collidepoint(event.pos):
                        if options_button == 'Graphics':
                            audio = False
                            fullscreen = not fullscreen
                            if fullscreen:
                                change_resolution(monitor_size[0], monitor_size[1], full_screen=True)
                            else:
                                change_resolution(800, 400)
                        elif options_button == 'Audio':
                            audio = True
                        active_option = options_text[options_button]['rect']
                if audio:
                    mouse_down = True

        elif menu and not controls:
            # MENU OPTIONS
            if event.type == pygame.MOUSEBUTTONDOWN:
                for menu_button_text in menu_images:
                    menu_button = menu_images[menu_button_text]
                    menu_rect = menu_button['rect']
                    if menu_rect.collidepoint(event.pos):
                        if menu_button_text == 'PLAY':
                            menu = False
                            if not game_active:
                                game_active = True
                        elif menu_button_text == 'CONTROLS':
                            controls = True
                        elif menu_button_text == 'OPTIONS':
                            options = True
                        elif menu_button_text == 'EXIT THE GAME':
                            pygame.quit()
                            exit()
        elif game_active:
            # OBSTACLE SPAWN
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choices([i for i in obstacles],
                                                    weights=[obstacles.get(i) for i in obstacles])[0]))
            if event.type == score_timer:
                score += 1
            end_score = score
        else:
            score = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_active = True

    # GAME
    if menu:
        screen.fill((94, 129, 162))
        screen.blit(game_name, game_name_rect)
        if controls:
            # DISPLAY CONTROLS
            for x in controls_button_text:
                current_button_text = controls_button_text[x]
                screen.blit(current_button_text['surf'], current_button_text['rect'])
            for y in controls_text:
                current_text = controls_text[y]
                screen.blit(current_text['surf'], current_text['rect'])
        elif options:
            # DISPLAY OPTIONS
            pygame.draw.rect(screen, (150, 150, 150), (
                int(screen_height / 4), int(screen_height / 4), int(screen_width / 1.3), int(screen_height / 1.6)))
            pygame.draw.rect(screen, (32, 32, 32), (
                int(screen_height / 4), int(screen_height / 4), int(screen_width / 1.3), int(screen_height / 1.6)), 2)
            pygame.draw.line(screen, (32, 32, 32), (screen_width / 2, screen_height / 4),
                             (screen_width / 2, screen_height / 1.142857142857143 - 1), 3)
            if active_option:
                pygame.draw.rect(screen, (200, 200, 200), active_option)
            for x in options_text:
                current_options_text = options_text[x]
                screen.blit(current_options_text['surf'], current_options_text['rect'])
            if audio:
                mouse_move_x = pygame.mouse.get_rel()[0]
                if mouse_down:
                    move_audio_bar(mouse_move_x)
                else:
                    mouse_button_interaction = False
                for x in audio_items:
                    current_progress_bar = audio_items[x]
                    if x == 'outerIn':
                        pass
                    elif x == 'inner':
                        audio_items['outer']['surf'].blit(audio_items['outerIn']['surf'],
                                                          audio_items['outerIn']['rect'])
                        audio_items['outer']['surf'].blit(current_progress_bar['surf'], current_progress_bar['rect'])
                    else:
                        screen.blit(current_progress_bar['surf'], current_progress_bar['rect'])
                        # audio_items['outer']['surf'].blit(audio_items['outer']['surf'], (0, 0))
        else:
            # DISPLAY MENU TEXTS
            for x in menu_images:
                current_menu_image = menu_images[x]
                current_menu_text = menu_text_image[x]
                screen.blit(current_menu_image['surf'], current_menu_image['rect'])
                current_menu_image['surf'].blit(current_menu_text['surf'], current_menu_text['rect'])

    elif game_active:
        # BACKGROUND
        screen.blit(pygame.transform.scale(sky, (screen_width, screen_height)), (0, 0))
        screen.blit(pygame.transform.scale(ground, (screen_width, screen_height)), (0, ground_position))
        pygame.draw.rect(screen, '#c8e0ec',
                         (game_name_rect.left - 5,
                          game_name_rect.top - 5,
                          game_name_rect.width + 10,
                          game_name_rect.height + 5),
                         0, 5)
        screen.blit(game_name, game_name_rect)

        # SCORE
        score_surf = font.render('Score: ' + str(score), False, (32, 32, 32))
        score_rect = score_surf.get_rect(center=(screen_width / 2, game_name_rect.bottom + screen_height / 20))
        screen.blit(score_surf, score_rect)

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

    else:  # DEATH SCREEN
        player.update()
        shield.update()
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)
        screen.blit(game_name, game_name_rect)
        screen.blit(start_the_game, start_the_game_rect)

        start_shield_spawn_timer = int(pygame.time.get_ticks() / 1000)

        # SCORE
        score_message = font.render('Score: ' + str(end_score), False, 'Black')
        score_message_rect = score_message.get_rect(
            center=(screen_width / 2, game_name_rect.bottom + screen_height / 20))

        if end_score != 0:
            screen.blit(score_message, score_message_rect)
        if end_score > highest_score:
            highest_score = end_score
            f = open('highest_score.txt', 'w')
            f.write('Highest score: ' + str(highest_score))
            f.close()
            highest_score_surf = font.render('Highest score: ' + str(highest_score), False, '#FF33AA')
            highest_score_surf = pygame.transform.rotozoom(highest_score_surf, 0, 0.7)
            highest_score_rect = highest_score_surf.get_rect(topleft=(10, 10))

        screen.blit(highest_score_surf, highest_score_rect)

    pygame.display.update()
    fps.tick(60)
