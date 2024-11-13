# encoding:utf-8  

import os  
import io  
import re  
import time  
import plugins  
from PIL import Image  
from bridge.context import ContextType  
from bridge.reply import Reply, ReplyType  
from common.log import logger  
from plugins import *  
from config import conf  

@plugins.register(  
    name="DuanYiTianJi",  # 插件名称  
    desire_priority=99,  # 插件优先级  
    hidden=False,  # 是否隐藏  
    desc="DuanYiTianJi 64 trigrams image",  # 插件描述  
    version="1.0",  # 插件版本  
    author="sakura7301",  # 作者  
)  
class DuanYiTianJi(Plugin):  
    def __init__(self):  
        super().__init__()  # 调用父类的初始化  
        self.GUA_MAPPING = {  
            "乾": "乾为天",  
            "坤": "坤为地",  
            "震": "震为雷",  
            "巽": "巽为风",  
            "坎": "坎为水",  
            "离": "离为火",  
            "艮": "艮为山",  
            "兑": "兑为泽",  
            "天风": "天风姤",  
            "天山": "天山遁",  
            "天地": "天地否",  
            "天雷": "天雷无妄",  
            "天火": "天火同人",  
            "天水": "天水讼",  
            "天泽": "天泽履",  
            "地风": "地风升",  
            "地山": "地山谦",  
            "地天": "地天泰",  
            "地雷": "地雷复",  
            "地火": "地火明夷",  
            "地水": "地水师",  
            "地泽": "地泽临",  
            "雷风": "雷风恒",  
            "雷山": "雷山小过",  
            "雷天": "雷天大壮",  
            "雷地": "雷地豫",  
            "雷火": "雷火丰",  
            "雷水": "雷水解",  
            "雷泽": "雷泽归妹",  
            "风山": "风山渐",  
            "风天": "风天小畜",  
            "风地": "风地观",  
            "风雷": "风雷益",  
            "风火": "风火家人",  
            "风水": "风水涣",  
            "风泽": "风泽中孚",  
            "水风": "水风井",  
            "水山": "水山蹇",  
            "水天": "水天需",  
            "水地": "水地比",  
            "水雷": "水雷屯",  
            "水火": "水火既济",  
            "水泽": "水泽节",  
            "火风": "火风鼎",  
            "火山": "火山旅",  
            "火天": "火天大有",  
            "火地": "火地晋",  
            "火雷": "火雷噬嗑",  
            "火水": "火水未济",  
            "火泽": "火泽睽",  
            "山风": "山风蛊",  
            "山天": "山天大畜",  
            "山地": "山地剥",  
            "山雷": "山雷颐",  
            "山火": "山火贲",  
            "山水": "山水蒙",  
            "山泽": "山泽损",  
            "泽风": "泽风大过",  
            "泽山": "泽山咸",  
            "泽天": "泽天夬",  
            "泽地": "泽地萃",  
            "泽雷": "泽雷随",  
            "泽火": "泽火革",  
            "泽水": "泽水困"  
        }  
        # 注册处理上下文的事件  
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context  
        logger.info("[DuanYiTianJi] 插件初始化完毕")  

    def GuaTuRequest(self, query):  
        """检查输入查询是否包含"卦图"关键词"""  
        divination_keywords = ['卦图']  
        return any(keyword in query for keyword in divination_keywords)  

    def GuaTuReDailyRequest(self, query):  
        """检查输入查询是否包含"每日一卦"关键词"""  
        divination_keywords = ['每日一卦']  
        return any(keyword in query for keyword in divination_keywords)  

    def GuaTu(self, input_text):  
        """根据输入文本读取对应的卦图"""  
        try:  
            input_text = input_text.replace('　', ' ').strip()  
            gua_dir = "./plugins/DuanYiTianJi/image"  
            current_directory = os.getcwd()  
            logger.debug(f"current_directory: {current_directory}")
            logger.debug(f"[DuanYiTianJi] 查找卦图目录: {gua_dir}")  
            files = os.listdir(gua_dir)  # 列出卦图目录中的所有文件  
            input_text = input_text.replace('卦图', '').strip()  # 去掉"卦图"关键词  
            target_file = None  
            gua_name = None  

            # 正则匹配数字  
            number_match = re.search(r'\d+', input_text)  
            if number_match:  
                number = int(number_match.group())  
                if 1 <= number <= 64:  
                    prefix = f"{number:02d}_"  # 构造文件前缀  
                    for file in files:  
                        if file.startswith(prefix):  
                            target_file = file  
                            break  
            logger.debug(f"target_file: {target_file}")

            if not target_file:  
                search_text = input_text.replace(' ', '')  
                # 处理卦名称  
                if len(search_text) >= 1 and search_text[0] in self.GUA_MAPPING:  
                    gua_name = self.GUA_MAPPING[search_text[0]]  
                elif len(search_text) >= 2 and search_text[:2] in self.GUA_MAPPING:  
                    gua_name = self.GUA_MAPPING[search_text[:2]]  
                
                if gua_name:  
                    for file in files:  
                        file_gua_name = file.split('_')[1].replace('.jpg', '')  
                        if file_gua_name == gua_name:  
                            target_file = file  
                            break  
            
            if target_file is None:  
                logger.warning(f"找不到与 '{input_text}' 匹配的卦图")  
                raise FileNotFoundError(f"找不到与 '{input_text}' 匹配的卦图")  
                
            image_path = os.path.join(gua_dir, target_file)  
            logger.info(f"image_path:{image_path}")
            with Image.open(image_path) as img:  
                image_io = io.BytesIO()  
                img.save(image_io, format='PNG')  
                image_io.seek(0)  
                logger.info(f"成功找到并读取卦图：{target_file}")  
                return image_io  
                
        except Exception as e:  
            logger.error(f"获取卦图时出现错误：{str(e)}")  
            return None  

    def GuaTuNum(self):  
        """根据生成的随机数字（1-64）读取对应的卦图"""  
        try:  
            current_time = time.time()  
            microseconds = int(str(current_time).split('.')[1][:6])  
            gen_random_num = microseconds % 64 + 1  # 生成随机数字  
            gua_dir = "./plugins/DuanYiTianJi/image"   
            current_directory = os.getcwd()  
            logger.debug(f"current_directory: {current_directory}")
            logger.debug(f"[DuanYiTianJi] 查找卦图目录: {gua_dir}")   
            files = os.listdir(gua_dir)  
            prefix = f"{gen_random_num:02d}_"  
            target_file = None  
            for file in files:  
                if file.startswith(prefix):  
                    target_file = file  
                    break  

            if target_file is None:  
                logger.warning(f"找不到序号为 {gen_random_num} 的卦图")  
                raise FileNotFoundError(f"找不到序号为 {gen_random_num} 的卦图")  
                
            image_path = os.path.join(gua_dir, target_file)  
            with Image.open(image_path) as img:  
                image_io = io.BytesIO()  
                img.save(image_io, format='PNG')  
                image_io.seek(0)  
                logger.info(f"成功找到并读取卦图：{target_file}")  
                return image_io  
                
        except Exception as e:  
            logger.error(f"获取随机卦图时出现错误：{str(e)}")  
            return None  

    def on_handle_context(self, e_context: EventContext):  
        """处理上下文事件"""  
        if e_context["context"].type not in [ContextType.TEXT]:  
            logger.debug("[DuanYiTianJi] 上下文类型不是文本，无需处理")  
            return  
        
        content = e_context["context"].content.strip()  
        logger.debug(f"[DuanYiTianJi] 处理上下文内容: {content}")  

        if self.GuaTuReDailyRequest(content):  
            logger.info("[DuanYiTianJi] 用户请求每日一卦")  
            reply = Reply()  
            image = self.GuaTuNum()  # 获取卦图  
            reply.type = ReplyType.IMAGE if image else ReplyType.TEXT  
            reply.content = image if image else "未找到卦图"  
            e_context['reply'] = reply  
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑  

        elif self.GuaTuRequest(content):  
            logger.info("[DuanYiTianJi] 用户请求卦图")  
            reply = Reply()  
            image = self.GuaTu(content)  # 获取卦图  
            reply.type = ReplyType.IMAGE if image else ReplyType.TEXT  
            reply.content = image if image else "未找到卦图"  
            e_context['reply'] = reply  
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑  

    def get_help_text(self, **kwargs):  
        """获取帮助文本"""  
        help_text = "请按照以下格式：\n[每日一卦]：回复随机卦图\n[卦图+卦名]：回复指定卦图\n"  
        return help_text