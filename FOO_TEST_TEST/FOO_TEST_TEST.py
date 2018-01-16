#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'ipetrash'


import cv2
import numpy as np


def crop_by_contour(img, contour):
    rect = cv2.boundingRect(contour)
    x, y, h, w = rect
    return img[y:y+h, x:x+w]


def get_game_board(img__or__file_name):
    if isinstance(img__or__file_name, str):
        img = cv2.imread(img__or__file_name)
    else:
        img = img__or__file_name

    # cv2.imshow('img', img)

    edges = cv2.Canny(img, 100, 200)
    # cv2.imshow('edges_img', edges)

    ret, thresh = cv2.threshold(edges, 200, 255, cv2.THRESH_BINARY)
    image, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.imshow('image_', image)

    # cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
    # cv2.imshow('img_with_contour', img)
    #
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    if not contours:
        print('Не получилсоь найти контуры')
        quit()

    print(len(contours))
    print([cv2.contourArea(i) for i in contours if cv2.contourArea(i) > 10000])
    contours = [i for i in contours if 249000 < cv2.contourArea(i) < 255000]
    if not contours:
        print('Не получилсоь найти контур поля игры')
        # quit()
        return

    # img_with_contour = img.copy()
    # cv2.drawContours(img_with_contour, contours, -1, (0, 255, 0), 3)
    # cv2.imshow('img_with_contour', img_with_contour)

    crop_img = crop_by_contour(img, contours[-1])
    # cv2.imshow("cropped", crop_img)
    #
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    return crop_img


def get_cell_point_by_contour(board_img):
    # cv2.imshow("board_img", board_img)
    temp_board_img = board_img.copy()
    w, h, _ = temp_board_img.shape

    indent = 15
    size_cell = 122

    for i in range(5):
        cv2.rectangle(temp_board_img, (0, size_cell * i), (w, size_cell * i + indent), 0, cv2.FILLED)
        cv2.rectangle(temp_board_img, (size_cell * i, 0), (size_cell * i + indent, h), 0, cv2.FILLED)

    # cv2.imshow("temp_board_img", temp_board_img)

    gray_img = cv2.cvtColor(temp_board_img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_img, 50, 255, cv2.THRESH_BINARY)
    gray_img_contours, cell_contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.imshow("gray_img_contours", gray_img_contours)

    print(len(cell_contours))
    print([cv2.contourArea(i) for i in cell_contours])

    cell_contours = [i for i in cell_contours if cv2.contourArea(i) > 10000]
    print(len(cell_contours))

    if len(cell_contours) != 16:
        print('Нужно ровно 16 контуров ячеек')
        quit()

    # img_with_contour = board_img.copy()
    # cv2.drawContours(img_with_contour, cell_contours, -1, (0, 255, 0), 3)
    # cv2.imshow('img_with_contour_' + str(hex(id(board_img))), img_with_contour)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    sort_x = sorted([cv2.boundingRect(x)[0] for x in cell_contours])
    mean_of_points = [
        sum(sort_x[0:4]) // 4,
        sum(sort_x[4:8]) // 4,
        sum(sort_x[8:12]) // 4,
        sum(sort_x[12:16]) // 4,
    ]

    # print(mean_of_points)
    MEAN_EPS = 5
    # print(sorted([cv2.boundingRect(x)[1] for x in cell_contours]))

    point_by_contour = dict()
    for contour in cell_contours:
        x, y, _, _ = cv2.boundingRect(contour)
        # print(x, y)

        for mean_point in mean_of_points:
            # Максимальное отклонение от средней позиции
            if abs(x - mean_point) <= MEAN_EPS:
                x = mean_point

            if abs(y - mean_point) <= MEAN_EPS:
                y = mean_point

        point_by_contour[(x, y)] = contour

    # cell_contours.sort(key=lambda x: (cv2.boundingRect(x)[1], cv2.boundingRect(x)[0]))
    # print([(cv2.boundingRect(contour)[0], cv2.boundingRect(contour)[1]) for contour in cell_contours])

    return point_by_contour


