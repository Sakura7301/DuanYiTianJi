import os  
import io  
import re  
import time  
from PIL import Image  
from plugins import *
from common.log import logger  



@plugins.register(name="DuanYiTianJi", desc="DuanYiTianJi 64 trigrams image", version="1.0", author="lanvent", desire_priority= 99)
class DuanYiTianJi:  
    def __init__(self):  
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
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[DuanYiTianJi] inited")

    def GuaTuRequest(self, query):  
        divination_keywords = ['卦图']  
        return any(keyword in query for keyword in divination_keywords)  

    def GuaTuReDailyRequest(self, query):  
        divination_keywords = ['每日一卦']  
        return any(keyword in query for keyword in divination_keywords)  

    def GuaTu(self, input_text):  
        """  
        根据输入文本读取对应的卦图  
    
        参数:  
        input_text (str): 包含卦图信息的文本，可以是数字、卦名或卦名前缀  
    
        返回:  
        bytes: 图片的二进制数据  
        """  
        try:  
            input_text = input_text.replace('　', ' ').strip()  
            gua_dir = "./image"
            files = os.listdir(gua_dir)  
            input_text = input_text.replace('卦图', '').strip()  
            target_file = None  
            gua_name = None  
            
            number_match = re.search(r'\d+', input_text)  
            if number_match:  
                number = int(number_match.group())  
                if 1 <= number <= 64:  
                    prefix = f"{number:02d}_"  
                    for file in files:  
                        if file.startswith(prefix):  
                            target_file = file  
                            break  
            
            if not target_file:  
                search_text = input_text.replace(' ', '')  
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
                raise FileNotFoundError(f"找不到与 '{input_text}' 匹配的卦图")  
                
            image_path = os.path.join(gua_dir, target_file)  
            with Image.open(image_path) as img:  
                image_io = io.BytesIO()  
                img.save(image_io, format='PNG')  
                image_io.seek(0)  
                logger.info(f"成功找到并读取卦图：{target_file}")  
                return image_io  
                
        except Exception as e:  
            logger.info(f"错误：{str(e)}")  
            return None  

    def GuaTuNum(self):  
        """  
        根据数字（1-64）读取对应的卦图  
    
        返回:  
        bytes: 图片的二进制数据，如果出错返回None  
        """  
        try:  
            current_time = time.time()  
            microseconds = int(str(current_time).split('.')[1][:6])  
            gen_random_num = microseconds % 64 + 1  
            gua_dir = "./image" 
            files = os.listdir(gua_dir)  
            prefix = f"{gen_random_num:02d}_"  
            target_file = None  
            for file in files:  
                if file.startswith(prefix):  
                    target_file = file  
                    break  

            if target_file is None:  
                raise FileNotFoundError(f"找不到序号为 {gen_random_num} 的卦图")  
                
            image_path = os.path.join(gua_dir, target_file)  
            with Image.open(image_path) as img:  
                image_io = io.BytesIO()  
                img.save(image_io, format='PNG')  
                image_io.seek(0)  
                logger.info(f"成功找到并读取卦图：{target_file}")  
                return image_io  
                
        except Exception as e:  
            logger.error(f"错误：{str(e)}")  
            return None  

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        content = e_context['context'].content
        if self.GuaTuRequest(content):
            reply = Reply()
            reply.type = ReplyType.IMAGE
            reply.content = self.GuaTu(content)
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS # 事件结束，并跳过处理context的默认逻辑
        elif self.GuaTuReDailyRequest(content):
            reply = Reply()
            reply.type = ReplyType.IMAGE
            reply.content = self.GuaTuNum()
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "请按照以下格式：\n[每日一卦]：回复随机卦图\n[卦图+卦名]回复指定卦图\n"
        return help_text
