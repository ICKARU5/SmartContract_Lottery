from brownie import network
from brownie.network import account
import pytest
from scripts.WEB3_support import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
)
from scripts.deploy_lottery import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    print(account.address)

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    tx = fund_with_link(lottery)
    print("funded with link")
    lottery.endLottery({"from": account})
    # Have to wait for response from chainlink node
    time.sleep(180)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
