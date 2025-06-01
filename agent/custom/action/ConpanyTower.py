

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from maa.define import RectType

from utils import logger


@AgentServer.custom_action("IsConpanyTowerEnabled")
class IsConpanyTowerEnabled(CustomAction):
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

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        #4个塔
        roi_list = [
            [534,400,19,17],  
            [627,400,19,17],  
            [719,400,19,17], 
            [812,400,19,17]
        ]
        tower_list = [
            "极乐净土之塔",  
            "米西利斯之塔",  
            "泰特拉之塔",  
            "朝圣者之塔"
        ]
        for i in range(len(roi_list)):
            try:
                logger.info(f"正在刷{tower_list[i]}~")
                roi = roi_list[i]
                context.run_task(
                    "EnterConpanyTower",
                    {
                        "EnterConpanyTower": {
                            "roi": roi,
                        }
                    },
                )
                logger.info(f"{tower_list[i]}刷取完毕~")
                logger.info(f"开始换图~")
                context.run_task("Arknights")           
                continue
            except Exception as e:
                logger.error(f"{tower_list[i]}发生错误: {e}")
                CustomAction.RunResult(success=False)
        logger.info(f"企业塔刷取完毕~")
        # if inverse:  
        #     return [0, 0, 0, 0]
        return CustomAction.RunResult(success=True)
