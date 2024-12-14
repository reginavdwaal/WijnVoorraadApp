import openai

# Stel je API-sleutel in
openai.api_key = "jouw-api-sleutel"
print(openai.__version__)  # Moet '1.57.2' tonen

# Aanroep naar de ChatCompletion API
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What wine is in this image?"}],
    max_tokens=300,
)

print(response)
