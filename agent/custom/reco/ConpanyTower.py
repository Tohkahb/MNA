import json
from typing import Union, Optional

from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
from maa.define import RectType

from utils import logger


@AgentServer.custom_recognition("IsConpanyTowerEnabled")
class IsConpanyTowerEnabled(CustomRecognition):
    """
    识别企业塔是否开启

    参数格式:
    {
        "expected": "开启",
    }

    返回结果:
    - 找到时：返回商品位置坐标 [x, y, width, height]
    - 未找到时：返回 None
    - inverse=True 且未找到时：返回 [0, 0, 0, 0]
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        # 解析识别参数
        data = json.loads(argv.custom_recognition_param)
        expected = "开启" 
        # inverse = data.get("inverse", False) 

        # 获取当前屏幕截图
        img = context.tasker.controller.post_screencap().wait().get()

        #4个塔
        roi_list = [
            [534,400,19,17],  
            [627,400,19,17],  
            [719,400,19,17], 
            [812,400,19,17]
        ]

        for i in range(len(roi_list)):
            try:
                logger.info(f"正在检测第{i+1}个企业塔~")
                roi = roi_list[i]
                reco_detail = context.run_recognition(
                    "ConpanyTowerTemplate",    
                    argv.image,
                    {"ConpanyTowerTemplate": {"roi": roi}},
                )
                if reco_detail is not None:
                    return reco_detail.box  
            except Exception as e:
                logger.warning(f"Recognition error: {e}")
                continue

        # if inverse:  
        #     return [0, 0, 0, 0]
        return None  
