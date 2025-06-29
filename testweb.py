import requests

# 使用params参数传递查询参数
base_url = "http://localhost:2403"
params = {
    "url": "https://github.3x25.com/https://raw.githubusercontent.com/wumingshiali/md2docx-gui/master/README.md"
}

# 发送GET请求
requests.get(url=base_url, params=params)