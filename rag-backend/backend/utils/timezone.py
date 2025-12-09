"""
时区工具模块
提供统一的时区转换功能
"""
import pytz
from datetime import datetime
from typing import Optional

# 中国时区
CHINA_TZ = pytz.timezone('Asia/Shanghai')
UTC_TZ = pytz.UTC


def to_china_time(dt: Optional[datetime]) -> Optional[datetime]:
    """
    将UTC时间转换为中国时间
    
    Args:
        dt: UTC时间的datetime对象，如果为None则返回None
        
    Returns:
        转换后的中国时间datetime对象，如果输入为None则返回None
    """
    if dt is None:
        return None
    
    # 如果datetime对象没有时区信息，假设它是UTC时间
    if dt.tzinfo is None:
        dt = UTC_TZ.localize(dt)
    
    # 转换为中国时区
    return dt.astimezone(CHINA_TZ)


def get_china_now() -> datetime:
    """
    获取当前中国时间
    
    Returns:
        当前中国时间的datetime对象
    """
    return datetime.now(CHINA_TZ)


def format_china_time(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """
    将时间格式化为中国时区的字符串
    
    Args:
        dt: 要格式化的datetime对象
        fmt: 时间格式字符串
        
    Returns:
        格式化后的时间字符串，如果输入为None则返回None
    """
    if dt is None:
        return None
    
    china_time = to_china_time(dt)
    return china_time.strftime(fmt) if china_time else None


class ChinaTimeFormatter:
    """
    中国时区日志格式化器
    用于将UTC时间转换为中国时间进行日志输出
    """
    
    def __init__(self, fmt: str = "%Y-%m-%d %H:%M:%S"):
        self.fmt = fmt
    
    def formatTime(self, record, datefmt=None):
        """
        格式化日志时间为中国时区
        """
        # 获取UTC时间
        utc_time = datetime.utcfromtimestamp(record.created)
        # 转换为中国时间
        china_time = to_china_time(utc_time)
        # 格式化输出
        return china_time.strftime(datefmt or self.fmt)