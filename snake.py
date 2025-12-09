import curses
import random
import time
from typing import Deque, List, Tuple
from collections import deque

Position = Tuple[int, int]


def create_food(snake: Deque[Position], height: int, width: int) -> Position:
    available_positions: List[Position] = [
        (y, x)
        for y in range(1, height - 1)
        for x in range(1, width - 1)
        if (y, x) not in snake
    ]
    if not available_positions:
        raise RuntimeError("No space left for food")
    return random.choice(available_positions)


def init_window() -> curses.window:
    window = curses.initscr()
    curses.curs_set(0)
    window.nodelay(True)
    window.keypad(True)
    window.timeout(150)
    return window


def end_window(window: curses.window) -> None:
    window.nodelay(False)
    window.keypad(False)
    curses.curs_set(1)
    curses.endwin()


def draw_borders(window: curses.window) -> Tuple[int, int]:
    height, width = window.getmaxyx()
    window.border()
    return height, width


def draw_snake(window: curses.window, snake: Deque[Position]) -> None:
    for y, x in snake:
        window.addch(y, x, "#")


def draw_food(window: curses.window, food: Position) -> None:
    y, x = food
    window.addch(y, x, "*")


def next_position(head: Position, direction: int) -> Position:
    y, x = head
    if direction == curses.KEY_UP:
        return y - 1, x
    if direction == curses.KEY_DOWN:
        return y + 1, x
    if direction == curses.KEY_LEFT:
        return y, x - 1
    if direction == curses.KEY_RIGHT:
        return y, x + 1
    return head


def opposite_direction(direction: int) -> int:
    opposites = {
        curses.KEY_UP: curses.KEY_DOWN,
        curses.KEY_DOWN: curses.KEY_UP,
        curses.KEY_LEFT: curses.KEY_RIGHT,
        curses.KEY_RIGHT: curses.KEY_LEFT,
    }
    return opposites.get(direction, direction)


def render_status(window: curses.window, score: int) -> None:
    height, width = window.getmaxyx()
    status = f" Score: {score}  (Press q to quit) "
    window.addstr(0, max(1, (width - len(status)) // 2), status)


def play() -> None:
    window = init_window()
    try:
        height, width = draw_borders(window)
        start_y, start_x = height // 2, width // 2
        snake: Deque[Position] = deque(
            [(start_y, start_x + i) for i in range(2, -1, -1)]
        )
        direction = curses.KEY_RIGHT
        food = create_food(snake, height, width)
        score = 0

        while True:
            window.clear()
            height, width = draw_borders(window)
            render_status(window, score)
            draw_food(window, food)
            draw_snake(window, snake)
            window.refresh()

            key = window.getch()
            if key == ord("q"):
                break
            if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
                if opposite_direction(direction) != key:
                    direction = key

            new_head = next_position(snake[0], direction)
            new_y, new_x = new_head
            if new_y in (0, height - 1) or new_x in (0, width - 1) or new_head in snake:
                window.addstr(height // 2, (width - 9) // 2, "Game Over")
                window.refresh()
                time.sleep(1.5)
                break

            snake.appendleft(new_head)
            if new_head == food:
                score += 1
                window.timeout(max(50, 150 - score * 5))
                food = create_food(snake, height, width)
            else:
                snake.pop()
    finally:
        end_window(window)


if __name__ == "__main__":
    curses.wrapper(lambda stdscr: play())
