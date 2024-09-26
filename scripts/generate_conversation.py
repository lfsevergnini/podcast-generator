import openai

def generate_conversation(resources, speaker1, speaker2, num_turns=10):
    prompt = (
        f"Create a conversation between {speaker1} and {speaker2} based on the following resources:\n"
        f"{resources}\n\nConversation:\n"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates realistic conversations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )
    conversation = response.choices[0].message['content']
    return conversation

if __name__ == "__main__":
    with open('resources/input_resources.txt', 'r') as file:
        resources = file.read()

    conversation = generate_conversation(resources, "Alice", "Bob")
    with open('output/conversation.txt', 'w') as file:
        file.write(conversation)
