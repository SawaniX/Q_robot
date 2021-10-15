import random
import pygame

width, height = 1100, 800           # width and height of the app window
screen = pygame.display.set_mode((width, height))           # create screen of the app
pygame.display.set_caption("Simulation of the enviornment")       # add title of the window

refreshing = 60         # screen refreshing time per second

scale = 2       # 2 pixels = 1 cm in real life

robot_width, robot_length = 16, 26        # real robot width in cm, real robot length in cm
robot = pygame.image.load('rob.svg')        # load robot image to project
robot = pygame.transform.scale(robot, (robot_width*scale, robot_length*scale))         # rescale image
robot_up = pygame.transform.rotate(robot, 180)
robot_right = pygame.transform.rotate(robot, 90)
robot_left = pygame.transform.rotate(robot, -90)

move_distance = 15          # distance that robot moves in one move in cm
inaccuracy = 3               # inaccuracy of sensors in cm

l_dist, t_dist = 200, 200# odleglosc sciany pomieszczenia od lewej i gornej krawedzi okna [w rzeczywistej odleglosci cm]
room_width, room_height = 150, 150      # real room dimensions in cm
outside_wall_thick = 10         # thickness of the outside walls
exit_width = 30         # real width of the doors in cm
exit_wall_width = (room_width - exit_width) / 2

robot_start_position = [l_dist*scale + 19*scale, t_dist*scale + 105*scale]     # position of the left upper corner of the robot, here 19cm from left wall

black, white, green = (0, 0, 0), (255, 255, 255), (0, 255, 0)


def rotate_robot(pos, robot_direction):         # draw robot in right front direction
    if robot_direction == 0:
        screen.blit(robot, (pos.x, pos.y))
    elif robot_direction == 1:
        screen.blit(robot_up, (pos.x, pos.y))
    elif robot_direction == 2:
        screen.blit(robot_left, (pos.x - 10, pos.y + 10))
    elif robot_direction == 3:
        screen.blit(robot_right, (pos.x - 10, pos.y + 10))


def env(pos, robot_direction):
    screen.fill(black)            # refresh screen

    rotate_robot(pos, robot_direction)  # draw robot in right front direction depends on robot_direction var

    # exterior walls
    pygame.draw.rect(screen, white, (0, 0, width, outside_wall_thick))                             # outside_wall_top
    pygame.draw.rect(screen, white, (0, height-outside_wall_thick, width, outside_wall_thick))     # outside_wall_bottom
    pygame.draw.rect(screen, white, (0, 0, outside_wall_thick, height))                            # outside_wall_left
    pygame.draw.rect(screen, white, (width-outside_wall_thick, 0, outside_wall_thick, height))     # outside_wall_right

    # room walls
    pygame.draw.line(screen, white, (l_dist * scale, t_dist * scale),           # left wall of the room
                     (l_dist * scale, t_dist * scale + room_height * scale))
    pygame.draw.line(screen, white, (l_dist * scale, t_dist * scale + room_height * scale),           # bottom wall
                     (l_dist * scale + room_width * scale, t_dist * scale + room_height * scale))
    pygame.draw.line(screen, white, (l_dist * scale + room_width * scale, t_dist * scale + room_height * scale),
                     (l_dist * scale + room_width * scale, t_dist * scale))                 # right wall
    pygame.draw.line(screen, white, (l_dist * scale, t_dist * scale),           # top wall of the room
                     (l_dist * scale + exit_wall_width * scale, t_dist * scale))
    pygame.draw.line(screen, white, (l_dist * scale + room_width * scale - exit_wall_width * scale, t_dist * scale),
                     (l_dist * scale + room_width * scale, t_dist * scale))             # top wall of the room

    # obstacles
    pygame.draw.rect(screen, white, (l_dist * scale, t_dist * scale + 150, 150, 30))

    pygame.display.update()         # update screen


def forward(pos, robot_direction):
    ran = random.randint(-inaccuracy * scale, inaccuracy * scale)          # inaccuracy of encoders/sensors
    if robot_direction == 0:
        pos.y += move_distance * scale + ran
    elif robot_direction == 1:
        pos.y -= move_distance * scale + ran
    elif robot_direction == 2:
        pos.x -= move_distance * scale + ran
    elif robot_direction == 3:
        pos.x += move_distance * scale + ran
    return pos


def backward(pos, robot_direction):
    ran = random.randint(-inaccuracy * scale, inaccuracy * scale)          # inaccuracy of encoders/sensors
    if robot_direction == 0:
        pos.y -= move_distance * scale + ran
    elif robot_direction == 1:
        pos.y += move_distance * scale + ran
    elif robot_direction == 2:
        pos.x += move_distance * scale + ran
    elif robot_direction == 3:
        pos.x -= move_distance * scale + ran
    return pos


def left(robot_direction):              # rotate left
    if robot_direction == 0:
        robot_direction = 3
    elif robot_direction == 1:
        robot_direction = 2
    elif robot_direction == 2:
        robot_direction = 0
    elif robot_direction == 3:
        robot_direction = 1
    return robot_direction


