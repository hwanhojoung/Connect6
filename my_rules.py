from common import Point, Debugger, repr_direction

debug = Debugger(enable_log=False)

class StrategicStatus:
    def __init__(self):
        self.a = 0
        self.a_point = []
        self.b = 0
        self.b_point = []

# 8방향
DIRECTIONS = [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 0), (-1, 1), (-1, -1)]

def reverse_of(dir):
    return -dir[0], -dir[1]

def is_outta_range(x, y):
    return not(0 <= x < 19 and 0 <= y < 19)

def track(board, start_x, start_y, dir_func):
    pass

def scan_from_last(board, last_points, player):
    for point in last_points:
        x, y = point
        # check 8 directions and start backtracking.
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if is_outta_range(nx, ny): 
                continue

            if board[ny][nx] == board[y][x]:
                debug.log('Direction {}'.format((dx, dy)))
                debug.log('Start at {}'.format(Point(x, y)))

                # to check properly, go to the end of direction
                while board[ny][nx] == board[y][x]:
                    nx += dx
                    ny += dy
                    if is_outta_range(nx, ny): 
                        break

                dx, dy = reverse_of((dx, dy))

                debug.log('End of direction : {}'.format(Point(nx, ny)))

                is_end = track(board, nx, ny, reverse_of((dx, dy)))
                if is_end:
                    # returns player who won.
                    return board[ny][nx]

                debug.stop()

def scan_full(board) -> StrategicStatus:
    pass
