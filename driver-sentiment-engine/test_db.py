from app.config import supabase

def test_connection():
    try:
        response = supabase.table("driver_sentiment").select("*").limit(1).execute()
        print("✅ Connection successful!")
        print("Response:", response.data)
    except Exception as e:
        print("❌ Connection failed!")
        print("Error:", e)

if __name__ == "__main__":
    test_connection()