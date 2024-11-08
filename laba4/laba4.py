import tkinter as tk
from sympy import symbols, Or, And, Not, simplify_logic

# Змінні
X1, X2, X3, X4 = symbols('X1 X2 X3 X4')

# Ініціалізація головного вікна
root = tk.Tk()
root.title("Таблиця істинності та мінімізація")
root.geometry("800x750")

# Заголовок
label = tk.Label(root, text="Введіть 0 або 1 у таблиці істинності:")
label.grid(row=0, column=0, columnspan=6, pady=(10, 5))

# Заголовки стовпців
headers = ["X1", "X2", "X3", "X4", "Y"]
for j, header in enumerate(headers):
    header_label = tk.Label(root, text=header, font=("Arial", 10, "bold"), width=5, borderwidth=1, relief="solid")
    header_label.grid(row=1, column=j) 

# Поля для введення даних таблиці істинності
entries = []

for i in range(16):
    row = []
    for j in range(5):  # X1, X2, X3, X4, Y
        entry = tk.Entry(root, width=5)
        entry.grid(row=i + 2, column=j)
        row.append(entry)
    entries.append(row)

# Заповнення таблиці за замовчуванням
default_values = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1],
    [0, 0, 1, 0, 1],
    [0, 0, 1, 1, 0],
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 1],
    [0, 1, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0],
    [1, 0, 1, 0, 1],
    [1, 0, 1, 1, 0],
    [1, 1, 0, 0, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 0],
]

for i, row in enumerate(default_values):
    for j, val in enumerate(row):
        entries[i][j].insert(0, str(val))

# Поле для виведення результатів
output_text = tk.Text(root, height=15, width=90)
output_text.grid(row=19, column=0, columnspan=6)
output_text.insert(tk.END, "Результати\n")

# Функція для форматування виразів
def format_expression(expr, op_symbol, negate_symbol, wrap_terms=False):
    if isinstance(expr, And):
        terms = [format_expression(arg, '+', '!', wrap_terms=False) for arg in expr.args]
        return f"*".join(f"({term})" for term in terms) if wrap_terms else "".join(terms)
    elif isinstance(expr, Or):
        terms = [format_expression(arg, '*', '!', wrap_terms=False) for arg in expr.args]
        return op_symbol.join(terms)
    elif isinstance(expr, Not):
        return f"{negate_symbol}{format_expression(expr.args[0], '+', '!', wrap_terms=False)}"
    else:
        return str(expr)

# Функція для обчислення ДЗНФ, ДКНФ, мінімізації та відображення карти Карно
def calculate():
    try:
        # Очищення поля виведення
        output_text.delete(1.0, tk.END)

        # Отримання даних із таблиці
        truth_table = []
        for row in entries:
            truth_table.append([int(entry.get()) for entry in row])

        # Обчислення ДЗНФ та ДКНФ
        dznf_terms = []
        dknf_terms = []

        for row in truth_table:
            x1, x2, x3, x4, y = row
            term = (Not(X1) if x1 == 0 else X1) & \
                   (Not(X2) if x2 == 0 else X2) & \
                   (Not(X3) if x3 == 0 else X3) & \
                   (Not(X4) if x4 == 0 else X4)
            if y == 1:
                dznf_terms.append(term)
            else:
                term_dknf = (Not(X1) if x1 == 1 else X1) | \
                            (Not(X2) if x2 == 1 else X2) | \
                            (Not(X3) if x3 == 1 else X3) | \
                            (Not(X4) if x4 == 1 else X4)
                dknf_terms.append(term_dknf)

        # Формування ДЗНФ та ДКНФ
        dznf = Or(*dznf_terms)
        dknf = And(*dknf_terms)

        # Мінімізація
        min_dznf = simplify_logic(dznf, form='dnf')
        min_dknf = simplify_logic(dknf, form='cnf')
        
        # Форматування виразів
        formatted_dznf = format_expression(dznf, '+', '!')
        formatted_dknf = format_expression(dknf, '*', '!', wrap_terms=True)

        formatted_min_dznf = format_expression(min_dznf, '+', '!')
        formatted_min_dknf = format_expression(min_dknf, '*', '!', wrap_terms=True)
        
        # Вивід результатів у текстове поле
        output_text.insert(tk.END, f"ДДНФ: {formatted_dznf}\n")
        output_text.insert(tk.END, f"Мінімізована ДДНФ: {formatted_min_dznf}\n")
        output_text.insert(tk.END, f"ДКНФ: {formatted_dknf}\n")
        output_text.insert(tk.END, f"Мінімізована ДКНФ: {formatted_min_dknf}\n")

        # Відображення карти Карно
        draw_karnaugh_map(truth_table)
        
    except ValueError:
        output_text.insert(tk.END, "Помилка: Введіть тільки 0 або 1 у таблиці істинності.\n")

# Функція для відображення карти Карно в текстовому полі
def draw_karnaugh_map(truth_table):
    karnaugh_map = [[None for _ in range(4)] for _ in range(4)]

    row_order = [0, 1, 3, 2]  # Відповідає значенням (X1X2): 00, 01, 11, 10
    col_order = [0, 1, 3, 2]  # Відповідає значенням (X3X4): 00, 01, 11, 10

    for row in truth_table:
        x1, x2, x3, x4, y = row
        map_row = row_order[(x1 << 1) | x2]
        map_col = col_order[(x3 << 1) | x4]
        karnaugh_map[map_row][map_col] = y

    output_text.insert(tk.END, "\nКарта Карно:\n")
    
    output_text.insert(tk.END, "     " + " | ".join(f"{bin(col)[2:].zfill(2)}" for col in col_order) + "\n")
    output_text.insert(tk.END, "   " + "-" * 20 + "\n")

    for i in range(4):
        row_label = bin(row_order[i])[2:].zfill(2)
        output_text.insert(tk.END, f"{row_label} | ")
        output_text.insert(tk.END, " | ".join(str(karnaugh_map[i][j] if karnaugh_map[i][j] is not None else '-') for j in range(4)) + "\n")


# Кнопка для обчислення
calc_button = tk.Button(root, text="Обчислити", command=calculate)
calc_button.grid(row=18, column=0, columnspan=6, pady=(10, 10))

root.mainloop()