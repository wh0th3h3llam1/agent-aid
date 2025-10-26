import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "AgentAid Need Agent",
    "https://located-instructors-driving-bright.trycloudflare.com",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key="eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NjE0NTk5NzEsImlhdCI6MTc2MTQ1NjM3MSwiaXNzIjoiZmV0Y2guYWkiLCJqdGkiOiI5NGE4MDYwOTQ5NzNhOWNkMDBkMWU1MDEiLCJzY29wZSI6IiIsInN1YiI6IjlhYzEwODJiZDk1Nzg3MjNiMTNkZDBkOTE1MDBmODQxNjk0ZjQ4NzQ4YzRhYjU1NCJ9.aVVYcTIAKOB7OLRRDEBc2iR7jdo9WFpI1u3Fh_AJuNmVCCj0liaTzQjWg4TwznXxJJsp4ingCZ6nyySbxaKZUW5NycZdbuRUcyCpGntyAdVzC5kwLupVAnIuQ8sC7j0B29wYEBYfGEiwOkY1Sfjh9oKZenK5dF75303d-y-mgmGpcygQmkEY7WR_LVS57VRL-MkPEh7rXKh9ZMtsC-CuRRlzL5SAZDD39Pmr50WKUiBfVJMbOun330y0BjpaUQjdGIHHFIN9yQfE8HMJIqmKK4PbwUn9MBj0GA0R_gl5WQTJIsiAiyaZjtulbUZhhDbpDxbQ5sJqfpmcKNg-O2Wtkg",
        agent_seed_phrase="8b8d6a47-f513-4c5d-a19a-1fec4d698d0b",
    ),
)
