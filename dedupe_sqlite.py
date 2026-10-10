import sqlite3

conn = sqlite3.connect('database/startup_platform.db')
c = conn.cursor()
rows = c.execute('SELECT id, user_id, startup_name, domain FROM startup_projects ORDER BY id').fetchall()
print('SQLITE ROWS BEFORE:', rows)

seen = set()
to_del = []
for r in rows:
    name_clean = r[2].strip().lower() if r[2] else ''
    domain_clean = r[3].strip().lower() if r[3] else ''
    key = (r[1], name_clean, domain_clean)
    if key in seen:
        to_del.append(r[0])
    else:
        seen.add(key)

tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
for did in to_del:
    c.execute('DELETE FROM startup_projects WHERE id=?', (did,))
    for tbl in ['market_analysis', 'competitor_data', 'competitors', 'validation_results', 'business_models', 'financial_analysis', 'reports']:
        if tbl in tables:
            try:
                c.execute(f'DELETE FROM {tbl} WHERE startup_id=?', (did,))
            except Exception:
                pass

conn.commit()
rows_after = c.execute('SELECT id, user_id, startup_name, domain FROM startup_projects ORDER BY id').fetchall()
print(f"Removed {len(to_del)} duplicate SQLite projects. Remaining unique: {len(rows_after)}")
print('SQLITE ROWS AFTER:', rows_after)
conn.close()
