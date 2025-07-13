import os

# Папки, содержимое файлов из которых НЕ нужно показывать
EXCLUDE_DIRS = {'venv', '.venv', 'buildlog', 'models', '.gradio', '__pycache__', '.idea'}

def is_excluded(path):
    """
    True, если в любом сегменте относительного пути встречается папка из EXCLUDE_DIRS.
    """
    return any(part in EXCLUDE_DIRS for part in path.split(os.sep))

def build_tree_and_collect_files(base_path='.'):
    """
    Обходит директорию base_path, строит представление дерева (список строк)
    и собирает пути тех файлов, для которых нужно показать содержимое.
    """
    tree_lines = []
    files_to_print = []

    for root, dirs, files in os.walk(base_path):
        # Относительный путь от base_path
        rel_root = os.path.relpath(root, base_path)
        indent_level = 0 if rel_root == '.' else rel_root.count(os.sep) + 1

        # Строка для текущей директории
        dir_name = '[ROOT]' if rel_root == '.' else rel_root
        tree_lines.append('    ' * indent_level + f"[DIR] {dir_name}")

        # Убираем из обхода вложенные EXCLUDE_DIRS
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for filename in files:
            rel_file = os.path.join(rel_root, filename) if rel_root != '.' else filename
            tree_lines.append('    ' * (indent_level + 1) + f"- {filename}")

            # Собираем файлы, для которых надо вывести содержимое
            if not is_excluded(rel_file):
                files_to_print.append(os.path.join(root, filename))

    return tree_lines, files_to_print

def print_contents(file_paths, max_chars=500):
    """
    Печатает название файла и первые max_chars символов его содержимого.
    """
    for path in file_paths:
        rel = os.path.relpath(path)
        print(f"\n=== {rel} ===")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            snippet = content if len(content) <= max_chars else content[:max_chars] + '...'
            print(snippet)
        except Exception as e:
            print(f"[Ошибка при чтении: {e}]")

if __name__ == '__main__':
    BASE = '.'
    tree, files = build_tree_and_collect_files(BASE)

    # 1) Вывод структуры
    print("СТРУКТУРА ПРОЕКТА:\n")
    for line in tree:
        print(line)

    # 2) Вывод содержимого
    print("\nСОДЕРЖИМОЕ ФАЙЛОВ:\n")
    print_contents(files)
