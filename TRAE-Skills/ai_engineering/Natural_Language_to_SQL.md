# Skill: Natural Language to SQL (NL2SQL)

## Purpose
To build systems that convert natural language questions into executable SQL queries, enabling non-technical users to interact with databases.

## When to Use
- When building analytics dashboards for business users
- For customer support tools that query databases directly
- When implementing internal tools for non-technical teams
- For data exploration applications
- When building chatbots that need database access

## Procedure

### 1. Simple NL2SQL with OpenAI
Use LLMs to generate SQL from natural language.

```python
import openai
import sqlite3

client = openai.OpenAI(api_key="your-api-key")

def nl_to_sql(question, table_schema):
    prompt = f"""Given the following table schema:
{table_schema}

Generate a SQLite SQL query to answer this question: {question}

Only return the SQL query, no explanation.
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

# Example usage
table_schema = """
Table: users
- id: INTEGER
- name: TEXT
- email: TEXT
- created_at: DATE
- status: TEXT (active, inactive)

Table: orders
- id: INTEGER
- user_id: INTEGER
- total_amount: DECIMAL
- order_date: DATE
- status: TEXT (pending, completed, cancelled)
"""

question = "Show me all active users who placed orders over $100 in 2024"
sql_query = nl_to_sql(question, table_schema)
print(sql_query)
```

### 2. Execute Query Safely
Execute the generated SQL with safety checks.

```python
def execute_safe_query(db_path, sql):
    # Safety checks
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'INSERT', 'UPDATE', 'CREATE']
    for keyword in dangerous_keywords:
        if keyword.upper() in sql.upper():
            raise Exception(f"Query contains forbidden operation: {keyword}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()
    
    return {"columns": columns, "results": results}

# Usage
try:
    result = execute_safe_query("mydb.sqlite", sql_query)
    print("Columns:", result["columns"])
    print("Results:", result["results"])
except Exception as e:
    print("Error:", e)
```

### 3. Few-Shot Learning Examples
Improve accuracy with few-shot examples.

```python
few_shot_examples = """
Example 1:
Question: How many users are there?
SQL: SELECT COUNT(*) FROM users;

Example 2:
Question: Show users who signed up in 2024
SQL: SELECT * FROM users WHERE created_at >= '2024-01-01';

Example 3:
Question: What's the total revenue from completed orders?
SQL: SELECT SUM(total_amount) FROM orders WHERE status = 'completed';
"""

def nl_to_sql_with_examples(question, table_schema):
    prompt = f"""Given the following table schema:
{table_schema}

Examples:
{few_shot_examples}

Generate a SQLite SQL query to answer this question: {question}
Only return the SQL query.
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()
```

### 4. Using LangChain for NL2SQL
Use LangChain's SQL database chain.

```python
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

db = SQLDatabase.from_uri("sqlite:///mydb.sqlite")
llm = ChatOpenAI(model="gpt-4", temperature=0)
chain = create_sql_query_chain(llm, db)

question = "Show me the top 5 users by total order amount"
response = chain.invoke({"question": question})
print(response)
```

## Best Practices
- **Whitelist Operations**: Only allow SELECT queries in production
- **Schema Context**: Always provide clear table schema information
- **Validation**: Validate generated queries before execution
- **Few-Shot Learning**: Use examples to improve accuracy
- **Error Handling**: Gracefully handle query generation failures
- **Sanitize Inputs**: Prevent SQL injection even from generated queries
- **Log Everything**: Log questions, queries, and results for debugging
