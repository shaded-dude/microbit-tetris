from microbit import *
import random
import music

# shape
SHAPES = [
    [(0,0)],                    
    [(0,0), (0,1)],              
    [(0,0), (1,0)]              
]

def spawn_shape():
    shape = random.choice(SHAPES)
    new_piece = {'blocks': shape, 'x': 2, 'y': 0}
    for dx, dy in shape:
        px = new_piece['x'] + dx
        py = new_piece['y'] + dy
        if py < 5 and grid[py][px]:
            global game_over
            game_over = True
    return new_piece

def draw():
    display.clear()
    for y in range(5):
        for x in range(5):
            if grid[y][x]:
                display.set_pixel(x, y, 9)
    for dx, dy in current['blocks']:
        px = current['x'] + dx
        py = current['y'] + dy
        if 0 <= px < 5 and 0 <= py < 5:
            display.set_pixel(px, py, 5)
    # Pview ghost piece
    ghost_y = current['y']
    while not check_collision(dy=ghost_y - current['y'] + 1):
        ghost_y += 1
    for dx, dy in current['blocks']:
        px = current['x'] + dx
        py = ghost_y + dy
        if 0 <= px < 5 and 0 <= py < 5 and not grid[py][px]:
            display.set_pixel(px, py, 2)

def check_collision(dx=0, dy=1):
    for bx, by in current['blocks']:
        x = current['x'] + bx + dx
        y = current['y'] + by + dy
        if y >= 5 or x < 0 or x >= 5 or (0 <= y < 5 and grid[y][x]):
            return True
    return False

def lock_shape():
    global score
    for bx, by in current['blocks']:
        x = current['x'] + bx
        y = current['y'] + by
        if 0 <= x < 5 and 0 <= y < 5:
            grid[y][x] = 1
    score += len(current['blocks'])
    music.pitch(880, 100)  # drop sound

def clear_lines():
    global grid, score
    new_grid = []
    for row in grid:
        if all(row):
            # clear anim
            for i in range(3):
                for x in range(5):
                    display.set_pixel(x, grid.index(row), 0 if i % 2 == 0 else 9)
                sleep(100)
            score += 5
            music.play(['G4:1', 'C5:2'])  # line clear sound
            new_grid.insert(0, [0]*5)
        else:
            new_grid.append(row)
    while len(new_grid) < 5:
        new_grid.insert(0, [0]*5)
    grid = new_grid

def move(dx):
    new_x = current['x'] + dx
    for bx, by in current['blocks']:
        x = new_x + bx
        y = current['y'] + by
        if x < 0 or x >= 5 or (0 <= x < 5 and 0 <= y < 5 and grid[y][x]):
            return
    current['x'] = new_x

def rotate():
    if len(current['blocks']) == 2:
        a, b = current['blocks']
        if a[0] == b[0]:  # vertical > horizontal
            current['blocks'] = [(0,0), (1,0)]
        else:             # horizontal < vertical
            current['blocks'] = [(0,0), (0,1)]

def drop():
    global current, game_over
    max_y = max([dy for _, dy in current['blocks']]) + 1
    if current['y'] + max_y >= 5 or check_collision():
        lock_shape()
        clear_lines()
        current = spawn_shape()
        if check_collision(dy=0):
            game_over = True
    else:
        current['y'] += 1

# restart by a+b
while True:
    display.scroll("Press A+B")
    while not (button_a.is_pressed() and button_b.is_pressed()):
        sleep(100)
    display.clear()

    # sum stupid sound 
    music.play(['C4:2', 'E4:2', 'G4:2', 'C5:4'])

    # new game state
    grid = [[0]*5 for _ in range(5)]
    score = 0
    game_over = False
    current = spawn_shape()

    # main shit over here
    while not game_over:
        draw()
        drop_speed = max(250, 600 - score * 5)  # more score = more speed 
        sleep(drop_speed)

        # button thingy
        if button_a.is_pressed():
            move(-1)
            draw()
            sleep(150)
        elif button_b.is_pressed():
            move(1)
            draw()
            sleep(150)

        # rotate blocj = a+b (holding a)
        if button_a.is_pressed() and button_b.is_pressed():
            rotate()
            draw()
            sleep(200)

        # tilt 
        x_tilt = accelerometer.get_x()
        if x_tilt < -300:
            move(-1)
            draw()
            sleep(150)
        elif x_tilt > 300:
            move(1)
            draw()
            sleep(150)

        drop()

    # another stupid sound
    music.play(['C5:2', 'A4:2', 'F4:2', 'D4:4'])
    display.scroll("Score: {}".format(score))
    