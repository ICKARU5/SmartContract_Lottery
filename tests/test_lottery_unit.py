from brownie import network, exceptions
from scripts.WEB3_support import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest

# these unit tests should only be tested on development networks

# Eth value in mock was 2000 USD and entrance fee 50 USD, fee is in wei
def test_get_entrance_fee():

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    Fee = lottery.getEntranceFee()
    Expected = Web3.toWei(0.025, "ether")
    assert Fee == Expected


def test_cant_enter_unless_started():

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": account, "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    assert lottery.players(0) == account


def test_can_end_lottery():

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    lottery.endLottery({"from": account})

    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)

    # for check later
    starting_bal = account.balance()
    lottery_bal = lottery.balance()

    tx = lottery.endLottery({"from": account})

    # Make dummy random call
    request_id = tx.events["RequestedRandomness"]["requestId"]
    RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, RNG, lottery, {"from": account}
    )

    # 777%3 = 0, since 3 players entered
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_bal + lottery_bal
