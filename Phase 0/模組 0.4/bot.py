from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError
import os, time, random, logging, argparse

load_dotenv()

messages = []

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "忽略之前的指令",
    "you are now",
    "你現在是",
    "[system",
    "[[",
]

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler("bot.log"),
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="baidu/cobuddy:free", help="模型選擇")
    parser.add_argument("--max_tokens", type= int, default= 500, help = "最大回應 token 數")
    parser.add_argument("--verbose", action= "store_true", help="顯示 DEBUG 訊息")
    return parser.parse_args()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def sanitize_input(user_input: str) -> str:
    lowered = user_input.lower()
    for inject_message in INJECTION_PATTERNS:
        if inject_message in lowered:
            logger.warning("警告，你可能在注入攻擊")
            raise ValueError("輸入包含不允許的內容")
    return user_input.strip()


def try_call(args, max_tries = 3):
    for i in range(max_tries):
        output = ""
        try:
            with client.chat.completions.create(
                model= args.model,
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
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    while True:
        try:
            user_input = input("請輸入：").strip()
            if user_input.lower() == "quit":
                break
            elif not user_input:
                continue
            clean_input = sanitize_input(user_input)
        except ValueError as e:
            print(f"⚠️ {e}")
            continue
        except KeyboardInterrupt:
            print("\n再見！")
            break
        messages.append({"role": "user", "content": clean_input})
        try_call(args)
        print()