import openai
from settings import GPT_TOKEN

openai.api_key = GPT_TOKEN
model_engine = "gpt-3.5-turbo"


async def get_gpt3_response(prompt, history=None):
    messages = [{"role": "system", "content": 'You are GptMagicianBot. Якщо тобі зададуть питання на російській мові, відповідай українською мовою.'}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    response = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo',
        messages=messages,
        max_tokens=2048,
        temperature=0,
    )

    return response.choices[-1].message.content
