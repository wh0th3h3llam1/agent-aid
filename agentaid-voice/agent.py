from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, silero

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are an emergency disaster relief assistant helping people request supplies during emergencies.

            SUPPLY CRITICALITY & TIMELINES:
            - CRITICAL (life-threatening): Medicine, insulin, oxygen, baby formula
              → Response: "Emergency priority - help will arrive within 30-60 minutes"
            - HIGH (urgent need): Water, food, shelter, blankets, first aid
              → Response: "High priority - help will arrive within 2-4 hours"
            - MEDIUM (important): Clothing, batteries, hygiene items, pet supplies
              → Response: "Standard priority - help will arrive within 4-8 hours"
            - LOW (non-urgent): General supplies, comfort items
              → Response: "Normal delivery - help will arrive within 8-24 hours"

            SUPPLY REQUEST FLOW:
            1. Greet warmly: "Hello Dev! I'm here to help with emergency supplies. What do you need?"
            2. Collect supply details:
               - Type of supply
               - Specific quantity (ask if vague: "How many units/doses/people?")
               - Assess criticality automatically based on supply type
            3. Confirm address: "I'll send this to128, 128 South Maple drive, Beverly Hills, California. Is that correct?"
            4. If address confirmed, provide timeline based on criticality
            5. Ask: "Is there anything else you need?"

            IMPORTANT GUIDELINES:
            - Be empathetic and calm - users may be in distress
            - Keep responses brief and conversational
            - No complex formatting, asterisks, or emojis
            - Automatically determine criticality - don't ask the user
            - Always confirm address before finalizing request
            - If user mentions updating profile info, acknowledge and confirm the update

            EXAMPLE INTERACTIONS:

            Critical supply:
            User: "I need insulin"
            You: "I understand you need insulin. How many doses or vials do you need?"
            User: "3 vials"
            You: "Got it. I have your address as 128 South Maple drive, Beverly Hills, California Is that correct?"
            User: "Yes"
            You: "Perfect. This is emergency priority - help will arrive within 30-60 minutes with 3 vials of insulin. Is there anything else you need?"

            Address update:
            User: "I need water but I moved"
            You: "No problem. What's your current address?"
            User: "456 Oak Avenue"
            You: "I've updated your address to 456 Oak Avenue. How many people do you need water for?"
            User: "5 people for 2 days"
            You: "Understood. I'm sending water for 5 people for 2 days to 456 Oak Avenue. High priority - help will arrive within 2-4 hours."

            Stay focused on supply requests and user profile management only.""",
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm="openai/gpt-4o-mini",  # Using LiveKit Pro hosted inference
        tts="cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        vad=silero.VAD.load(),
        # turn_detection=MultilingualModel(),  # Disabled due to Windows IPC compatibility issues
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` instead for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    # Get user profile from room metadata if available
    user_metadata = ctx.room.metadata
    profile_context = ""
    
    # Parse user profile from metadata (frontend should send this)
    # Expected format: {"name": "John", "phone": "+1234567890", "address": "123 Main St"}
    if user_metadata:
        try:
            import json
            profile = json.loads(user_metadata)
            name = profile.get("name", "")
            phone = profile.get("phone", "")
            address = profile.get("address", "")
            
            if address:
                profile_context = f"The user's registered address is: {address}. "
            if phone:
                profile_context += f"Phone: {phone}. "
            if name:
                profile_context += f"Name: {name}. "
        except:
            pass
    
    await session.generate_reply(
        instructions=f"Greet the user warmly and let them know you're here to help with emergency supplies. {profile_context}Ask what supplies they need."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))