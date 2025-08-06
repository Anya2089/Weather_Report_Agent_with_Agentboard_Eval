import requests
import logging
from geopy.distance import geodesic
from datetime import datetime
from copy import deepcopy
from datetime import datetime, timedelta
import json
import uuid
import os

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# 从IP中生成物理地址

URLS = {
    "historical_weather": "https://archive-api.open-meteo.com/v1/archive",
    "geocoding": "https://geocoding-api.open-meteo.com/v1/search",
    "air_quality": "https://air-quality-api.open-meteo.com/v1/air-quality",
    "elevation": "https://api.open-meteo.com/v1/elevation",
    # "zipcode": "http://ZiptasticAPI.com/{zipcode}"
    # "weather_forecast": "https://api.open-meteo.com/v1/forecast",
}

def is_within_30_days(start_date: str, end_date: str) -> bool:
    # 将字符串格式的日期转换为datetime对象
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 计算两个日期之间的差异
    difference = end_date_obj - start_date_obj
    
    # 判断差异是否为30天
    if difference > timedelta(days=30):
        return False
    else:
        return True

def clean_observation(observation):
    new_observation = deepcopy(observation)
    if type(new_observation) == dict and "daily" in new_observation.keys() and "temperature_2m_max" in new_observation["daily"].keys():
        new_observation["daily"].pop("temperature_2m_max")
        new_observation["daily"].pop("temperature_2m_min")
        new_observation["daily"].pop("temperature_2m_mean")
    return new_observation

def log_path(func):
    def wrapper(*args, **kwargs):
        if "action_path" in kwargs.keys():
            action_path = kwargs["action_path"]
            kwargs.pop("action_path")
            success, result = func(*args, **kwargs)

            # convert value in kwargs to string
            # for key, value in kwargs.items():
                # kwargs[key] = str(value)

            if success:
                action_path.append({
                    "Action" : func.__name__,
                    "Action Input" : str(kwargs),
                    "Observation": result,
                    "Subgoal": clean_observation( result )
                })
                return result
            else:
                action_path.append({
                    "Action" : func.__name__,
                    "Action Input" : str(kwargs),
                    "Observation": result,
                    "Subgoal": "Calling " + func.__name__ + " with " + str(kwargs) + " failed",
                })
                return result
        else:
            success, result = func(*args, **kwargs)
            return success, result  # 返回元组(success, result)而不是只返回result
    return wrapper

