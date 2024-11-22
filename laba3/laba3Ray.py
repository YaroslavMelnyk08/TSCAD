import tkinter as tk
import numpy as np

# Глобальні змінні
occupied_cells_list = []  # Кожен шар має свій набір зайнятих клітинок


# Функція для обчислення матриці зв'язків
def create_connection_matrix():
    C = np.zeros((7, 7), dtype=int)  # Матриця 7x7 для зв'язків (A-H)
    elements = ['A', 'B', 'C', 'D', 'E', 'F', 'H']
    for i, element in enumerate(elements):
        connections = connection_entries[i].get().strip().upper()
        for connection in connections:
            if connection in elements:
                j = elements.index(connection)
                C[i][j] += 1
    return C


# Функція для обчислення початкової матриці
def get_initial_matrix():
    initial_matrix = np.full((11, 9), '', dtype=str)
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

# Променевий алгоритм для пошуку найкоротшого шляху
def ray_algorithm(matrix, start, goal, occupied_cells):
    rows, cols = matrix.shape
    directions = {
        'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)
    }

    rays_from_start = {start: set(directions.keys())}
    rays_from_goal = {goal: set(directions.keys())}

    visited_from_start = {start: None}
    visited_from_goal = {goal: None}

    max_iterations = rows * cols  # Максимальна кількість ітерацій
    iteration_count = 0

    while rays_from_start and rays_from_goal:
        iteration_count += 1
        if iteration_count > max_iterations:
            print(f"Шлях між {start} та {goal} не знайдений після {max_iterations} ітерацій.")
            return []  # Повертаємо порожній шлях, якщо перевищили максимальну кількість ітерацій

        # Поширення променів від старту
        new_rays_from_start = {}
        for (x, y), active_directions in rays_from_start.items():
            for direction in active_directions:
                dx, dy = directions[direction]
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in occupied_cells and (
                nx, ny) not in visited_from_start:
                    visited_from_start[(nx, ny)] = (x, y)
                    new_rays_from_start[(nx, ny)] = active_directions  # Продовжуємо рух у всіх напрямках
                    if (nx, ny) in visited_from_goal:
                        return reconstruct_path((nx, ny), visited_from_start, visited_from_goal)
        rays_from_start = new_rays_from_start

        # Поширення променів від цілі
        new_rays_from_goal = {}
        for (x, y), active_directions in rays_from_goal.items():
            for direction in active_directions:
                dx, dy = directions[direction]
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in occupied_cells and (
                nx, ny) not in visited_from_goal:
                    visited_from_goal[(nx, ny)] = (x, y)
                    new_rays_from_goal[(nx, ny)] = active_directions  # Продовжуємо рух у всіх напрямках
                    if (nx, ny) in visited_from_start:
                        return reconstruct_path((nx, ny), visited_from_start, visited_from_goal)
        rays_from_goal = new_rays_from_goal

    return []



# Відновлення шляху після зустрічі променів
def reconstruct_path(meeting_point, visited_from_start, visited_from_goal):
    path = []
    step = meeting_point
    while step:
        path.append(step)
        step = visited_from_start.get(step)
    path.reverse()
    step = visited_from_goal[meeting_point]
    while step:
        path.append(step)
        step = visited_from_goal.get(step)
    return path


# Функція для побудови графіки з червоною лінією
def draw_matrix_with_connection(matrix, paths):
    canvas_width = 450
    canvas_height = 550
    cell_size = 50

    canvas = tk.Canvas(result_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack(side=tk.LEFT)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            canvas.create_rectangle(x1, y1, x2, y2, outline="black")
            if matrix[i][j] != "":
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=matrix[i][j], font=("Arial", 16))

    for path in paths:
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            x1_canvas = y1 * cell_size + cell_size / 2
            y1_canvas = x1 * cell_size + cell_size / 2
            x2_canvas = y2 * cell_size + cell_size / 2
            y2_canvas = x2 * cell_size + cell_size / 2
            canvas.create_line(x1_canvas, y1_canvas, x2_canvas, y2_canvas, fill="red", width=3)


