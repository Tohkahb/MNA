import json
from typing import Union, Optional

from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
from maa.define import RectType

from utils import logger
    
@AgentServer.custom_recognition("FreeBattlesLeft")
class FreeBattlesLeft(CustomRecognition):
    """
    新人竞技场选择对手 。

    参数格式:
    {
        "opponent": "选择的对手"
    }
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:

        opponent = json.loads(argv.custom_recognition_param)["opponent"]
        expected = "免费"
        roi_list = [
            [762,380,27,14],
            [762,480,27,14],
            [762,580,27,15]
        ]
        roi = roi_list[int(opponent) - 1]

        reco_detail = context.run_recognition(
            "FreeBattlesTemplate",
            argv.image,
            {"FreeBattlesTemplate": {"roi":roi, "expected": expected}}
        )
        logger.info(f"FreeBattlesTemplate: {reco_detail}")

        if reco_detail is None:
            return CustomRecognition.AnalyzeResult(box=None, detail="无文字")

        for result in reco_detail.all_results:
            if expected in result.text:
                return CustomRecognition.AnalyzeResult(box=result.box, detail=expected)

        return CustomRecognition.AnalyzeResult(box=None, detail="无目标")
