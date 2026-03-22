# src/services/weather_service.py
import requests
from PyQt6.QtCore import QThread, pyqtSignal

class WeatherWorker(QThread):
    data_received = pyqtSignal(dict)
    
    def __init__(self, api_key, api_host): # <--- 新增 api_host 参数
        super().__init__()
        self.api_key = api_key
        self.api_host = api_host # 保存 Host

    def run(self):
        try:
            # 1. 获取位置 (保持不变)
            loc_resp = requests.get("http://ip-api.com/json/?lang=zh-CN", timeout=5)
            loc_data = loc_resp.json()
            if loc_data['status']!= 'success':
                raise Exception("定位失败")
            
            lat = loc_data['lat']
            lon = loc_data['lon']
            city_name = loc_data['city']

            # 2. 【关键修改】使用你的专属 API Host
            # 注意：这里把 devapi.qweather.com 换成了 self.api_host
            url = f"https://{self.api_host}/v7/weather/now?location={lon},{lat}&key={self.api_key}"
            
            weather_resp = requests.get(url, timeout=5)
            w_data = weather_resp.json()

            if w_data['code']!= '200':
                raise Exception(f"API错误: {w_data['code']}")

            result = {
                "temp": w_data['now']['temp'],
                "icon": w_data['now']['icon'],
                "text": w_data['now']['text'],
                "city": city_name
            }
            self.data_received.emit(result)

        except Exception as e:
            print(f"天气服务错误: {e}")
            self.data_received.emit({})