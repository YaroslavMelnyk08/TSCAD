import tkinter as tk
import numpy as np
import heapq
from collections import deque

occupied_cells = set()
first_graph_paths = set()

# Функція для обчислення матриці зв'язків
def create_connection_matrix():
    C = np.zeros((7, 7), dtype=int)  # Матриця 7x7 для зв'язків (A-H)
    elements = ['A', 'B', 'C', 'D', 'E', 'F', 'H']

    for i, element in enumerate(elements):
        connections = connection_entries[i].get().strip().upper()  # Отримуємо зв'язки для кожного елементу
        for connection in connections:
            if connection in elements:  # Перевіряємо чи введена буква правильна
                j = elements.index(connection)  # Отримуємо індекс зв'язаного елемента
                C[i][j] += 1  # Додаємо зв'язок
    return C

# Функція для обчислення початкової матриці
def get_initial_matrix():
    initial_matrix = np.full((11, 9), '', dtype=str)  # Початкова матриця 11x9
    for i in range(11):
        for j in range(9):
            value = fixed_entries[i][j].get().strip().upper()
            initial_matrix[i][j] = value if value else ''
    return initial_matrix

# Функція для пошуку елементу на матриці
def find_element_positions(matrix):
    positions = {}
    elements = ['A', 'B', 'C', 'D', 'E', 'F', 'H']
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i][j] in elements:
                positions[matrix[i][j]] = (i, j)
    return positions

# Функція для пошуку найкоротшого шляху (алгоритм Лі)
def lee_algorithm(matrix, start, goal):
    rows, cols = matrix.shape
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Тільки горизонтальні та вертикальні рухи
    costs = np.full((rows, cols), np.inf)
    costs[start] = 0
    queue = [(0, start)]
    previous = {start: None}  # Запам'ятовуємо попередні кроки

    while queue:
        cost, (x, y) = heapq.heappop(queue)
        if (x, y) == goal:
            break

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in occupied_cells:
                new_cost = cost + 1  # Вага горизонтальних та вертикальних рухів дорівнює 1
                if new_cost < costs[nx, ny]:
                    costs[nx, ny] = new_cost
                    heapq.heappush(queue, (new_cost, (nx, ny)))
                    previous[(nx, ny)] = (x, y)  # Записуємо попередню клітинку

    # Відновлюємо шлях
    path = []
    if costs[goal] < np.inf:
        step = goal
        while step:
            path.append(step)
            step = previous[step]
        path.reverse()  # Шлях у правильному порядку

    # Додаємо знайдений шлях до списку зайнятих клітинок
    for cell in path:
        occupied_cells.add(cell)

    return path if path else None

# Функція для побудови графіки з червоною лінією
def draw_matrix_with_connection(matrix, paths):
    canvas_width = 450  # Ширина canvas
    canvas_height = 550  # Висота canvas
    cell_size = 50  # Розмір однієї клітинки

    canvas = tk.Canvas(result_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack(side=tk.LEFT)

    # Малюємо сітку і елементи
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            canvas.create_rectangle(x1, y1, x2, y2, outline="black")
            if matrix[i][j] != "":
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=matrix[i][j], font=("Arial", 16))

    # Малюємо червоні лінії для кожного шляху
    for path in paths:
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            x1_canvas = y1 * cell_size + cell_size / 2
            y1_canvas = x1 * cell_size + cell_size / 2
            x2_canvas = y2 * cell_size + cell_size / 2
            y2_canvas = x2 * cell_size + cell_size / 2
            canvas.create_line(x1_canvas, y1_canvas, x2_canvas, y2_canvas, fill="red", width=3)

