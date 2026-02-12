import requests
import json
import time
import os
import hashlib
from datetime import datetime

class CLSSpider:
    def __init__(self):
        self.url = "https://www.cls.cn/telegraph"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.news_data = []  # 存储当天已抓取的新闻
        self.seen_ids = set() # 存储已抓取的新闻 ID，防止重复

    def fetch_latest_news(self):
        """抓取最新的快讯数据"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"[{datetime.now()}] 抓取失败，状态码: {response.status_code}")
                return []
            
            # 从 HTML 中提取 __NEXT_DATA__
            html_content = response.text
            start_marker = '<script id="__NEXT_DATA__" type="application/json">'
            end_marker = '</script>'
            
            start_idx = html_content.find(start_marker)
            if start_idx == -1:
                print(f"[{datetime.now()}] 未找到 __NEXT_DATA__")
                return []
            
            start_idx += len(start_marker)
            end_idx = html_content.find(end_marker, start_idx)
            
            json_str = html_content[start_idx:end_idx]
            data = json.loads(json_str)
            
            # 解析新闻列表
            try:
                telegraph_list = data['props']['initialState']['telegraph']['telegraphList']
            except KeyError:
                print(f"[{datetime.now()}] JSON 结构解析失败")
                return []
            
            new_items = []
            for item in telegraph_list:
                item_id = item.get('id')
                if item_id and item_id not in self.seen_ids:
                    news_item = {
                        "id": item_id,
                        "title": item.get('title'),
                        "content": item.get('content'),
                        "ctime": item.get('ctime'),
                        "time_str": datetime.fromtimestamp(item.get('ctime')).strftime('%Y-%m-%d %H:%M:%S') if item.get('ctime') else "N/A"
                    }
                    new_items.append(news_item)
                    self.seen_ids.add(item_id)
            
            return new_items
        except Exception as e:
            print(f"[{datetime.now()}] 抓取过程中发生异常: {str(e)}")
            return []

    def save_to_file(self):
        """每小时保存一次数据"""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        hour_str = now.strftime('%H')
        
        # 创建日期文件夹
        dir_path = os.path.join(os.getcwd(), date_str)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            # 跨天重置
            self.news_data = []
            self.seen_ids = set()
            print(f"[{now}] 进入新的一天，重置数据缓存")

        file_name = f"{hour_str}.json"
        file_path = os.path.join(dir_path, file_name)
        
        # 按照 ctime 排序，确保新闻顺序正确（最新的在后面或前面，这里按时间顺序排列）
        self.news_data.sort(key=lambda x: x['ctime'])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.news_data, f, ensure_ascii=False, indent=4)
        
        print(f"[{now}] 数据已保存至: {file_path}, 当前累计新闻数: {len(self.news_data)}")

    def run(self):
        """主循环"""
        print(f"[{datetime.now()}] 财联社快讯爬虫已启动...")
        
        # 初始抓取，填充已有的新闻
        initial_news = self.fetch_latest_news()
        if initial_news:
            self.news_data.extend(initial_news)
            print(f"[{datetime.now()}] 初始抓取完成，加载了 {len(initial_news)} 条新闻")
        
        last_save_hour = datetime.now().hour
        
        while True:
            try:
                now = datetime.now()
                
                # 1. 每分钟请求一次
                new_news = self.fetch_latest_news()
                if new_news:
                    self.news_data.extend(new_news)
                    # 按照 ctime 排序，确保新闻顺序正确
                    self.news_data.sort(key=lambda x: x['ctime'])
                    print(f"[{now}] 发现 {len(new_news)} 条新快讯，当前总数: {len(self.news_data)}")
                else:
                    print(f"[{now}] 轮询中：暂无新快讯")
                
                # 2. 每小时保存一次 (当小时数改变时)
                if now.hour != last_save_hour:
                    self.save_to_file()
                    last_save_hour = now.hour
                
                # 3. 等待 60 秒
                time.sleep(60)
            except KeyboardInterrupt:
                print(f"[{datetime.now()}] 爬虫已手动停止。")
                self.save_to_file() # 退出前保存一次
                break
            except Exception as e:
                print(f"[{datetime.now()}] 运行出错: {e}")
                time.sleep(10)

if __name__ == "__main__":
    spider = CLSSpider()
    # 为了演示方便，你可以手动调用一次 save_to_file 来查看效果
    # spider.save_to_file() 
    spider.run()
