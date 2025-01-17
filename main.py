import os
from openai import AzureOpenAI # type: ignore
import mysql.connector # type: ignore
import re
import time

# Azure OpenAI API Configuration
OPENAI_API_KEY = "Your-API-Key"
AZURE_ENDPOINT = "Your-Target-Name"
DEPLOYMENT_NAME = "gpt-4o"

DB_CONFIG = {
    "host": "localhost",
    "user": "root", #Your Database username generally "root"
    "password": "Your-MySql-Password",
    "database": "Your-Database-Name"
}

def initialize_database():
    print("\n[INFO] Initializing database connection...")
    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS gpt4_db")
    cursor.execute("USE gpt4_db")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompts_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL
        )
    """)
    cursor.close()
    connection.close()
    print("[SUCCESS] Database initialized successfully!\n")

def format_gpt_response(response):
    print("[INFO] Formatting GPT-4 response...")
    if not response:
        return response
    # Clean markdown formatting
    replacements = [
        (r'\*\*(.*?)\*\*', r'\1'),           # Bold
        (r'\*(.*?)\*', r'\1'),               # Italic
        (r'^\d+\.\s+', ''),                  # Numbered lists
        (r'^\s*[-•]\s+', ''),                # Bullet points
        (r'```(?:\w+)?\n(.*?)```', r'\1'),   # Code blocks
        (r'`(.*?)`', r'\1'),                 # Inline code
        (r'\n{3,}', '\n\n')                  # Multiple newlines
    ]
    
    for pattern, replacement in replacements:
        response = re.sub(pattern, replacement, response, flags=re.MULTILINE|re.DOTALL)
    
    formatted_response = '\n'.join(line.strip() for line in response.split('\n')).strip()
    print("[SUCCESS] Response formatted successfully!")
    return formatted_response

def get_gpt4_response(prompt):
    print("\n[INFO] Connecting to Azure OpenAI API...")
    client = AzureOpenAI(
        api_key=OPENAI_API_KEY,
        api_version="2024-08-01-preview",
        azure_endpoint=AZURE_ENDPOINT
    )
    
    print("[INFO] Sending request to GPT-4...")
    start_time = time.time()
    
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    end_time = time.time()
    print(f"[SUCCESS] Response received in {end_time - start_time:.2f} seconds!")
    
    return format_gpt_response(response.choices[0].message.content.strip())

def store_in_database(prompt, response):
    print("\n[INFO] Storing data in database...")
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    cursor.execute(
        "INSERT INTO prompts_responses (prompt, response) VALUES (%s, %s)", 
        (prompt, response)
    )
    
    connection.commit()
    cursor.close()
    connection.close()
    print("[SUCCESS] Data stored successfully!")

def retrieve_last_entry():
    print("\n[INFO] Retrieving last entry from database...")
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM prompts_responses ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    print("[SUCCESS] Entry retrieved successfully!")
    return result

def main():
    print("\n=== GPT-4 Database Integration System ===")
    initialize_database()
    
    while True:
        print("\n" + "="*40)
        prompt = input("Enter your prompt (or 'exit' to quit): ")
        if prompt.lower() == "exit":
            print("\n[INFO] Exiting program...")
            print("Goodbye!")
            break
        
        response = get_gpt4_response(prompt)
        if response:
            store_in_database(prompt, response)
            result = retrieve_last_entry()
            
            if result:
                print("\n=== Stored Data ===")
                print(f"Prompt: {result[1]}")
                print(f"Response: {result[2]}")
                print("=" * 40 + "\n")

if __name__ == "__main__":
    main()