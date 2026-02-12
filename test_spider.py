import requests
import json
import os
from datetime import datetime

def test_fetch():
    url = "https://www.cls.cn/telegraph"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"正在测试抓取: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    
    html_content = response.text
    start_marker = '<script id="__NEXT_DATA__" type="application/json">'
    end_marker = '</script>'
    
    start_idx = html_content.find(start_marker)
    if start_idx == -1:
        print("错误: 未找到 __NEXT_DATA__")
        return
    
    start_idx += len(start_marker)
    end_idx = html_content.find(end_marker, start_idx)
    json_str = html_content[start_idx:end_idx]
    data = json.loads(json_str)
    
    telegraph_list = data['props']['initialState']['telegraph']['telegraphList']
    print(f"成功抓取到 {len(telegraph_list)} 条新闻")
    
    # 模拟保存
    date_str = datetime.now().strftime('%Y-%m-%d')
    hour_str = datetime.now().strftime('%H')
    dir_path = os.path.join(os.getcwd(), 'test_output', date_str)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    file_path = os.path.join(dir_path, f"{hour_str}.json")
    
    news_items = []
    for item in telegraph_list[:5]: # 只取前5条做测试
        news_items.append({
            "id": item.get('id'),
            "title": item.get('title'),
            "content": item.get('content'),
            "time_str": datetime.fromtimestamp(item.get('ctime')).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(news_items, f, ensure_ascii=False, indent=4)
    
    print(f"测试数据已保存至: {file_path}")
    print("前两条新闻内容预览:")
    for item in news_items[:2]:
        print(f"- {item['time_str']} | {item['title']}")

if __name__ == "__main__":
    test_fetch()
