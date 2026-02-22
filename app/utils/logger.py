import logging
import os
from logging.handlers import RotatingFileHandler
from flask import current_app


def setup_logging(app):
    """配置日志系统"""
    
    # 创建logs目录
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # 只在非调试模式下使用文件日志
    if not app.debug:
        # 配置文件日志处理器
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    # 设置日志级别
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')


def get_logger(name):
    """获取命名日志记录器"""
    return logging.getLogger(name)