# Функція для альтернативного пошуку шляху
def find_alternative_path(start, goal, occupied_cells, grid_size):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Праворуч, вниз, ліворуч, вгору
    queue = deque([(start, [])])  # Черга з поточним положенням і пройденим шляхом
    visited = set()

    while queue:
        (current_pos, path_taken) = queue.popleft()
        if current_pos == goal:
            return path_taken + [goal]  # Повертаємо повний шлях, якщо досягнуто цілі

        if current_pos in visited:
            continue
        visited.add(current_pos)

        for dx, dy in directions:
            next_x = current_pos[0] + dx
            next_y = current_pos[1] + dy
            next_pos = (next_x, next_y)

            # Перевірка меж та зайнятих клітинок
            if 0 <= next_x < grid_size[0] and 0 <= next_y < grid_size[1] and next_pos not in occupied_cells:
                queue.append((next_pos, path_taken + [current_pos]))  # Додаємо нову позицію до шляху

    return []  # Повертаємо порожній шлях, якщо не знайдено

# Функція для малювання невдалих шляхів
def draw_failed_paths(matrix, failed_paths, occupied_cells_for_failed):
    canvas_width = 450  # Ширина canvas
    canvas_height = 550  # Висота canvas
    cell_size = 50  # Розмір кожної клітинки

    canvas = tk.Canvas(result_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack(side=tk.LEFT)

    # Малюємо сітку та елементи
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            canvas.create_rectangle(x1, y1, x2, y2, outline="black")

            if matrix[i][j] != "":
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=matrix[i][j], font=("Arial", 16))

    # Малюємо лінії для кожного невдалого шляху
    all_failed_paths = []  # Зберігання всіх альтернативних шляхів
    for start_pos, goal_pos in failed_paths:
        # Перевіряємо, чи вже намальований шлях у першому графіку
        if (start_pos, goal_pos) in first_graph_paths or (goal_pos, start_pos) in first_graph_paths:
            continue

        # Пошук альтернативного шляху
        alternative_path = find_alternative_path(start_pos, goal_pos, occupied_cells_for_failed, matrix.shape)
        if alternative_path:
            # Малюємо альтернативний шлях
            for (x1, y1), (x2, y2) in zip(alternative_path, alternative_path[1:]):
                x1_canvas = y1 * cell_size + cell_size / 2
                y1_canvas = x1 * cell_size + cell_size / 2
                x2_canvas = y2 * cell_size + cell_size / 2
                y2_canvas = x2 * cell_size + cell_size / 2
                canvas.create_line(x1_canvas, y1_canvas, x2_canvas, y2_canvas, fill="red", width=3)

            for cell in alternative_path:
                occupied_cells_for_failed.add(cell)
            all_failed_paths.append(alternative_path)
        else:
            print(f"Не вдалося знайти альтернативний шлях між {start_pos} та {goal_pos}.")

    return all_failed_paths

# Функція для зберігання зайнятих клітинок з першого графіка
def store_occupied_cells_from_first_graph(paths, occupied_cells):
    for path in paths:
        for cell in path:
            occupied_cells.add(cell)

# Функція для підрахунку зайнятих клітинок
def calculate_occupied_cells(paths_red, paths_blue, matrix):
    element_positions = find_element_positions(matrix)
    occupied_red = set()
    occupied_blue = set()

    # Підрахунок зайнятих клітинок червоними лініями
    for path in paths_red:
        for cell in path:
            if cell not in element_positions.values():  # Ігноруємо клітинки з елементами
                occupied_red.add(cell)

    # Підрахунок зайнятих клітинок синіми лініями
    for path in paths_blue:
        for cell in path:
            if cell not in element_positions.values():
                occupied_blue.add(cell)

    total_occupied_cells = occupied_red.union(occupied_blue)
    return len(total_occupied_cells)