def right(robot_direction):             # rotate right
    if robot_direction == 0:
        robot_direction = 2
    elif robot_direction == 1:
        robot_direction = 3
    elif robot_direction == 2:
        robot_direction = 1
    elif robot_direction == 3:
        robot_direction = 0
    return robot_direction


def find_center(pos, robot_direction):         # finds center of every edge of the robot
    up_down_x, up_y, down_y, right_left_y, left_x, right_x = 0, 0, 0, 0, 0, 0
    if robot_direction == 0 or robot_direction == 1:            # find center of top, lower, right and left edge
        up_down_x = pos.x + (robot_width * scale) / 2
        up_y = pos.y
        down_y = pos.y + robot_length * scale
        right_left_y = pos.y + (robot_length * scale) / 2
        left_x = pos.x
        right_x = pos.x + robot_width * scale
    elif robot_direction == 2 or robot_direction == 3:
        up_down_x = pos.x - 10 + (robot_length * scale) / 2
        up_y = pos.y + 10
        down_y = pos.y + 10 + robot_width * scale
        right_left_y = pos.y + 10 + (robot_width * scale) / 2
        left_x = pos.x - 10
        right_x = pos.x - 10 + robot_length * scale

    up = [up_down_x, up_y]
    down = [up_down_x, down_y]
    left_edge = [left_x, right_left_y]
    right_edge = [right_x, right_left_y]
    return up, down, left_edge, right_edge


def draw_distances(up, down, left_edge, right_edge, top, low, left, right):         # draws lines from robot edges to the nearest walls
    pygame.draw.line(screen, green, (up[0], up[1]), (up[0], int(up[1] - top)))
    pygame.draw.line(screen, green, (down[0], down[1]), (down[0], int(down[1] + low)))
    pygame.draw.line(screen, green, (left_edge[0], left_edge[1]), (left_edge[0] - left, int(left_edge[1])))
    pygame.draw.line(screen, green, (right_edge[0], right_edge[1]), (right_edge[0] + right, int(right_edge[1])))


def measure(pos, robot_direction):      # measure distance from the nearest wall, simulation of ultrasonic sensors in real robot
    up, down, left_edge, right_edge = find_center(pos, robot_direction)
    up_dist, down_dist, right_dist, left_dist = 0, 0, 0, 0

    margin = 36

    search = True
    tp, dw, lf, rg = True, True, True, True
    odl = 1
    while search:
        if tp and screen.get_at((int(up[0]), int(up[1] + margin - odl)))[:3] == white:          # find distance from top
            up_dist = odl - margin
            tp = False
        if dw and screen.get_at((int(down[0]), int(down[1] - margin + odl)))[:3] == white:
            down_dist = odl - margin
            dw = False
        if lf and screen.get_at((int(left_edge[0] + margin - odl), int(left_edge[1])))[:3] == white:
            left_dist = odl - margin
            lf = False
        if rg and screen.get_at((int(right_edge[0] - margin + odl), int(right_edge[1])))[:3] == white:
            right_dist = odl - margin
            rg = False
        if rg or tp or dw or lf:
            odl += 1
        else:
            search = False

    if robot_direction == 0:
        front_dist = down_dist
        back_dist = up_dist
        r_dist = left_dist
        l_dist = right_dist
        draw_distances(up, down, left_edge, right_edge, back_dist, front_dist, r_dist, l_dist)
    elif robot_direction == 1:
        front_dist = up_dist
        back_dist = down_dist
        r_dist = right_dist
        l_dist = left_dist
        draw_distances(up, down, left_edge, right_edge, front_dist, back_dist, l_dist, r_dist)
    elif robot_direction == 2:
        front_dist = left_dist
        back_dist = right_dist
        r_dist = up_dist
        l_dist = down_dist
        draw_distances(up, down, left_edge, right_edge, r_dist, l_dist, front_dist, back_dist)
    elif robot_direction == 3:
        front_dist = right_dist
        back_dist = left_dist
        r_dist = down_dist
        l_dist = up_dist
        draw_distances(up, down, left_edge, right_edge, l_dist, r_dist, back_dist, front_dist)

    pygame.display.update()
    return front_dist / scale, back_dist / scale, r_dist / scale, l_dist / scale


def main():
    pos = pygame.Rect(robot_start_position[0], robot_start_position[1], robot_width, robot_length)
    robot_direction = 0  # direction of the front of the robot: 0-down, 1-up, 2-left, 3-right

    clock = pygame.time.Clock()     # clock to refresh screen refreshing frames per second
    run = True          # if it is False then quit program

    while run:
        clock.tick(refreshing)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:         # go forward
                    pos = forward(pos, robot_direction)
                if event.key == pygame.K_a:         # turn left and go forward
                    robot_direction = left(robot_direction)
                    forward(pos, robot_direction)
                if event.key == pygame.K_s:         # go backward
                    pos = backward(pos, robot_direction)
                if event.key == pygame.K_d:         # turn right and go forward
                    robot_direction = right(robot_direction)
                    forward(pos, robot_direction)

        env(pos, robot_direction)
        print(measure(pos, robot_direction))
    pygame.quit()


if __name__ == "__main__":
    main()