class weather_toolkits:
    def __init__(self, init_config=None):
        if init_config is not None:
            if "current_date" in init_config.keys():
                self.current_date = init_config["current_date"]
            if "current_location" in init_config.keys():
                self.current_location = init_config["current_location"]

    @log_path
    def get_user_current_date(self):
        return True, self.current_date

    @log_path
    def get_user_current_location(self):
        return True, self.current_location

    @log_path
    def get_historical_temp(self, latitude=None, longitude=None, start_date=None, end_date=None, is_historical=True):
        if is_historical is True:
            # make sure that start_date and end_date are fewer than current_date
            if start_date is not None:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if start_date_obj >= current_date_obj:
                    return False, "Error: start_date should be earlier than current_date"
            if end_date is not None:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if end_date_obj >= current_date_obj:
                    return False, "Error: end_date should be earlier than current_date"
        
        if is_within_30_days(start_date, end_date) is False:
            return False, "Error: Sorry, at present, we support a maximum time span of 30 days between start_date and end_date in a single query. Your input exceeds this range. You can split your current query into multiple sub-queries that meet our criteria."

        def _clean(response):
            if "elevation" in response.keys():
                response.pop("elevation")
            if "generationtime_ms" in response.keys():
                response.pop("generationtime_ms")
            if "timezone" in response.keys():
                response.pop("timezone")
            if "timezone_abbreviation" in response.keys():
                response.pop("timezone_abbreviation")
            if "utc_offset_seconds" in response.keys():
                response.pop("utc_offset_seconds")
            # if "daily_units" in response.keys():
                # response.pop("daily_units")
            return response

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "GMT",   # Use default timezone
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean"
        }
        response = requests.get(URLS["historical_weather"], params=params)
        if response.status_code == 200:
            return True, _clean( response.json() )
        else:
            return False, response.text

    @log_path
    def get_historical_rain(self, latitude=None, longitude=None, start_date=None, end_date=None, is_historical=True):
        if is_historical is True:
            # make sure that start_date and end_date are fewer than current_date
            if start_date is not None:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if start_date_obj >= current_date_obj:
                    return False, "Error: start_date should be earlier than current_date"
            if end_date is not None:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if end_date_obj >= current_date_obj:
                    return False, "Error: end_date should be earlier than current_date"

        if is_within_30_days(start_date, end_date) is False:
            return False, "Error: Sorry, at present, we support a maximum time span of 30 days between start_date and end_date in a single query. Your input exceeds this range. You can split your current query into multiple sub-queries that meet our criteria."

        def _clean(response):
            if "elevation" in response.keys():
                response.pop("elevation")
            if "generationtime_ms" in response.keys():
                response.pop("generationtime_ms")
            if "timezone" in response.keys():
                response.pop("timezone")
            if "timezone_abbreviation" in response.keys():
                response.pop("timezone_abbreviation")
            if "utc_offset_seconds" in response.keys():
                response.pop("utc_offset_seconds")
            return response

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "GMT",   # Use default timezone
            "daily": "rain_sum"
        } 
        response = requests.get(URLS["historical_weather"], params=params)
        if response.status_code == 200:
            return True, _clean( response.json() )
        else:
            return False, response.text

    @log_path
    def get_historical_snow(self, latitude=None, longitude=None, start_date=None, end_date=None, is_historical=True):
        if is_historical is True:
            # make sure that start_date and end_date are fewer than current_date
            if start_date is not None:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if start_date_obj >= current_date_obj:
                    return False, "Error: start_date should be earlier than current_date"
            if end_date is not None:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if end_date_obj >= current_date_obj:
                    return False, "Error: end_date should be earlier than current_date"

        if is_within_30_days(start_date, end_date) is False:
            return False, "Error: Sorry, at present, we support a maximum time span of 30 days between start_date and end_date in a single query. Your input exceeds this range. You can split your current query into multiple sub-queries that meet our criteria."

        def _clean(response):
            if "elevation" in response.keys():
                response.pop("elevation")
            if "generationtime_ms" in response.keys():
                response.pop("generationtime_ms")
            if "timezone" in response.keys():
                response.pop("timezone")
            if "timezone_abbreviation" in response.keys():
                response.pop("timezone_abbreviation")
            if "utc_offset_seconds" in response.keys():
                response.pop("utc_offset_seconds")
            return response

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "GMT",   # Use default timezone
            "daily": "snowfall_sum"
        } 
        response = requests.get(URLS["historical_weather"], params=params)
        if response.status_code == 200:
            return True, _clean( response.json() )
        else:
            return False, response.text

    @log_path
    def get_snow_forecast(self,
                          latitude=None,
                          longitude=None,
                          start_date=None,
                          end_date=None):
        # make sure that start_date and end_date are later than current_date
        if start_date is not None:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
            if start_date_obj <= current_date_obj:
                return False, "Error: start_date should be later than current_date"
        if end_date is not None:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
            if end_date_obj <= current_date_obj:
                return False, "Error: end_date should be later than current_date"

        if is_within_30_days(start_date, end_date) is False:
            return False, "Error: Sorry, at present, we support a maximum time span of 30 days between start_date and end_date in a single query. Your input exceeds this range. You can split your current query into multiple sub-queries that meet our criteria."
 
        success, response = self.get_historical_snow(latitude=latitude,
                                            longitude=longitude,
                                            start_date=start_date,
                                            end_date=end_date,
                                            is_historical=False)
        return success, response

    @log_path
    def get_current_snow(self,
                         latitude=None,
                         longitude=None,
                         current_date=None):
        success, response = self.get_historical_snow(latitude=latitude,
                                            longitude=longitude,
                                            start_date=current_date,
                                            end_date=current_date,
                                            is_historical=False
                                            )
        return success, response

    @log_path
    def get_current_temp(self, latitude=None, longitude=None, current_date=None):
        # We use get_historical_weather to get current weather
        success, response = self.get_historical_temp(latitude=latitude,
                                               longitude=longitude,
                                               start_date=current_date,
                                               end_date=current_date,
                                               is_historical=False
                                               )
        return success, response

    @log_path
    def get_latitude_longitude(self, name=None):
        def _clean(response):
            for item in response["results"]:
                if "elevation" in item.keys():
                    item.pop("elevation")
                if "feature_code" in item.keys():
                    item.pop("feature_code")
                if "country_code" in item.keys():
                    item.pop("country")
                if "country_id" in item.keys():
                    item.pop("country_id")
                if "admin1_id" in item.keys():
                    item.pop("admin1_id")
                if "timezone" in item.keys():
                    item.pop("timezone")
                if "population" in item.keys():
                    item.pop("population")
                if "postcodes" in item.keys():
                    item.pop("postcodes")
                for key in list(item.keys()):
                    if key.endswith("id"):
                        item.pop(key)
                for key in list(item.keys()):
                    if "admin" in key:
                        item.pop(key)
            if "generationtime_ms" in response.keys():
                response.pop("generationtime_ms")
            return response

        params = {
            "name": name,
            "count": 3,
            "language": "en",
            "format": "json"
        }

        response = requests.get(URLS["geocoding"], params=params)
        if response.status_code == 200:
            return True, _clean( response.json() )
        else:
            return False, response.text
    
    @log_path
    def get_air_quality(slef, latitude=None, longitude=None):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "european_aqi_pm2_5"
            # "hourly": hourly
        }
        response = requests.get(URLS["air_quality"], params=params)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text

    @log_path
    def get_elevation(self, latitude=None, longitude=None):
        params = {
            "latitude": latitude,
            "longitude": longitude
        }
        response = requests.get(URLS["elevation"], params=params)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text

    @log_path
    def get_temp_forecast(self,
                             latitude=None,
                             longitude=None,
                             start_date=None,
                             end_date=None):
        # make sure that start_date and end_date are later than current_date
        if start_date is not None:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
            if start_date_obj <= current_date_obj:
                return False, "Error: start_date should be later than current_date"
        if end_date is not None:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
            if end_date_obj <= current_date_obj:
                return False, "Error: end_date should be later than current_date"

        if is_within_30_days(start_date, end_date) is False:
            return False, "Error: Sorry, at present, we support a maximum time span of 30 days between start_date and end_date in a single query. Your input exceeds this range. You can split your current query into multiple sub-queries that meet our criteria."

        success, response = self.get_historical_temp(latitude=latitude,
                                                longitude=longitude,
                                                start_date=start_date,
                                                end_date=end_date,
                                                is_historical=False)
        return success, response

    @log_path
    def get_rain_forecast(self,
                          latitude=None,
                          longitude=None,
                          start_date=None,
                          end_date=None):
        # make sure that start_date and end_date are later than current_date
        if start_date is not None:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
            if start_date_obj <= current_date_obj:
                return False, "Error: start_date should be later than current_date"
        if end_date is not None:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
            if end_date_obj <= current_date_obj:
                return False, "Error: end_date should be later than current_date"

        if is_within_30_days(start_date, end_date) is False:
            return False, "Error: Sorry, at present, we support a maximum time span of 30 days between start_date and end_date in a single query. Your input exceeds this range. You can split your current query into multiple sub-queries that meet our criteria."
     
        success, response = self.get_historical_rain(latitude=latitude,
                                                longitude=longitude,
                                                start_date=start_date,
                                                end_date=end_date,
                                                is_historical=False)
        return success, response

    @log_path
    def get_current_rain(self,
                         latitude=None,
                         longitude=None,
                         current_date=None):
        success, response = self.get_historical_rain(latitude=latitude,
                                            longitude=longitude,
                                            start_date=current_date,
                                            end_date=current_date,
                                            is_historical=False
                                            )
        return success, response

    @log_path
    def get_distance(self, latitude1=None, longitude1=None, latitude2=None, 
                     longitude2=None):
        coord1 = (latitude1, longitude1)
        coord2 = (latitude2, longitude2)
        distance = geodesic(coord1, coord2).km
        return True, distance
    
    @log_path
    def get_historical_air_quality_index(self,
                           latitude=None,
                           longitude=None,
                           start_date=None,
                           end_date=None,
                           is_historical=True):
        if is_historical is True:
            # make sure that start_date and end_date are fewer than current_date
            if start_date is not None:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if start_date_obj >= current_date_obj:
                    return False, "Error: start_date should be earlier than current_date"
            if end_date is not None:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
                if end_date_obj >= current_date_obj:
                    return False, "Error: end_date should be earlier than current_date"

        if is_within_30_days(start_date, end_date) is False:
            return False, "Error: Sorry, at present, we support a maximum time span of 30 days between start_date and end_date in a single query. Your input exceeds this range. You can split your current query into multiple sub-queries that meet our criteria."

        def _clean(response):
            if "elevation" in response.keys():
                response.pop("elevation")
            if "generationtime_ms" in response.keys():
                response.pop("generationtime_ms")
            if "timezone" in response.keys():
                response.pop("timezone")
            if "timezone_abbreviation" in response.keys():
                response.pop("timezone_abbreviation")
            if "utc_offset_seconds" in response.keys():
                response.pop("utc_offset_seconds")
            return response
        
        def _gather_data(response):
            new_response = {
                "latitude": response["latitude"],
                "longitude": response["longitude"],
                "daily_units": response["hourly_units"],
                "daily": response["hourly"]
            }

            # filter 12:00 data as daily data
            num_days = len(new_response["daily"]["time"]) // 24
            european_aqi_pm2_5 = []
            for i in range(num_days):
                european_aqi_pm2_5.append( new_response["daily"]["european_aqi_pm2_5"][24*i+12] )
            new_response["daily"]["european_aqi_pm2_5"] = european_aqi_pm2_5
            time = []
            for i in range(num_days):
                time.append( new_response["daily"]["time"][24*i+12] )
            new_response["daily"]["time"] = time
            return new_response

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "GMT",   # Use default timezone
            "hourly": "european_aqi_pm2_5"
        }
        response = requests.get(URLS["air_quality"], params=params)
        if response.status_code == 200:
            response = _clean( response.json() )
            response = _gather_data( response )
            return True, response
        else:
            return False, response.text

    @log_path
    def get_current_air_quality_index(self,
                           latitude=None,
                           longitude=None,
                           current_date=None):
        success, response = self.get_historical_air_quality_index(latitude=latitude,
                                                         longitude=longitude,
                                                         start_date=current_date,
                                                         end_date=current_date,
                                                         is_historical=False)
        return success, response

    @log_path
    def get_air_quality_level(self, air_quality_index):
        response = None
        if air_quality_index <= 20:
            response = "good"
        elif 21 < air_quality_index <= 40:
            response = "fair"
        elif 41 < air_quality_index <= 60:
            response = "moderate"
        elif 61 < air_quality_index <= 80:
            response = "poor"
        elif 81 < air_quality_index <= 100:
            response = "very poor"
        else:
            response = "extremely poor"
        return True, response
    
    @log_path
    def convert_zipcode_to_address(self, zipcode):
        response = requests.get(URLS["zipcode"].format(zipcode=zipcode))
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    
    @log_path
    def generate_weather_report(self, location_name=None, weather_data=None, report_type="comprehensive", output_formats=["json", "markdown", "html", "text"], save_to_file=True, base_directory="weather_reports"):
        """
        生成多格式天气报告并保存到文件
        """
        if not location_name or not weather_data:
            return False, "Error: location_name and weather_data are required"
        
        # 生成报告ID和时间戳
        now = datetime.now()
        report_id = f"weather_report_{now.strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        generated_at = now.isoformat()
        
        # 记录当前工作目录和环境信息
        current_dir = os.getcwd()
        logger.info(f"Weather report generation started - Working directory: {current_dir}")
        logger.info(f"Report ID: {report_id}, Location: {location_name}")
        
        # 解析天气数据
        parsed_data = self._parse_weather_data(weather_data)
        
        # 生成各种格式的报告
        reports = {}
        
        if "json" in output_formats:
            reports["json"] = self._generate_json_report(location_name, parsed_data, report_id, generated_at)
        
        if "markdown" in output_formats:
            reports["markdown"] = self._generate_markdown_report(location_name, parsed_data, report_id, generated_at)
        
        if "html" in output_formats:
            reports["html"] = self._generate_html_report(location_name, parsed_data, report_id, generated_at)
        
        if "text" in output_formats:
            reports["text"] = self._generate_text_report(location_name, parsed_data, report_id, generated_at)
        
        # 保存文件
        files = {}
        base_dir = None
        file_verification = {}
        
        if save_to_file:
            try:
                # 创建目录结构：使用绝对路径确保位置可预测
                date_str = now.strftime('%Y-%m-%d')
                base_dir = os.path.abspath(os.path.join(current_dir, base_directory, date_str, report_id))
                
                logger.info(f"Attempting to create directory: {base_dir}")
                os.makedirs(base_dir, exist_ok=True)
                
                # 验证目录创建成功
                if os.path.exists(base_dir):
                    logger.info(f"Directory created successfully: {base_dir}")
                else:
                    logger.error(f"Directory creation failed: {base_dir}")
                    return False, f"Failed to create directory: {base_dir}"
                
                # 保存各种格式的文件
                for format_name, content in reports.items():
                    try:
                        if format_name == "json":
                            file_path = os.path.join(base_dir, "report.json")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(content, f, ensure_ascii=False, indent=2)
                        elif format_name == "markdown":
                            file_path = os.path.join(base_dir, "report.md")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        elif format_name == "html":
                            file_path = os.path.join(base_dir, "report.html")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        elif format_name == "text":
                            file_path = os.path.join(base_dir, "report.txt")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        
                        # 立即验证文件是否保存成功
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                            files[format_name] = file_path
                            file_verification[format_name] = {
                                "exists": True,
                                "size": os.path.getsize(file_path),
                                "absolute_path": os.path.abspath(file_path)
                            }
                            logger.info(f"File saved and verified: {file_path} ({os.path.getsize(file_path)} bytes)")
                        else:
                            file_verification[format_name] = {
                                "exists": False,
                                "size": 0,
                                "absolute_path": os.path.abspath(file_path) if file_path else None
                            }
                            logger.error(f"File verification failed: {file_path}")
                            
                    except Exception as file_error:
                        logger.error(f"Error saving {format_name} file: {str(file_error)}")
                        file_verification[format_name] = {
                            "exists": False,
                            "size": 0,
                            "error": str(file_error)
                        }
                        continue
                    
            except Exception as e:
                logger.error(f"Error in file saving process: {str(e)}")
                return False, f"Error saving files: {str(e)}"
        
        # 计算实际保存成功的文件数量
        files_actually_saved = len([v for v in file_verification.values() if v.get("exists", False)])
        
        result = {
            "success": True,
            "reports": reports,
            "files": files if save_to_file else {},
            "metadata": {
                "report_id": report_id,
                "generated_at": generated_at,
                "location": location_name,
                "formats": output_formats,
                "base_directory": base_dir if save_to_file else None,
                "files_saved": save_to_file and files_actually_saved > 0,
                "files_requested": len(output_formats) if save_to_file else 0,
                "files_actually_saved": files_actually_saved,
                "working_directory": current_dir,
                "absolute_base_directory": base_dir,
                "file_verification": file_verification
            }
        }
        
        logger.info(f"Weather report generation completed - Files saved: {files_actually_saved}/{len(output_formats) if save_to_file else 0}")
        
        return True, result

    def _parse_weather_data(self, weather_data):
        """解析天气数据"""
        parsed = {
            "temperature": {},
            "precipitation": {},
            "air_quality": {},
            "location_info": {}
        }
        
        # 解析温度数据
        if "temperature" in weather_data:
            temp_data = weather_data["temperature"]
            if "daily" in temp_data:
                daily = temp_data["daily"]
                if "temperature_2m_mean" in daily:
                    parsed["temperature"]["current"] = daily["temperature_2m_mean"][0] if daily["temperature_2m_mean"] else None
                if "temperature_2m_max" in daily:
                    parsed["temperature"]["max"] = daily["temperature_2m_max"][0] if daily["temperature_2m_max"] else None
                if "temperature_2m_min" in daily:
                    parsed["temperature"]["min"] = daily["temperature_2m_min"][0] if daily["temperature_2m_min"] else None
        
        # 解析降水数据
        if "precipitation" in weather_data:
            precip_data = weather_data["precipitation"]
            if "rain" in precip_data:
                parsed["precipitation"]["rain"] = precip_data["rain"]
            if "snow" in precip_data:
                parsed["precipitation"]["snow"] = precip_data["snow"]
        
        # 解析空气质量数据
        if "air_quality" in weather_data:
            aq_data = weather_data["air_quality"]
            parsed["air_quality"]["index"] = aq_data.get("index")
            parsed["air_quality"]["level"] = aq_data.get("level")
        
        return parsed

    def _generate_json_report(self, location_name, parsed_data, report_id, generated_at):
        """生成JSON格式报告"""
        return {
            "report_id": report_id,
            "location": {
                "name": location_name,
                "query_date": self.current_date
            },
            "generated_at": generated_at,
            "current_weather": {
                "temperature": {
                    "current": parsed_data["temperature"].get("current"),
                    "max": parsed_data["temperature"].get("max"),
                    "min": parsed_data["temperature"].get("min"),
                    "unit": "°C"
                },
                "precipitation": {
                    "rain": parsed_data["precipitation"].get("rain", 0.0),
                    "snow": parsed_data["precipitation"].get("snow", 0.0),
                    "unit": "mm"
                },
                "air_quality": {
                    "index": parsed_data["air_quality"].get("index"),
                    "level": parsed_data["air_quality"].get("level")
                }
            },
            "summary": self._generate_summary(parsed_data),
            "recommendations": self._generate_recommendations(parsed_data)
        }

    def _generate_markdown_report(self, location_name, parsed_data, report_id, generated_at):
        """生成Markdown格式报告"""
        temp = parsed_data["temperature"]
        precip = parsed_data["precipitation"]
        aq = parsed_data["air_quality"]
        
        markdown = f"""# 🌤️ 天气报告

## 📍 基本信息
- **查询位置**: {location_name}
- **查询日期**: {self.current_date}
- **报告生成时间**: {generated_at}
- **报告ID**: {report_id}

## 🌡️ 当前天气状况
- **温度**: {temp.get('current', 'N/A')}°C (最高: {temp.get('max', 'N/A')}°C, 最低: {temp.get('min', 'N/A')}°C)
- **降雨量**: {precip.get('rain', 0.0)}mm {'(无降雨)' if precip.get('rain', 0.0) == 0 else ''}
- **降雪量**: {precip.get('snow', 0.0)}mm {'(无降雪)' if precip.get('snow', 0.0) == 0 else ''}
- **空气质量**: {aq.get('level', 'N/A')} {'(AQI: ' + str(aq.get('index')) + ')' if aq.get('index') else ''}

## 📊 天气总结
{self._generate_summary(parsed_data)}

## 💡 生活建议
{chr(10).join(['- ✅ ' + rec for rec in self._generate_recommendations(parsed_data)])}

---
*报告生成时间: {generated_at}*
"""
        return markdown

    def _generate_html_report(self, location_name, parsed_data, report_id, generated_at):
        """生成HTML格式报告"""
        temp = parsed_data["temperature"]
        precip = parsed_data["precipitation"]
        aq = parsed_data["air_quality"]
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>天气报告 - {location_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #74b9ff, #0984e3); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .weather-card {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 5px solid #74b9ff; }}
        .weather-card h3 {{ margin-top: 0; color: #2d3436; }}
        .temperature {{ font-size: 2.5em; color: #e17055; font-weight: bold; }}
        .weather-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .weather-item {{ background: #dfe6e9; padding: 15px; border-radius: 8px; text-align: center; }}
        .weather-item .value {{ font-size: 1.5em; font-weight: bold; color: #2d3436; }}
        .weather-item .label {{ color: #636e72; margin-top: 5px; }}
        .recommendations {{ background: #d1f2eb; padding: 20px; border-radius: 10px; border-left: 5px solid #00b894; }}
        .recommendations ul {{ margin: 10px 0; padding-left: 20px; }}
        .recommendations li {{ margin: 5px 0; }}
        .footer {{ text-align: center; color: #636e72; font-size: 0.9em; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ 天气报告</h1>
            <p>📍 {location_name} | 📅 {self.current_date}</p>
        </div>
        
        <div class="content">
            <div class="weather-card">
                <h3>🌡️ 温度信息</h3>
                <div class="temperature">{temp.get('current', 'N/A')}°C</div>
                <div class="weather-grid">
                    <div class="weather-item">
                        <div class="value">{temp.get('max', 'N/A')}°C</div>
                        <div class="label">最高温度</div>
                    </div>
                    <div class="weather-item">
                        <div class="value">{temp.get('min', 'N/A')}°C</div>
                        <div class="label">最低温度</div>
                    </div>
                </div>
            </div>
            
            <div class="weather-card">
                <h3>🌧️ 降水信息</h3>
                <div class="weather-grid">
                    <div class="weather-item">
                        <div class="value">{precip.get('rain', 0.0)}mm</div>
                        <div class="label">降雨量</div>
                    </div>
                    <div class="weather-item">
                        <div class="value">{precip.get('snow', 0.0)}mm</div>
                        <div class="label">降雪量</div>
                    </div>
                </div>
            </div>
            
            <div class="weather-card">
                <h3>🌬️ 空气质量</h3>
                <div class="weather-grid">
                    <div class="weather-item">
                        <div class="value">{aq.get('level', 'N/A')}</div>
                        <div class="label">质量等级</div>
                    </div>
                    <div class="weather-item">
                        <div class="value">{aq.get('index', 'N/A')}</div>
                        <div class="label">AQI指数</div>
                    </div>
                </div>
            </div>
            
            <div class="recommendations">
                <h3>💡 生活建议</h3>
                <ul>
                    {''.join(['<li>' + rec + '</li>' for rec in self._generate_recommendations(parsed_data)])}
                </ul>
            </div>
            
            <div class="footer">
                <p>报告ID: {report_id}</p>
                <p>生成时间: {generated_at}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
        return html

    def _generate_text_report(self, location_name, parsed_data, report_id, generated_at):
        """生成纯文本格式报告"""
        temp = parsed_data["temperature"]
        precip = parsed_data["precipitation"]
        aq = parsed_data["air_quality"]
        
        text = f"""==================== 天气报告 ====================
查询位置: {location_name}
查询日期: {self.current_date}
报告时间: {generated_at}
报告ID: {report_id}

当前天气:
- 温度: {temp.get('current', 'N/A')}°C ({temp.get('min', 'N/A')}°C - {temp.get('max', 'N/A')}°C)
- 降雨: {precip.get('rain', 0.0)}mm
- 降雪: {precip.get('snow', 0.0)}mm
- 空气质量: {aq.get('level', 'N/A')} (AQI: {aq.get('index', 'N/A')})

天气总结:
{self._generate_summary(parsed_data)}

生活建议:
{chr(10).join(['- ' + rec for rec in self._generate_recommendations(parsed_data)])}

================================================"""
        return text

    def _generate_summary(self, parsed_data):
        """生成天气总结"""
        temp = parsed_data["temperature"]
        precip = parsed_data["precipitation"]
        aq = parsed_data["air_quality"]
        
        summary_parts = []
        
        # 温度描述
        if temp.get("current"):
            if temp["current"] < 10:
                summary_parts.append("天气较冷")
            elif temp["current"] < 25:
                summary_parts.append("天气温和宜人")
            else:
                summary_parts.append("天气较为炎热")
        
        # 降水描述
        rain = precip.get("rain", 0.0)
        snow = precip.get("snow", 0.0)
        if rain > 0 or snow > 0:
            if rain > 0:
                summary_parts.append("有降雨")
            if snow > 0:
                summary_parts.append("有降雪")
        else:
            summary_parts.append("无降水")
        
        # 空气质量描述
        if aq.get("level"):
            summary_parts.append(f"空气质量{aq['level']}")
        
        return "，".join(summary_parts) + "。"

    def _generate_recommendations(self, parsed_data):
        """生成生活建议"""
        recommendations = []
        temp = parsed_data["temperature"]
        precip = parsed_data["precipitation"]
        aq = parsed_data["air_quality"]
        
        # 基于温度的建议
        if temp.get("current"):
            if temp["current"] < 10:
                recommendations.append("天气较冷，建议穿着厚外套")
                recommendations.append("注意保暖，避免长时间户外活动")
            elif temp["current"] < 25:
                recommendations.append("温度适宜，适合户外运动和散步")
                recommendations.append("建议穿着轻薄长袖或短袖")
            else:
                recommendations.append("天气炎热，注意防暑降温")
                recommendations.append("建议穿着透气轻薄的衣物")
        
        # 基于降水的建议
        if precip.get("rain", 0.0) > 0:
            recommendations.append("有降雨，出行请携带雨具")
        if precip.get("snow", 0.0) > 0:
            recommendations.append("有降雪，注意路面湿滑，小心出行")
        
        # 基于空气质量的建议
        if aq.get("level"):
            if aq["level"] in ["Good", "良好", "good"]:
                recommendations.append("空气质量良好，适合开窗通风")
            elif aq["level"] in ["Moderate", "中等", "moderate"]:
                recommendations.append("空气质量一般，敏感人群减少户外活动")
            else:
                recommendations.append("空气质量较差，建议减少户外活动")
        
        # 温差建议
        if temp.get("max") and temp.get("min"):
            temp_diff = temp["max"] - temp["min"]
            if temp_diff > 10:
                recommendations.append("早晚温差较大，注意增减衣物")
        
        return recommendations if recommendations else ["天气状况正常，注意适当增减衣物"]

    @log_path
    def finish(self, answer):
        if type(answer) == list:
            answer = sorted(answer)
        return True, answer

    # @log_path

if __name__ == "__main__":
    init_config = {
        "current_date": "2023-01-01"
    }
    tool = weather_toolkits(init_config=init_config)
    
    # print( tool.get_temp_forecast(latitude=40.699997,
                                #   longitude= ) )
    # print( tool.get_weather_forecast(latitude="52.52", longitude="13.41") )
    # print( tool.get_weather_forecast(latitude="52.52", longitude="13.41") )
    # print( tool.get_eveluation(latitude="52.52", longitude="13.41") )
    # pprint( tool.get_air_quality(latitude="40.7128", longitude="-74.0060") )
    # pprint(tool.get_geocoding(name="New York"))
    print(tool.get_historical_temp(latitude=31.22222, longitude=121.45806, start_date="2015-01-01", end_date="2015-03-01"))
    # pprint( tool.get_historical_air(latitude=52.52, longitude=13.41, start_date="2022-11-01", end_date="2022-11-30") )
    # pprint( tool.convert_zipcode_to_address("84323") )
    # print( tool.get_geocoding(name="Shanghai") )
