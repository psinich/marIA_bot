from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  #extra_headers={
  #  "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
  #  "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  #},
  extra_body={},
  model="google/gemini-2.0-flash-thinking-exp:free",
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Расскажи про себя?"
        }
      ]
    }
  ]
)
print(completion.choices[0].message.content)