# Функція для обробки результатів після натискання кнопки "Розрахувати"
def calculate_matrix():
    global result_window, occupied_cells_list
    occupied_cells_list = [set(), set(), set()]  # Три окремі шари для кожного канвасу
    total_occupied_cells = set()  # Сукупний набір зайнятих клітинок з усіх шарів
    initial_matrix = get_initial_matrix()
    C = create_connection_matrix()

    elements = ['A', 'B', 'C', 'D', 'E', 'F', 'H']
    element_positions = find_element_positions(initial_matrix)

    # Отримуємо позиції всіх елементів, щоб виключити їх з підрахунку
    element_cells = set(element_positions.values())

    # Набір для зберігання з'єднань, які вже побудовані
    built_connections = set()

    all_paths_by_layers = [[], [], []]  # Три шари для зберігання шляхів окремо для кожного канвасу

    for i, element in enumerate(elements):
        start_pos = element_positions[element]
        connected_elements = [(elements[j], C[i][j]) for j in range(len(elements)) if C[i][j] > 0]

        for connected_element, connection_count in connected_elements:
            goal_pos = element_positions[connected_element]

            # Уникати дублювання зворотних зв'язків
            connection_key = (min(element, connected_element), max(element, connected_element))

            if connection_key not in built_connections:
                for _ in range(connection_count):  # Будуємо стільки зв'язків, скільки потрібно
                    path_found = False  # Відстежуємо, чи був знайдений шлях
                    layer_index = 0  # Починаємо з першого канвасу

                    while layer_index < 3:  # Перевіряємо тільки 3 шари
                        occupied_cells = occupied_cells_list[layer_index]

                        # Перевіряємо, чи не перевищено ліміт шляхів на поточному канвасі
                        if len(all_paths_by_layers[layer_index]) < 4:
                            print(
                                f"Спробуємо знайти шлях між {element} та {connected_element} на шарі {layer_index + 1}.")
                            path = ray_algorithm(initial_matrix, start_pos, goal_pos, occupied_cells)
                            if path:
                                # Додаємо шлях на поточний шар
                                all_paths_by_layers[layer_index].append(path)
                                occupied_cells.update(path)  # Оновлюємо зайняті клітинки поточного шару


                                # Додаємо до сукупних зайнятих клітинок, але виключаємо клітинки з елементами
                                total_occupied_cells.update(set(path) - element_cells)
                                path_found = True
                                break  # Виходимо з циклу, якщо шлях знайдено
                        layer_index += 1  # Переходимо до наступного канвасу

                    # Якщо шлях не знайдений на існуючих шарах, повідомляємо про помилку
                    if not path_found:
                        print(
                            f"Шлях між {element} і {connected_element} не знайдений. Не вистачає шарів для уникнення перетину.")

                # Додаємо з'єднання у набір побудованих зв'язків
                built_connections.add(connection_key)

    # Виведення результатів на трьох канвасах
    result_window = tk.Toplevel(root)
    result_window.title("Результати")

    result_frame = tk.Frame(result_window)
    result_frame.pack(side=tk.LEFT)

    for layer_index, current_paths in enumerate(all_paths_by_layers):
        print(f"Виводимо шари: {layer_index + 1}")
        draw_matrix_with_connection(initial_matrix, current_paths)

    # Додаємо критерій якості (загальна кількість зайнятих клітинок)
    quality_frame = tk.Frame(result_window)
    quality_frame.pack(side=tk.LEFT, padx=20)

    occupied_cells_label = tk.Label(quality_frame,
                                    text=f"Кр. якості: {len(total_occupied_cells)}",
                                    font=("Arial", 12))
    occupied_cells_label.pack()

# Головне вікно
root = tk.Tk()
root.title("Променевий алгоритм трасування")

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
