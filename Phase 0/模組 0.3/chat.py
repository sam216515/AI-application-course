from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError
import os, time, random

load_dotenv()

messages = []

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def try_call(max_tries = 3):
    for i in range(max_tries):
        output = ""
        try:
            with client.chat.completions.create(
                model="baidu/cobuddy:free",
                messages= messages,
                stream= True
            ) as stream:
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        print(delta, end="", flush=True)
                        output += delta
                messages.append({"role": "assistant", "content": output})
                return output

        except APIStatusError as e:
            if e.status_code == 429 or e.status_code >= 500:
                wait = 2**i + random.uniform(0,1)
                time.sleep(wait)
            else:
                raise
        except APIConnectionError:
            wait = 2**i + random.uniform(0,1)
            time.sleep(wait)
            
    raise RuntimeError("已達最大重試次數，API 呼叫失敗")


if __name__ == "__main__":
    while True:
        try:
            user_input = input("請輸入：").strip()
        except KeyboardInterrupt:
            print("\n再見！")
            break
        if user_input.lower() == "quit":
            break
        elif not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        try_call()
        print()