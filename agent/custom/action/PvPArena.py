import re
import json
import time

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger

@AgentServer.custom_action("SelectRookieOpponent")
class SelectChapter(CustomAction):
    """
    新人竞技场选择对手 。

    参数格式:
    {
        "opponent": "选择的对手"
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        opponent = json.loads(argv.custom_action_param)["opponent"]
        roi_list = [
            [726,364,97,70],
            [0,0,0,0],
            [731,558,90,70]
        ]
        roi = roi_list[int(opponent) - 1]

        context.run_task(
            "FreeBattlesLeft",
            {
                "FreeBattlesLeft": {
                    "roi": roi
                }
            },
        )

    #    roi_list = [
    #         [325, 286, 87, 23],
    #         [568, 284, 87, 23],
    #         [798, 286, 101, 21],
    #         [1047, 285, 87, 23],
    #         [327, 547, 87, 23],
    #         [566, 546, 87, 23],
    #         [806, 546, 87, 23],
    #         [1046, 547, 87, 23],
    #     ]

    #     for roi in roi_list:
    #         try:
    #             reco_detail = context.run_recognition(
    #                 "BankShopTemplate",
    #                 img,
    #                 {"BankShopTemplate": {"roi": roi, "expected": expected}},
    #             )


        return CustomAction.RunResult(success=True)
