from history import ChatHistoryManager

db = ChatHistoryManager()

cid = db.create_conversation("Testing")

db.add_message(cid, "user", "Hello")

db.add_message(cid, "assistant", "Hi!")

print(db.get_conversations())

print(db.get_messages(cid))