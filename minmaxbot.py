from bot import Bot
import time
from common import Point


class MinimaxBot(Bot):

    def move(self, board, nth_move):
        best_score = float('-inf')
        best_move = None
        start_time = time.time()
        considered_moves = set()  # add this line

        for depth in range(1, 20):  # iterative deepening
            if time.time() - start_time > 5:  # if time limit exceeded
                break
            for x in range(19):
                for y in range(19):
                    if board[y][x] == 0 and (x, y) not in considered_moves:  # check if the spot is empty and not considered yet
                        considered_moves.add((x, y))  # add move to the set of considered moves
                        board[y][x] = self.player
                        score = self.minimax(board, depth, float('-inf'), float('inf'), False, start_time)
                        board[y][x] = 0
                        if score > best_score:
                            best_score = score
                            best_move = (x, y)

        return best_move


    def minimax(self, board, depth, alpha, beta, maximizing_player, start_time):
        if time.time() - start_time > 10:  # if time limit exceeded
            return self.heuristic(board)
        if depth == 0 or self.game_over(board):  # if depth reached or game over
            return self.heuristic(board)

        if maximizing_player:
            max_eval = float('-inf')
            for x in range(19):
                for y in range(19):
                    if board[x][y] == 0:  # if the spot is empty
                        board[x][y] = self.player
                        eval = self.minimax(board, depth - 1, alpha, beta, False, start_time)
                        board[x][y] = 0
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break  # beta cut-off
            return max_eval

        else:  # minimizing player
            min_eval = float('inf')
            for x in range(19):
                for y in range(19):
                    if board[x][y] == 0 : # if the spot is empty
                        board[x][y] = 3 - self.player  # opponent's stone
                        eval = self.minimax(board, depth - 1, alpha, beta, True, start_time)
                        board[x][y] = 0
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break  # alpha cut-off
            return min_eval

    def heuristic(self, board):
        my_score = 0
        opponent_score = 0

        for x in range(19):
            for y in range(19):
                if board[x][y] == self.player:
                    # 연속된 돌의 점수
                    my_score += self.check_consecutive(board, x, y, self.player)
                    # 중앙 가까이에 있는 돌의 점수
                    my_score += self.check_center(x, y)
                elif board[x][y] == 3 - self.player:
                    # 상대방의 연속된 돌의 점수
                    opponent_score += self.check_consecutive(board, x, y, 3 - self.player)
        # 점수의 차이를 반환
        return my_score - opponent_score


    def check_consecutive(self, board, x, y, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # 가로, 세로, 대각선 방향
        score = 0

        for dx, dy in directions:
            count = 0
            for i in range(-4, 5):  # 주변 4개의 돌을 확인
                nx, ny = x + dx * i, y + dy * i
                if 0 <= nx < 19 and 0 <= ny < 19 and board[nx][ny] == player:
                    count += 1
                    if count == 5:
                        score += 100 if player == 3 - self.player else 10
                    elif count == 4:
                        score += 50 if player == 3 - self.player else 5
                    elif count == 3:
                        score += 30 if player == 3 - self.player else 3
                    elif count == 2:
                        score += 10 if player == 3 - self.player else 1
                else:
                    count = 0  # 연속되지 않으면 초기화

        return score



    def check_center(self, x, y):
        # 주어진 위치가 중앙에 가까울수록 높은 점수를 반환하는 함수
        # 예를 들어, 중앙에서의 거리를 계산하여 이를 점수로 사용할 수 있습니다.
        center_distance = abs(x - 9) + abs(y - 9)  # 19x19 보드의 중앙은 (9, 9)
        return 9 - center_distance  # 중앙에 가까울수록 높은 점수


    def game_over(self, board):
        for x in range(19):
            for y in range(19):
                if board[x][y] != 0:
                    for dx, dy in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                        if self.check_six(board, x, y, dx, dy):
                            return True
        return False

    def check_six(self, board, x, y, dx, dy):
        count = 0
        for i in range(6):
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < 19 and 0 <= ny < 19 and board[nx][ny] == board[x][y]:
                count += 1
            else:
                break
        return count == 6
