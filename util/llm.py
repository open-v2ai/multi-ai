import asyncio

from openai import AsyncOpenAI

from util.conf import get_conf
from util.log import get_logger

conf = get_conf()
logger = get_logger()

# 创建客户端字典
clients = {}
for llm_name, llm_conf in conf["llms"].items():
    clients[llm_name] = AsyncOpenAI(base_url=llm_conf["base_url"], api_key=llm_conf["api_key"])

async def call_llm(name: str, message: str, stream: bool = True):
    """统一的异步LLM调用接口，支持流式输出"""
    try:
        if name not in conf["llms"].keys():
            raise ValueError(f"未知的LLM名称: {name}")
        
        client = clients[name]
        model = conf["llms"][name]["model_name"]
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            stream=stream,
            temperature=0.7,
            max_tokens=1000
        )
        
        if stream:
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            yield response.choices[0].message.content
            
    except Exception as e:
        error_msg = f"调用{name}出错: {str(e)}"
        logger.info(error_msg)
        yield error_msg

async def test_llm():
    """测试函数"""
    message = "你好，你是谁？"
    
    for name in conf["llms"].keys():
        logger.info(f"测试LLM: {name}")
        print(f"Q: {message}")
        try:
            print("A: ", end="")
            async for chunk in call_llm(name, message):
                print(chunk, end="", flush=True)
        except Exception as e:
            logger.info(f"错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_llm())
