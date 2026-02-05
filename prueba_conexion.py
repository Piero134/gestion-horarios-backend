import psycopg2
import sys

# PON AQUÍ TUS DATOS EXACTOS
DB_HOST = "aws-0-us-east-1.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"
DB_USER = "postgres.qzeokekudwvrngddfvjv"
DB_PASS = "rRQAouhamBf1Ygbl"  # <--- CAMBIA ESTO

print(f"--- Intentando conectar a {DB_HOST} ---")

try:
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    print("✅ ¡ÉXITO! La conexión funciona perfectamente.")
    connection.close()
except Exception as e:
    print("\n❌ FALLO LA CONEXIÓN:")
    print(e)