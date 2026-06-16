# src/services/weather_service.py
import requests
from PyQt6.QtCore import QThread, pyqtSignal


class WeatherWorker(QThread):
    data_received = pyqtSignal(dict)

    def __init__(self, api_key, api_host):
        super().__init__()
        self.api_key = api_key
        self.api_host = api_host

    def run(self):
        try:
            if not self.api_key or not self.api_host:
                raise ValueError("天气 API 配置缺失")

            loc_resp = requests.get("http://ip-api.com/json/?lang=zh-CN", timeout=5)
            loc_data = self._read_json_response(loc_resp, "定位服务")
            if loc_data.get("status") != "success":
                raise ValueError(f"定位失败: {loc_data.get('message', loc_data.get('status'))}")

            lat = loc_data.get("lat")
            lon = loc_data.get("lon")
            city_name = loc_data.get("city") or "未知位置"
            if lat is None or lon is None:
                raise ValueError("定位服务缺少经纬度")

            url = f"https://{self.api_host}/v7/weather/now?location={lon},{lat}&key={self.api_key}"
            weather_resp = requests.get(url, timeout=5)
            w_data = self._read_json_response(weather_resp, "天气服务")

            if w_data.get("code") != "200":
                raise ValueError(f"API错误: {w_data.get('code')}")

            now_data = w_data.get("now") or {}
            temp = now_data.get("temp")
            icon = now_data.get("icon")
            text = now_data.get("text")
            if temp is None or not icon or not text:
                raise ValueError("天气服务缺少 now.temp/icon/text")

            result = {
                "temp": temp,
                "icon": icon,
                "text": text,
                "city": city_name,
                "available": True,
            }
            self.data_received.emit(result)

        except Exception as e:
            print(f"天气服务错误: {e}")
            self.data_received.emit(self._fallback_result(str(e)))

    @staticmethod
    def _read_json_response(response, source_name):
        response.raise_for_status()
        content = response.content or b""
        if not content.strip():
            raise ValueError(f"{source_name}响应为空")
        try:
            return response.json()
        except ValueError as exc:
            raise ValueError(f"{source_name}返回非 JSON 响应") from exc

    @staticmethod
    def _fallback_result(error_message=""):
        return {
            "temp": "--",
            "icon": "999",
            "text": "天气暂不可用",
            "city": "未知位置",
            "available": False,
            "error": error_message,
        }
