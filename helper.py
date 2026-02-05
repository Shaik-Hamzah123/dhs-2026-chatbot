# from langchain_core.tools import StructuredTool
# from mem0 import MemoryClient
# from pydantic import BaseModel, Field
# from typing import List, Dict, Any, Optional
# import os

# client = MemoryClient(
#     api_key=os.getenv("MEM0_API_KEY")
# )

# class Message(BaseModel):
#     role: str = Field(description="Role of the message sender (user or assistant)")
#     content: str = Field(description="Content of the message")

# class AddMemoryInput(BaseModel):
#     messages: List[Message] = Field(description="List of messages to add to memory")
#     user_id: str = Field(description="ID of the user associated with these messages")
#     metadata: Optional[Dict[str, Any]] = Field(description="Additional metadata for the messages", default=None)

#     class Config:
#         json_schema_extra = {
#             "examples": [{
#                 "messages": [
#                     {"role": "user", "content": "Hi, I'm Alex. I'm a vegetarian and I'm allergic to nuts."},
#                     {"role": "assistant", "content": "Hello Alex! I've noted that you're a vegetarian and have a nut allergy."}
#                 ],
#                 "user_id": "alex",
#                 "metadata": {"food": "vegan"}
#             }]
#         }

# def add_memory(messages: List[Message], user_id: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
#     """Add messages to memory with associated user ID and metadata."""
#     message_dicts = [msg.dict() for msg in messages]
#     return client.add(message_dicts, user_id=user_id, metadata=metadata)

# add_tool = StructuredTool(
#     name="add_memory",
#     description="Add new messages to memory with associated metadata",
#     func=add_memory,
#     args_schema=AddMemoryInput
# )

# class SearchMemoryInput(BaseModel):
#     query: str = Field(description="The search query string")
#     filters: Dict[str, Any] = Field(description="Filters to apply to the search")

#     class Config:
#         json_schema_extra = {
#             "examples": [{
#                 "query": "tell me about my allergies?",
#                 "filters": {
#                     "AND": [
#                         {"user_id": "alex"},
#                         {"created_at": {"gte": "2024-01-01", "lte": "2024-12-31"}}
#                     ]
#                 }
#             }]
#         }

# def search_memory(query: str, filters: Dict[str, Any]) -> Any:
#     """Search memory with the given query and filters."""
#     return client.search(query=query, filters=filters)

# search_tool = StructuredTool(
#     name="search_memory",
#     description="Search through memories with a query and filters",
#     func=search_memory,
#     args_schema=SearchMemoryInput
# )