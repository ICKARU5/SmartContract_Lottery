from scripts.WEB3_support import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_pricefeed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Deployed lottery")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]

    start_tx = lottery.startLottery({"from": account})
    start_tx.wait(1)
    print("Lottery has started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]

    required_fee = lottery.getEntranceFee()

    tx_enter = lottery.enter({"from": account, "value": required_fee + 1000})
    tx_enter.wait(1)
    print(f"Account with address {account.address} has entered the lottery")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # First fund contract with required LINK token
    tx_1 = fund_with_link(lottery.address)

    tx_end = lottery.endLottery({"from": account})

    # Waiting for contract to finish
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