# Функція для обробки результатів після натискання кнопки "Розрахувати"
def calculate_matrix():
    global result_window, occupied_cells, first_graph_paths
    occupied_cells = set()
    first_graph_paths = set()
    initial_matrix = get_initial_matrix()  # Отримуємо початкову матрицю
    C = create_connection_matrix()  # Створюємо матрицю зв'язків

    # Обчислюємо кількість зв'язків для кожного елемента
    connection_sums = np.sum(C, axis=1)  # Вектор кількості зв'язків для кожного елемента
    elements = ['A', 'B', 'C', 'D', 'E', 'F', 'H']
    element_connections = list(zip(elements, connection_sums))

    # Сортуємо елементи за кількістю зв'язків (спадний порядок)
    sorted_connections = sorted(element_connections, key=lambda x: x[1], reverse=True)

    # Отримуємо позиції елементів у початковій матриці
    element_positions = find_element_positions(initial_matrix)

    all_paths = []
    failed_paths = []
    occupied_cells_for_failed = set()

    for element, _ in sorted_connections:
        start_pos = element_positions[element]
        connected_elements = [elements[i] for i, val in enumerate(C[elements.index(element)]) if val > 0]

        if not connected_elements:
            continue  # Пропускаємо, якщо немає зв'язків

        for connected_element in connected_elements:
            goal_pos = element_positions[connected_element]

            # Перевірка, чи вже існує зв'язок (перший графік)
            if (start_pos, goal_pos) in first_graph_paths or (goal_pos, start_pos) in first_graph_paths:
                continue

            path = lee_algorithm(initial_matrix, start_pos, goal_pos)
            if path:
                all_paths.append(path)
                store_occupied_cells_from_first_graph([path], occupied_cells)
                for i in range(len(path) - 1):
                    first_graph_paths.add((path[i], path[i + 1]))
                    first_graph_paths.add((path[i + 1], path[i]))
            else:
                failed_paths.append((start_pos, goal_pos))

    result_window = tk.Toplevel(root)
    result_window.title("Результати")

    if all_paths:
        draw_matrix_with_connection(initial_matrix, all_paths)

    paths_blue = []
    if failed_paths:
        paths_blue = draw_failed_paths(initial_matrix, failed_paths, occupied_cells_for_failed)

    connection_text = tk.Text(result_window, height=30, width=40)
    connection_text.pack(side=tk.LEFT)
    connection_text.insert(tk.END, "Матриця зв'язків:\n")
    for row in C:
        connection_text.insert(tk.END, " ".join(map(str, row)) + "\n")

    total_occupied_cells = calculate_occupied_cells(all_paths, paths_blue, initial_matrix)
    hierarchy_text = tk.Text(result_window, height=30, width=40)
    hierarchy_text.pack(side=tk.LEFT)
    hierarchy_text.insert(tk.END, "Ієрархія елементів по кількості зв’язків:\n")
    for element, connections in sorted_connections:
        hierarchy_text.insert(tk.END, f"{element} - {connections} зв'язків\n")

    hierarchy_text.insert(tk.END, f"\nКритерій якості: {total_occupied_cells}")

# Головне вікно
root = tk.Tk()
root.title("Хвильовий алгоритм")

# Фрейм для початкової матриці
fixed_frame = tk.Frame(root)
fixed_frame.grid(row=0, column=0, padx=30, pady=30)

# Створення полів для введення початкової матриці (11x9)
fixed_entries = []
for i in range(11):
    row_entries = []
    for j in range(9):
        entry = tk.Entry(fixed_frame, width=9)
        entry.grid(row=i, column=j)
        row_entries.append(entry)
    fixed_entries.append(row_entries)

# Фрейм для введення зв'язків елементів
connection_frame = tk.Frame(root)
connection_frame.grid(row=0, column=1, padx=30, pady=30)

connection_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'H']
connection_entries = []

for i, label in enumerate(connection_labels):
    tk.Label(connection_frame, text=f"Елемент {label} зв'язаний з:").grid(row=i, column=0, sticky='w')
    entry = tk.Entry(connection_frame)
    entry.grid(row=i, column=1)
    connection_entries.append(entry)

# Кнопка для розрахунків
calculate_button = tk.Button(root, text="Розрахувати", command=calculate_matrix)
calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

root.mainloop()