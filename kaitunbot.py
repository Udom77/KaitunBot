import asyncio
import discord
import json
from difflib import get_close_matches
from dotenv import load_dotenv  # To load token securely


TOKEN = "MTM0MzEyMDY4MzM4Mjg2NjA4Mw.GhRIah.VMzPZ3hCy2hUe0-_GUNaMB6UEhB8nENodKMDEA"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def load_knowledge_base(file_path: str) -> dict:
    """Loads knowledge base from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"questions": []}


def save_knowledge_base(file_path: str, data: dict):
    """Saves knowledge base to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def find_best_match(user_question: str, questions: list[str]) -> str | None:
    """Finds the best match for the user question."""
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    """Gets the answer for a specific question."""
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None


@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore bot's own messages

    knowledge_base = load_knowledge_base("knowledge_base.json")
    user_input = message.content

    best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        await message.channel.send(answer)
    else:
        await message.channel.send("I don't know the answer. Can you teach me? Reply with `**answer`. If I ask twice by error, please ignore me.")

        # Wait for the user's response
        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.startswith("**")

        try:
            response = await client.wait_for("message", check=check,)
            new_answer = response.content[2:]  # Remove "**" from the message

            if new_answer:
                knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                save_knowledge_base("knowledge_base.json", knowledge_base)
                await message.channel.send("Thank you! I've learned a new response.")
        except asyncio.TimeoutError:
            pass

client.run(TOKEN)