def show_cell_on_board(board_img, point_by_contour):
    image = board_img.copy()

    row = 0
    col = 0
    value_matrix = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    i = 1

    cell_contours = list(point_by_contour.values())

    # for contour in cell_contours:
    for pos, contour in sorted(point_by_contour.items(), key=lambda x: (x[0][1], x[0][0])):
        rect_cell = cv2.boundingRect(contour)
        x, y, w, h = rect_cell
        # x, y = pos

        cell_img = crop_by_contour(board_img, contour)
        main_color = get_main_color_bgr(cell_img)

        text_row_col = '{}x{}'.format(row, col)
        text_pos = '{}x{}'.format(x, y)
        print(text_row_col)
        print('   ', text_pos)

        cv2.putText(image, str(i), (x, y + h//4), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0))
        cv2.putText(image, text_pos, (x + w // 3, y + h // 7), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 0))
        cv2.putText(image, text_row_col, (x + w // 8, y + int(h // 1.2)), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

        value_cell = get_value_by_color(main_color)
        print('    value:', value_cell)
        value_matrix[row][col] = value_cell

        if value_cell is not None:
            cv2.putText(image, str(value_cell), (x + w - 35, y + int(h // 1.2)), cv2.FONT_HERSHEY_PLAIN, 1.1, (100, 100, 0))

        else:
            file_name = 'unknown_{}.png'.format('-'.join(map(str, main_color)))
            print('    NOT FOUND COLOR:', main_color, file_name)
            cv2.imwrite(file_name, cell_img)

        col += 1
        if col == 4:
            col = 0
            row += 1

        i += 1

    print(value_matrix)

    cv2.drawContours(image, cell_contours, -1, (0, 255, 0), 3)
    cv2.imshow("img_with_contour_cell_contours_" + str(hex(id(image))), image)


def get_value_matrix_from_board(board_img, point_by_contour):
    row = 0
    col = 0
    value_matrix = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    # for contour in cell_contours:
    for pos, contour in sorted(point_by_contour.items(), key=lambda x: (x[0][1], x[0][0])):
        cell_img = crop_by_contour(board_img, contour)
        main_color = get_main_color_bgr(cell_img)
        value_cell = get_value_by_color(main_color)
        print('    value:', value_cell)
        value_matrix[row][col] = value_cell

        if value_cell is None:
            file_name = 'unknown_{}.png'.format('-'.join(map(str, main_color)))
            print('    NOT FOUND COLOR:', main_color, file_name)
            cv2.imwrite(file_name, cell_img)
            quit()

        col += 1
        if col == 4:
            col = 0
            row += 1

    print(value_matrix)
    return value_matrix


COLOR_BGR_BY_NUMBER = {
    (180, 192, 204): 0,  # None
    (217, 227, 237): 2,
    (199, 223, 235): 4,
    (122, 176, 241): 8,
    (98, 148, 244): 16,
    (94, 123, 244): 32,
    (59, 93, 246): 64,
    (115, 207, 236): 128,
    (98, 203, 236): 256,
    (82, 199, 236): 512,
    (65, 196, 235): 1024,
    (50, 193, 236): 2048,
    (50, 57, 60): 4096,
}


def get_value_by_color(color, deviation=5):
    def _generate_seq(value, deviation):
        """
        value = 5, deviation = 1 -> [4, 5, 6]
        value = 5, deviation = 2 -> [3, 4, 5, 6, 7]
        """

        left = list(range(value, value - deviation - 1, -1))
        right = list((range(value + 1, value + deviation + 1)))
        return list(sorted(left + right))

    for bgr_color, value in COLOR_BGR_BY_NUMBER.items():
        b1, g1, r1 = bgr_color
        b2, g2, r2 = color

        if b2 in _generate_seq(b1, deviation) \
                and g2 in _generate_seq(g1, deviation) \
                and r2 in _generate_seq(r1, deviation):
            return value

    return None


def get_main_color_bgr(image):
    img_points = []

    w, h = image.shape[:2]
    for i in range(h):
        for j in range(w):
            img_points.append(tuple(image[i, j]))

    from collections import Counter
    items = sorted(Counter(img_points).items(), reverse=True, key=lambda x: x[1])
    # print(items)
    return items[0][0]


# from collections import defaultdict
# color_by_images = defaultdict(list)
#
# import glob
# for file_name in glob.glob('data/cell/*.png'):
#     img_cell = cv2.imread(file_name)
#     color = get_main_color_bgr(img_cell)
#     # print(color, file_name)
#
#     color_by_images[color].append(file_name)
#
# # С сохранением файлов по цвету
# for color, images in sorted(color_by_images.items(), key=lambda x: len(x[1]), reverse=True):
#     i = 1
#
#     print('{} ({}):'.format(color, len(images)))
#     for file_name in images:
#         # new_file_name = 'data/cell_color/{}__{}.png'.format('.'.join(map(str, color)), i)
#         new_file_name = 'cell_color/{}__{}.png'.format(color, i)
#         print('    ' + file_name + ' -> ' + new_file_name)
#         import shutil
#         shutil.copy(file_name, new_file_name)
#
#         i += 1
#
#     print()
#
# quit()


# for color, images in sorted(color_by_images.items(), key=lambda x: len(x[1]), reverse=True):
#     print('{} ({}):'.format(color, len(images)))
#     for file_name in images:
#         print('    ' + file_name)
#
#     print()


# board = get_game_board('fojUvGQfBRc.jpg')
# point_by_contour = get_cell_point_by_contour(board)
# show_cell_on_board(board, point_by_contour)

# import glob
# for file_name in glob.glob('data/img/*.jpg'):
#     print(file_name)
#
#     try:
#         board = get_game_board(file_name)
#         point_by_contour = get_cell_point_by_contour(board)
#         # show_cell_on_board(board, point_by_contour)
#
#         for contour in point_by_contour.values():
#             crop_img = crop_by_contour(board, contour)
#
#             import hashlib
#             name_img = 'data/cell/' + hashlib.sha1(crop_img.data.tobytes()).hexdigest() + '.png'
#             # cv2.imshow(name_img, crop_img)
#             # hash_by_img[name_img] = crop_img
#             print(name_img)
#
#             cv2.imwrite(name_img, crop_img)
#
#     except Exception as e:
#         print(e)
#

# #
# # Save cell images:
#
# hash_by_img = dict()
#
# import hashlib
# import glob
# for file_name in glob.glob('data/img/*.jpg'):
#     try:
#         board = get_game_board(file_name)
#         point_by_contour = get_cell_point_by_contour(board)
#
#         cell_contours = list(point_by_contour.values())
#         for contour in cell_contours:
#             crop_img = crop_by_contour(board, contour)
#
#             name_img = hashlib.sha1(crop_img.data.tobytes()).hexdigest() + '.png'
#             # cv2.imshow(name_img, crop_img)
#             hash_by_img[name_img] = crop_img
#
#             cv2.imwrite('cell/' + name_img, crop_img)
#
#     except:
#         pass
#
#
# print(len(hash_by_img))
# # print(hash_by_img.keys())
# quit()


# import glob
# for file_name in glob.glob('test/*.png'):
#     image = cv2.imread(file_name)
#     print(get_main_color_bgr(image), get_main_color_bgr(image, append_gray=False), file_name)
# quit()


# import glob
# for file_name in glob.glob('*.png'):
#     board_img = get_game_board(cv2.imread(file_name))
#     point_by_contour = get_cell_point_by_contour(board_img)
#     show_cell_on_board(board_img, point_by_contour)
#     value_matrix = get_value_matrix_from_board(board_img, point_by_contour)
#     print('value_matrix:', value_matrix)


import pyautogui
import time

# pil_image = pyautogui.screenshot()
# opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
# board_img = get_game_board(opencv_image)
# # board_img = get_game_board(cv2.imread('img_bad.png'))
# # board_img = get_game_board(cv2.imread('img.png'))
# point_by_contour = get_cell_point_by_contour(board_img)
# show_cell_on_board(board_img, point_by_contour)
# value_matrix = get_value_matrix_from_board(board_img, point_by_contour)
# print('value_matrix:', value_matrix)
#
# cv2.waitKey()
# cv2.destroyAllWindows()
# quit()

# SOURCE: https://github.com/eshirazi/2048-bot
from eshirazi_2048_bot.board import Board
from eshirazi_2048_bot.board_score_heuristics import perfect_heuristic
from eshirazi_2048_bot.board_score_strategy import ExpectimaxStrategy


STRATEGY = ExpectimaxStrategy(perfect_heuristic)


# TODO: append logger
# TODO: append try/except/finally
while True:
    pil_image = pyautogui.screenshot()
    opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    board_img = get_game_board(opencv_image)
    if board_img is None:
        time.sleep(1)
        continue

    # board_img = get_game_board(cv2.imread('img.png'))
    point_by_contour = get_cell_point_by_contour(board_img)
    # show_cell_on_board(board_img, point_by_contour)
    value_matrix = get_value_matrix_from_board(board_img, point_by_contour)
    print('value_matrix:', value_matrix)

    board = Board(value_matrix)
    print(board)

    next_move = str(STRATEGY.get_next_move(board))
    print('next_move:', next_move)

    pyautogui.typewrite([next_move])

    # board.move(next_move)
    # print('has_moves:', board.has_legal_moves())
    # print('max tile:', board.get_max_tile())

    time.sleep(1)
