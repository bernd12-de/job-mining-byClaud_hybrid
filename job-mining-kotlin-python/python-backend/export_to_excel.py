import psycopg2
import csv
from datetime import datetime

def export_job_mining_data():
    # Zugangsdaten basierend auf deiner docker-compose.yml
    db_config = {
        "dbname": "jobmining_db",
        "user": "jobmining_user",
        "password": "secret_password",
        "host": "localhost", # Falls du es lokal ausführst, sonst der Container-Name
        "port": "5432"
    }

    output_file = f"masterarbeit_auswertung_{datetime.now().strftime('%Y%m%d')}.csv"

    # SQL für die longitudinale Auswertung
    # Verknüpft Jobs mit Kompetenzen und extrahiert das Jahr für die Zeitreihe
    query = """
            SELECT
                j.id as job_id,
                j.title,
                j.job_role,
                j.industry,
                j.region,
                j.posting_date,
                EXTRACT(YEAR FROM j.posting_date) as jahr,
                c.esco_label,
                c.esco_uri,
                c.original_term,
                c.is_digital,
                c.level,
                c.is_discovery,
                c.source_domain,
                c.role_context
                c.confidence_score
            FROM job_posting j
                     LEFT JOIN competence c ON j.id = c.job_posting_id
            ORDER BY j.posting_date DESC; \
            """

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]

        # Die Spaltennamen werden automatisch aus dem Query übernommen
        colnames = [desc[0] for desc in cur.description]

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';') # Semikolon für direkten Excel-Import
            writer.writerow(colnames)
            writer.writerows(rows)

        print(f"✅ Erfolg! {len(rows)} Datensätze wurden nach '{output_file}' exportiert.")
        print("💡 Du kannst diese Datei jetzt direkt in Excel öffnen.")

    except Exception as e:
        print(f"❌ Fehler beim Datenbank-Export: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    export_job_mining_data()
