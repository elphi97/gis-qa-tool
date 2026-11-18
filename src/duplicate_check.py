from db import get_connection


def run_duplicate_check():
    conn = get_connection()
    cur = conn.cursor()

    # KROK A: nowy przebieg w qa_runs, status 'running'
    cur.execute("""
        INSERT INTO qa_runs (layer_name, status, triggered_by)
        VALUES (%s, %s, %s)
        RETURNING run_id;
    """, ('test_parcels', 'running', 'manual'))

    run_id = cur.fetchone()[0]
    conn.commit()

    # KROK B: znajdź pary duplikatów (self-join z Kroku 5.2)
    cur.execute("""
        SELECT a.parcel_id, b.parcel_id
        FROM test_parcels a
        JOIN test_parcels b ON ST_Equals(a.geom, b.geom)
        WHERE a.parcel_id < b.parcel_id;    -- LUKA 1: ten sam warunek co w Kroku 5.2
    """)

    duplicate_pairs = cur.fetchall()   # LUKA 2: wszystkie wiersze, nie jeden

    # KROK C: dla każdej pary - DWA inserty do qa_results
    cur.execute("SELECT rule_id FROM qa_rules WHERE rule_name = %s;", ('duplicate_geometry_checker',))
    rule_id = cur.fetchone()[0]

    for pair in duplicate_pairs:
        id_a = pair[0]
        id_b = pair[1]

        # pierwszy wiersz: feature_id = id_a, wskazuje na id_b
        cur.execute("""
            INSERT INTO qa_results (run_id, rule_id, feature_id, detail)
            VALUES (%s, %s, %s, %s);
        """, (run_id, rule_id, id_a, f"Duplicate of parcel_id {id_b}"))
        # LUKA 3: które id wstawiamy tutaj do f-stringa?

        # drugi wiersz: feature_id = id_b, wskazuje na id_a
        cur.execute("""
            INSERT INTO qa_results (run_id, rule_id, feature_id, detail)
            VALUES (%s, %s, %s, %s);
        """, (run_id, rule_id, id_b, f"Duplicate of parcel_id {id_a}"))
        # LUKA 4 i 5: feature_id oraz id w f-stringu dla DRUGIEGO wiersza

    # KROK D: zamknij przebieg
    cur.execute("""
        UPDATE qa_runs
        SET finished_at = now(), status = 'success'
        WHERE run_id = %s;
    """, (run_id,))

    conn.commit()
    cur.close()
    conn.close()

    print(f"Run {run_id} finished. Found {len(duplicate_pairs)} duplicate pairs "
          f"({len(duplicate_pairs) * 2} result rows).")


if __name__ == "__main__":
    run_duplicate_check()