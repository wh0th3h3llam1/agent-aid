# tools/supply_admin.py
import os, asyncio
from typing import List
from uagents import Agent, Context
from agents.aid_protocol import AidProtocol, Restock, AdjustInventory, Item, InventoryStatus, ErrorMessage

ADMIN_SEED = os.getenv("ADMIN_SEED", "supply_admin_sender_seed")

async def send_restock(target_addr: str, secret: str, items: List[Item]):
    agent = Agent(name="supply_admin", seed=ADMIN_SEED, endpoint=[])
    @AidProtocol.on_message(model=InventoryStatus)
    async def on_status(ctx: Context, sender: str, msg: InventoryStatus):
        ctx.logger.info(f"Restock OK from {sender}: {[(i.name, i.qty) for i in msg.inventory]}")
        raise SystemExit(0)
    @AidProtocol.on_message(model=ErrorMessage)
    async def on_err(ctx: Context, sender: str, msg: ErrorMessage):
        ctx.logger.error(f"Error from {sender}: {msg.message}")
        raise SystemExit(1)
    agent.include(AidProtocol)

    async def run():
        await agent._ctx.send(target_addr, Restock(secret=secret, items=items))
        await asyncio.sleep(5)  # wait for reply

    asyncio.create_task(run())
    agent.run()

async def send_adjust(target_addr: str, secret: str, items: List[Item]):
    agent = Agent(name="supply_admin", seed=ADMIN_SEED, endpoint=[])
    @AidProtocol.on_message(model=InventoryStatus)
    async def on_status(ctx: Context, sender: str, msg: InventoryStatus):
        ctx.logger.info(f"Adjust OK from {sender}: {[(i.name, i.qty) for i in msg.inventory]}")
        raise SystemExit(0)
    @AidProtocol.on_message(model=ErrorMessage)
    async def on_err(ctx: Context, sender: str, msg: ErrorMessage):
        ctx.logger.error(f"Error from {sender}: {msg.message}")
        raise SystemExit(1)
    agent.include(AidProtocol)

    async def run():
        await agent._ctx.send(target_addr, AdjustInventory(secret=secret, items=items))
        await asyncio.sleep(5)

    asyncio.create_task(run())
    agent.run()

if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--addr", required=True, help="Supplier agent address")
    p.add_argument("--secret", required=True)
    p.add_argument("--mode", choices=["restock","adjust"], required=True)
    p.add_argument("--items", required=True, help='JSON, e.g. \'[{"name":"blanket","qty":50}]\'')
    args = p.parse_args()

    items = [Item(**x) for x in json.loads(args.items)]
    if args.mode == "restock":
        asyncio.run(send_restock(args.addr, args.secret, items))
    else:
        asyncio.run(send_adjust(args.addr, args.secret, items))
