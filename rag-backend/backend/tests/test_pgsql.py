from psycopg_pool import ConnectionPool
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    db_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DATABASE", "rag_checkpoint"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "123456")
        }
    # 创建数据库连接字符串
    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    print(connection_string)
    with (
    PostgresStore.from_conn_string(connection_string) as store,
    PostgresSaver.from_conn_string(connection_string) as checkpointer,
):
        # store.setup()
        # checkpointer.setup()
        # print("setup done")
        
        user_id = "test_user_000"
        namespace = ("memories", user_id)
        memories = store.search(namespace)
        
        if memories:
            print("✅ 记忆存储成功！")
            print(memories)

