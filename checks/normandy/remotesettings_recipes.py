"""
The recipes in the Remote Settings collection should match the Normandy API. The
collection of recipes with capabilities should contain all baseline recipes.

The lists of missing and extraneous recipes are returned for the baseline and
capabilities collections.
"""
import random

from telescope.typings import CheckResult
from telescope.utils import fetch_json


NORMANDY_URL = "{server}/api/v1/recipe/signed/?enabled=1&only_baseline_capabilities={baseline_only}"
REMOTESETTINGS_URL = (
    "{server}/buckets/main/collections/{cid}/changeset?_expected={expected}"
)


def compare_recipes_lists(a, b):
    """
    Return list of recipes present in `a` and missing in `b`, and present in `b` and missing in `a`.
    """
    a_by_id = {r["recipe"]["id"]: r["recipe"] for r in a}
    b_by_id = {r["recipe"]["id"]: r["recipe"] for r in b}
    missing = []
    for rid, r in a_by_id.items():
        r_in_b = b_by_id.pop(rid, None)
        if r_in_b is None:
            missing.append({"id": r["id"], "name": r["name"]})
    extras = [{"id": r["id"], "name": r["name"]} for r in b_by_id.values()]
    return missing, extras


async def run(normandy_server: str, remotesettings_server: str) -> CheckResult:
    # Baseline recipes from source of truth.
    normandy_url_baseline = NORMANDY_URL.format(server=normandy_server, baseline_only=1)
    normandy_recipes_baseline = await fetch_json(normandy_url_baseline)
    # Recipes with capabilities
    normandy_url_caps = NORMANDY_URL.format(server=normandy_server, baseline_only=0)
    normandy_recipes_caps = await fetch_json(normandy_url_caps)

    # Baseline recipes published on Remote Settings.
    rs_recipes_baseline_url = REMOTESETTINGS_URL.format(
        server=remotesettings_server,
        cid="normandy-recipes",
        expected=random.randint(999999000000, 999999999999),
    )
    rs_recipes_baseline = (await fetch_json(rs_recipes_baseline_url))["changes"]
    # Recipes with advanced capabilities.
    rs_recipes_caps_urls = REMOTESETTINGS_URL.format(
        server=remotesettings_server,
        cid="normandy-recipes-capabilities",
        expected=random.randint(999999000000, 999999999999),
    )
    rs_recipes_caps = (await fetch_json(rs_recipes_caps_urls))["changes"]

    # Make sure the baseline recipes are all listed in the baseline collection
    missing_baseline, extras_baseline = compare_recipes_lists(
        normandy_recipes_baseline, rs_recipes_baseline
    )
    # Make sure the baseline recipes are all listed in the baseline collection
    missing_caps, extras_caps = compare_recipes_lists(
        normandy_recipes_caps, rs_recipes_caps
    )

    ok = (
        len(missing_baseline)
        + len(missing_caps)
        + len(extras_baseline)
        + len(extras_caps)
    ) == 0
    data = {
        "baseline": {"missing": missing_baseline, "extras": extras_baseline},
        "capabilities": {"missing": missing_caps, "extras": extras_caps},
    }
    return ok, data
