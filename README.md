# Multi AI

🤖AI，一次问多个！

[🔗 demo](https://multi-ai.ailln.com)

## Getting Start

### 1 添加配置

```yaml
llms:
  OpenAI:
    base_url: "https://api.openai.com/v1/"
    api_key: ""
    model_name: ""
  通义千问:
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1/"
    api_key: ""
    model_name: ""
```

### 2 安装依赖

```shell
pip install -r requirements.txt
```

### 3 运行服务

```shell
export no_proxy="localhost, 127.0.0.1, ::1"

python -m server.main
```

## Deploy

```shell
docker build -t multi-ai:1.0.0 .

docker run -d --restart=always --name multi-ai \
  -p 8000:8000 -v $PWD/conf:/app/conf -v $PWD/log:/app/log \
  -e multi-ai:1.0.0

docker logs -f multi-ai
```

## License

MIT

