# GPT-4 Database Integration System

This project demonstrates how to integrate GPT-4 with a MySQL database using Python. The script accepts user prompts, retrieves responses from GPT-4 via Azure OpenAI, formats the responses, and stores them in a database. Additionally, the script allows users to retrieve the last stored entry from the database.

---

## Prerequisites

Before running the script, ensure the following tools and libraries are installed on your system:

1. **Python**: Version 3.8 or higher
2. **MySQL**: A MySQL server running locally or on a remote host
3. **Python Libraries**:
   - `openai`
   - `mysql-connector-python`

You can install the required Python libraries using:

```bash
pip install openai mysql-connector-python
```

4. **OpenAI API Credentials**: Ensure that you have valid API credentials.

---

## Step-by-Step Setup Guide

### 1. Install MySQL

#### For Windows:

1. Download the MySQL Installer from [MySQL Downloads](https://dev.mysql.com/downloads/).
2. Run the installer and select "MySQL Server" during installation.
3. Set a root password during configuration and remember it for later.

### 2. Configure MySQL

1. Log in to MySQL using the root user:

   ```bash
   mysql -u root -p
   ```

2. Enter the password when prompted.

3. Create a new database (if not already created by the script):

   ```sql
   CREATE DATABASE gpt4_db;
   ```
   Prefer to create using script.

### 3. Configure the Script

Update the `DB_CONFIG` dictionary in the script with your MySQL credentials:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",  # Replace with your MySQL username
    "password": "root@123",  # Replace with your MySQL password
    "database": "gpt4_db"
}
```

### 4. Configure the Tables Programmatically

You can programmatically create the necessary tables for the script using Python. Below is an example:

#### Code to Create Tables

```python
CREATE TABLE IF NOT EXISTS prompts_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

#### Running the Script

1. Save the above code to a file, such as `create_table.py`.
2. Run the script:

```bash
python create_table.py
```

This will create the `prompts_responses` table in your database.

---

### 5. Run the Script

1. Save the script as `your_script_name.py`.
2. Run the script using Python:
   ```bash
   python your_script_name.py
   ```
3. Enter a prompt when prompted. For example:
   ```
   Enter your prompt (or 'exit' to quit): What is Python?
   ```
4. The script will fetch the GPT-4 response, store it in the database, and display the stored data.

---

## Script Walkthrough

### Key Components

#### **Azure OpenAI API Configuration**

The following lines configure the Azure OpenAI API:

```python
OPENAI_API_KEY = "Your-API-Key"
AZURE_ENDPOINT = "Your-Endpoint-URL"
DEPLOYMENT_NAME = "gpt-4o"
```

#### **Database Initialization**

**Function**: `initialize_database`

This function:

- Connects to the MySQL server.
- Creates the database `gpt4_db` if it doesn’t already exist.
- Creates the `prompts_responses` table if it doesn’t already exist.

**Code:**

```python
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
```

#### **Formatting GPT-4 Response**

**Function**: `format_gpt_response`

This function:

- Cleans the response received from GPT-4.
- Removes unwanted markdown formatting.
- Ensures a clean, readable output.

**Code:**

```python
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
```

#### **Fetching GPT-4 Response**

**Function**: `get_gpt4_response`

This function:

- Sends the user prompt to Azure OpenAI.
- Retrieves and formats the GPT-4 response.

**Code:**

```python
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
```

#### **Storing Data in Database**

**Function**: `store_in_database`

This function:

- Saves the prompt and response to the MySQL database.
- Ensures the data is stored persistently.

**Code:**

```python
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
```

#### **Retrieve Last Entry**

**Function**: `retrieve_last_entry`

This function:

- Fetches the most recent entry in the `prompts_responses` table.
- Verifies data storage integrity.

**Code:**

```python
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
```

#### **Main Function**

**Function**: `main`

This function:

- Initializes the database.
- Repeatedly prompts the user for input until they choose to exit.
- Handles the interaction between the user, GPT-4 API, and database.

**Code:**

```python
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
```


---

## Troubleshooting

### Common Errors

1. **MySQL Connection Issues**:
   - Ensure the MySQL server is running.
   - Verify the credentials in `DB_CONFIG`.

2. **Module Not Found**:
   - Ensure all required Python libraries are installed.

3. **Access Denied for User**:
   - Check MySQL user permissions and password.

### Debugging Tips

- Use the `print()` statements in the script to trace errors.
- Test database connections manually using MySQL client:
  ```bash
  mysql -u root -p
  ```

---

## Usage Example

1. Run the script:
    ```bash
    python gpt4_integration.py
    ```
2. Enter a prompt (e.g., "What is the capital of France?").
3. View the formatted response and stored data.

Example Output:

```
[INFO] Connecting to Azure OpenAI API...
[SUCCESS] Response received in 1.23 seconds!
[INFO] Formatting GPT-4 response...
[SUCCESS] Response formatted successfully!
[INFO] Storing data in database...
[SUCCESS] Data stored successfully!

=== Stored Data ===
Prompt: What is the capital of France?
Response: The capital of France is Paris.
========================================
```

---

## Additional Notes

- Ensure API keys and sensitive information are not shared publicly.
- This script is designed for educational purposes and can be modified for specific use cases.

