import psycopg2
import os

url = "postgresql://postgres.iubicmwwjmpnwsabzdvb:wURAWFF7jTIzCPqS@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"  # use your real URL
conn = psycopg2.connect(url)
print("Connected!")
conn.close()