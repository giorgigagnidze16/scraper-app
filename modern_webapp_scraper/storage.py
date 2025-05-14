import os, csv, json, sqlite3


def save_csv(rows, fields, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'data.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def save_json(rows, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'data.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    return path


def save_sqlite(rows, fields, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    db_path = os.path.join(output_dir, 'data.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cols = ", ".join(f"{f} TEXT" for f in fields)
    cur.execute(f"CREATE TABLE IF NOT EXISTS items ({cols});")
    for r in rows:
        placeholders = ", ".join('?' for _ in fields)
        values = [r[f] for f in fields]
        cur.execute(f"INSERT INTO items VALUES ({placeholders});", values)
    conn.commit(); conn.close()
    return db_path