from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

api_id = "28037185"      # ← сюда свой ID
api_hash = '7e1d7cea64520aa9cacc19b1dc3d8484' # ← сюда свой hash

client = TelegramClient('session_name', api_id, api_hash)

async def dump_channel_messages(channel_username):
    await client.start()
    entity = await client.get_entity(channel_username)

    messages = []
    offset_id = 0
    limit = 100

    while True:
        history = await client(GetHistoryRequest(
            peer=entity,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        for message in history.messages:
            messages.append(message.message)

        offset_id = history.messages[-1].id

    return messages

with client:
    channel_usernames = [
    "strela_life2", "banksta", "criminallru", "ebitdaebitda", "bbbreaking",
    "boilerroomchannel", "Jelezobetonniyzames", "proeconomics", "Burovaia", "FatCat18",
     "belaya_kaska", "mamkinfinansist", "karaulny_accountant", 
    "vchk_gpu", "blablanomika", "rzd_partner_news", "Vgudok", "rzdfiles",
    "inflation_shock", "olegderipaska"
]  

    for username in channel_usernames:
        messages = client.loop.run_until_complete(dump_channel_messages(username))
        print(f"--- {username} ---")
        for msg in messages[:10]:  # покажем первые 10
            print(f"[{username}] {msg}")
        print("\n")
