from db import get_connection


def run_geometry_check():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO qa_runs (layer_name, status, triggered_by)
        VALUES (%s, %s, %s)
        RETURNING run_id;
    """, ('test_parcels', 'running', 'manual'))

    run_id = cur.fetchone()[0]

    conn.commit()

    cur.execute("""
        SELECT parcel_id, ST_IsValidReason(geom)
        FROM test_parcels
        WHERE NOT ST_IsValid(geom);    
    """)

    invalid_rows = cur.fetchall()

    rule_id = 1
    for row in invalid_rows:
        parcel_id = row[0]
        reason = row[1]

        cur.execute("""
            INSERT INTO qa_results (run_id, rule_id, feature_id, detail)
            VALUES (%s, %s, %s, %s);
        """, (run_id, rule_id, parcel_id, reason))

    cur.execute("""
        UPDATE qa_runs
        SET finished_at = now(), status = 'success'
        WHERE run_id = %s;
    """, (run_id,))

    conn.commit()

    cur.close()
    conn.close()

    print(f"Run {run_id} finished. Found {len(invalid_rows)} invalid geometries.")


if __name__ == "__main__":
    run_geometry_check()
