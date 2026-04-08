from langgraph.checkpoint.sqlite import SqliteSaver

# Persistent state across calls per thread_id
# This will create/use a local SQLite file `state.db`
checkpointer = SqliteSaver.from_conn_string("sqlite:///state.db")

