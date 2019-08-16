"""
The recipes in the Remote Settings collection should match the Normandy API.
"""
import aiohttp


NORMANDY_URL = "{server}/api/v1/recipe/signed/"
REMOTESETTINGS_URL = "{server}/buckets/main/collections/normandy-recipes/records"


async def run(request, normandy_server, remotesettings_server):
    async with aiohttp.ClientSession() as session:
        # Recipes from source of truth.
        normandy_url = NORMANDY_URL.format(server=normandy_server)
        async with session.get(normandy_url) as response:
            normandy_recipes = await response.json()
        # Recipes published on Remote Settings.
        remotesettings_url = REMOTESETTINGS_URL.format(server=remotesettings_server)
        async with session.get(remotesettings_url) as response:
            body = await response.json()
            remotesettings_recipes = body["data"]

    remotesettings_by_id = {r["id"]: r["recipe"] for r in remotesettings_recipes}
    normandy_by_id = {str(r["recipe"]["id"]): r["recipe"] for r in normandy_recipes}

    missing = []
    for rid, r in normandy_by_id.items():
        r = remotesettings_by_id.pop(rid, None)
        if r is None:
            missing.append({"id": r["id"], "name": r["name"]})
    extras = [{"id": r["id"], "name": r["name"]} for r in remotesettings_by_id.values()]

    ok = (len(missing) + len(extras)) == 0
    return ok, {"missing": missing, "extras": extras}
