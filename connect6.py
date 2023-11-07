import tkinter as tk
from tkinter import messagebox
import tensorflow as tf
import numpy as np

width = 800
height = 800
radius = 14
blank = 15
turn = 1  # 1 black 2 white
turnNum = -1
isStart = False
prohibited_mode = False  # 착수 금지점 설정 모드
prohibited_points = []  # 착수 금지점을 저장하는 리스트

root = tk.Tk()
canvas = tk.Canvas(root, width=width, height=height)
canvas.pack()

# 착수 금지점 설정 모드를 켜고 끄는 버튼
def toggle_prohibited_mode():
    global prohibited_mode
    prohibited_mode = not prohibited_mode
    if prohibited_mode:
        toggle_button.config(text="Finish Prohibited Mode")
    else:
        toggle_button.config(text="Start Prohibited Mode")

toggle_button = tk.Button(root, text="Start Prohibited Mode", command=toggle_prohibited_mode)
toggle_button.pack()

boardArray = [[0 for j in range(25)] for i in range(25)]

# Create a simple model
model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(input_shape=(25, 25)),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dense(625, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model with random data
random_board_states = np.random.randint(3, size=(1000, 25, 25))
random_next_moves = np.random.randint(625, size=(1000,))

model.fit(random_board_states, random_next_moves, epochs=5)

def clearBoard():
    global boardArray
    boardArray = [[0 for j in range(25)] for i in range(25)]

def updateBoard():
    global turn
    canvas.delete('all')
    canvas.create_rectangle(0, 0, width, height, fill="#ffcc66")
    for i in range(25):
        canvas.create_line(blank + i * 32, blank, blank + i * 32, height - blank, fill="#333300")
        canvas.create_line(blank, blank + i * 32, height - blank, blank + i * 32, fill="#333300")
    for i in range(4):
        for j in range(4):
            canvas.create_oval(blank + 4 * 32 + i * 8 * 32 - 3, blank + 4 * 32 + j * 8 * 32 - 3,
                                blank + 4 * 32 + i * 8 * 32 + 3, blank + 4 * 32 + j * 8 * 32 + 3,
                                fill="#333300", outline="#333300")
    for i in range(25):
        for j in range(25):
            if boardArray[i][j] == 1:
                canvas.create_oval(blank + i * 32 - radius, blank + j * 32 - radius,
                                    blank + i * 32 + radius, blank + j * 32 + radius,
                                    fill="#000000", outline="#000000")
            elif boardArray[i][j] == 2:
                canvas.create_oval(blank + i * 32 - radius, blank + j * 32 - radius,
                                    blank + i * 32 + radius, blank + j * 32 + radius,
                                    fill="#ffffff", outline="#ffffff")
    # 착수 금지점을 빨간색으로 표시
    for point in prohibited_points:
        canvas.create_oval(blank + point[0] * 32 - radius, blank + point[1] * 32 - radius,
                            blank + point[0] * 32 + radius, blank + point[1] * 32 + radius,
                            fill="#ff0000", outline="#ff0000")
    if turn == 2:  # AI's turn
        ai_move()

def ai_move():
    global turn, turnNum, isStart
    board_state = np.array(boardArray).reshape((1, 25, 25))
    predicted_move = model.predict(board_state).argmax()
    resultPos = {'x': predicted_move // 25, 'y': predicted_move % 25}
    # AI가 놓을 수 있는 곳을 선택할 때, 이미 돌이 놓인 곳이나 착수 금지점을 피하도록 예외 처리를 추가
    while (resultPos['x'], resultPos['y']) in prohibited_points or boardArray[resultPos['x']][resultPos['y']] != 0:
        predicted_move = (predicted_move + 1) % 625  # 다음 위치로 이동
        resultPos = {'x': predicted_move // 25, 'y': predicted_move % 25}
    boardArray[resultPos['x']][resultPos['y']] = turn
    checkOmok(turn, resultPos['x'], resultPos['y'])
    if not isStart:
        turnNum = 2
        turn = 3 - turn
        isStart = True
    else:
        if turnNum == turn:
            turnNum = 3 - turn
        else:
            turn = 3 - turn



clearBoard()
updateBoard()

def getMousePos(event):
    return {'x': event.x, 'y': event.y}

def getMouseRoundPos(xPos, yPos):
    x = (xPos - blank) / 32
    resultX = round(x)
    y = (yPos - blank) / 32
    resultY = round(y)
    return {'x': resultX, 'y': resultY}

def on_move(event):
    mousePos = getMousePos(event)
    drawNotClicked(mousePos['x'], mousePos['y'])

def on_click(event):
    global prohibited_mode
    mousePos = getMousePos(event)
    if prohibited_mode:
        add_prohibited_point(mousePos['x'], mousePos['y'])
    else:
        isClicked(mousePos['x'], mousePos['y'])

canvas.bind("<Motion>", on_move)
canvas.bind("<Button-1>", on_click)

def drawNotClicked(xPos, yPos):
    resultPos = getMouseRoundPos(xPos, yPos)
    if resultPos['x'] > -1 and resultPos['x'] < 28 and resultPos['y'] > -1 and resultPos['y'] < 25 and boardArray[resultPos['x']][resultPos['y']] == 0:
        updateBoard()
        if turn < 2:
            color = "#000000"
        else:
            color = "#ffffff"
        canvas.create_oval(blank + resultPos['x'] * 32 - radius,
                           blank + resultPos['y'] * 32 - radius,
                           blank + resultPos['x'] * 32 + radius,
                           blank + resultPos['y'] * 32 + radius,
                           fill=color, outline=color)

def add_prohibited_point(xPos, yPos):
    resultPos = getMouseRoundPos(xPos, yPos)
    if len(prohibited_points) < 4 and (resultPos['x'], resultPos['y']) not in prohibited_points and resultPos['x'] > -1 and resultPos['x'] < 25 and resultPos['y'] > -1 and resultPos['y'] < 25:
        prohibited_points.append((resultPos['x'], resultPos['y']))
        updateBoard()

def isClicked(xPos, yPos):
    global turn, turnNum, isStart
    resultPos = getMouseRoundPos(xPos, yPos)
    if turn == 2:  # AI's turn
        board_state = np.array(boardArray).reshape((1, 25, 25))
        predicted_move = model.predict(board_state).argmax()
        resultPos = {'x': predicted_move // 25, 'y': predicted_move % 25}
    if (resultPos['x'], resultPos['y']) not in prohibited_points and resultPos['x'] > -1 and resultPos['x'] < 25 and resultPos['y'] > -1 and resultPos['y'] < 25 and boardArray[resultPos['x']][resultPos['y']] == 0:
        boardArray[resultPos['x']][resultPos['y']] = turn
        checkOmok(turn, resultPos['x'], resultPos['y'])
        if not isStart:
            turnNum = 2
            turn = 3 - turn
            isStart = True
        else:
            if turnNum == turn:
                turnNum = 3 - turn
            else:
                turn = 3 - turn
    updateBoard()

def checkOmok(turn, xPos, yPos):
    if addOmok(turn, xPos, yPos, -1, -1) + addOmok(turn, xPos, yPos, 1, 1) == 5:
        gameSet()
    elif addOmok(turn, xPos, yPos, 0, -1) + addOmok(turn, xPos, yPos, 0, 1) == 5:
        gameSet()
    elif addOmok(turn, xPos, yPos, 1, -1) + addOmok(turn, xPos, yPos, -1, 1) == 5:
        gameSet()
    elif addOmok(turn, xPos, yPos, -1, 0) + addOmok(turn, xPos, yPos, 1, 0) == 5:
        gameSet()

def gameSet():
    global turn, prohibited_points
    messagebox.showinfo("Game Over", f"Player {turn} Win~~!!")
    clearBoard()
    prohibited_points.clear()  # 착수 금지점 초기화
    updateBoard()
    turn = 1

def addOmok(turn, xPos, yPos, xDir, yDir):
    if xPos + xDir < 0 or xPos + xDir > 24 or yPos + yDir < 0 or yPos + yDir > 24:
        return 0
    if boardArray[xPos + xDir][yPos + yDir] == turn:
        return 1 + addOmok(turn, xPos + xDir, yPos + yDir, xDir, yDir)
    else:
        return 0

root.mainloop()
