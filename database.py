import psycopg2
from psycopg2 import Error

# Konfigurasi Database (SESUAIKAN DENGAN PUNYAMU)
DB_HOST = "localhost"
DB_NAME = "churn"      
DB_USER = "postgres"       
DB_PASS = "lankocak" 
DB_PORT = "5432"

def create_connection():
    """Membuat koneksi ke database PostgreSQL"""
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        return connection
    except (Exception, Error) as error:
        print("Error saat koneksi ke PostgreSQL:", error)
        return None

def save_to_db(tenure, monthly, total, gender, contract, pred_result, pred_proba):
    """Menyimpan data input dan hasil prediksi ke tabel"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO prediction_history 
            (tenure, monthly_charges, total_charges, gender, contract, prediction_result, prediction_proba)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Eksekusi Query
            cursor.execute(query, (tenure, monthly, total, gender, contract, pred_result, pred_proba))
            connection.commit() # Simpan perubahan permanen
            print("Data berhasil disimpan ke Database!")
        except (Exception, Error) as error:
            print("Gagal menyimpan data:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()