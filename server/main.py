import asyncio

import gradio as gr

from util.conf import get_conf
from util.log import get_logger
from util.llm import call_llm

logger = get_logger("server.main")
conf = get_conf()

async def process(question):
    logger.info(question)

    """处理分析请求的主函数"""
    llm_len = len(conf["llms"])
    try:
        # 创建初始结果列表
        results = ["" for _ in range(llm_len)]

        async def process_single_model(model, index):
            """处理单个模型的响应"""
            try:
                async for chunk in call_llm(model, question):
                    results[index] += chunk
                    # 每次有新内容时都产生一个新的结果列表
                    yield results.copy()
            except Exception as e:
                results[index] = f"错误: {str(e)}"
                yield results.copy()

        # 创建并发任务
        tasks = []
        for index, llm_name in enumerate(conf["llms"].keys()):
            generator = process_single_model(llm_name, index)
            task = asyncio.create_task(generator.__anext__())
            tasks.append((task, generator))

        # 处理所有响应
        while tasks:
            # 等待任意一个任务完成
            done, _ = await asyncio.wait([t[0] for t in tasks], return_when=asyncio.FIRST_COMPLETED)
            
            # 处理完成的任务
            for completed_task in done:
                for i, (task, generator) in enumerate(tasks):
                    if task == completed_task:
                        try:
                            # 获取结果
                            await completed_task
                            # 创建新的任务继续处理该生成器
                            new_task = asyncio.create_task(generator.__anext__())
                            tasks[i] = (new_task, generator)
                            # 产生当前结果
                            yield results.copy()
                            break
                        except StopAsyncIteration:
                            # 如果生成器完成，从任务列表中移除
                            tasks.pop(i)
                            break
                        except Exception as e:
                            print(f"Error processing task: {str(e)}")
                            tasks.pop(i)
                            break

        # 返回结果
        yield results.copy()

    except Exception as e:
        error_msg = f"解答过程出错: {str(e)}"
        print(error_msg)

        yield [error_msg] * llm_len

# 创建 Gradio 界面 theme="NoCrypt/miku"
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 AI智囊团")

    with gr.Row():
        question = gr.Textbox(
            label="问题",
            value="给我讲一个笑话吧",
            scale=3
        )
        send_button = gr.Button("为朕分忧", variant="primary", scale=1)

    with gr.Row():
        for index, name in enumerate(conf["llms"].keys()):
            gr.Markdown(f"## {index+1} {name}")

    with gr.Row():
        llm_output_list = []
        for _ in conf["llms"].keys():
            llm_output = gr.Markdown("", height=600)
            llm_output_list.append(llm_output)

    send_button.click(
        process,
        inputs=[question],
        outputs=llm_output_list,
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch(debug=True, server_name="0.0.0.0", server_port=8000)
