"""
Political campaigns and queries for the TFM.

Four campaigns:
  - brexit_2016     : UK referendum, June 2016
  - trump_2016      : US presidential election, November 2016
  - españa_2023     : Spanish general election (23J), July 2023
  - trump_2024      : US presidential election, November 2024

Each campaign defines:
  - date range (since/until) embedded in query strings via Twitter search syntax
  - sentiment queries: general discourse, balanced neg/neu/pos
  - stance targets + queries: specific targets with favor/against signals

Date syntax passed directly to twscrape: since:YYYY-MM-DD until:YYYY-MM-DD
"""

CAMPAIGNS: dict[str, dict] = {

    # ── Brexit 2016 ──────────────────────────────────────────────────────────
    "brexit_2016": {
        "label": "Brexit 2016",
        "lang": "en",
        "since": "2016-04-15",
        "until": "2016-06-30",
        "sentiment_queries": [
            "#Brexit since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "Brexit referendum since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "(Leave OR Remain) EU since:2016-05-01 until:2016-06-30 lang:en -filter:retweets",
        ],
        "stance_targets": {
            "leave": {
                "label": "Leave (Brexit)",
                "queries": [
                    "#VoteLeave since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "(Vote Leave OR #Brexit) since:2016-05-01 until:2016-06-30 lang:en -filter:retweets",
                    "(leave EU OR leave europe) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                ],
                "pro_signals": ["#VoteLeave", "#TakeControl", "#Brexit", "#LeaveEU"],
                "against_signals": ["#StrongerIn", "#VoteRemain", "#Remain", "#IN"],
            },
            "remain": {
                "label": "Remain (Brexit)",
                "queries": [
                    "#StrongerIn since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "#VoteRemain since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "(stay EU OR remain europe) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                ],
                "pro_signals": ["#StrongerIn", "#VoteRemain", "#Remain", "#IN", "#BetterInEurope"],
                "against_signals": ["#VoteLeave", "#TakeControl", "#LeaveEU"],
            },
        },
    },

    # ── Trump 2016 ───────────────────────────────────────────────────────────
    "trump_2016": {
        "label": "Trump 2016",
        "lang": "en",
        "since": "2016-09-01",
        "until": "2016-11-15",
        "sentiment_queries": [
            "(Trump OR Clinton) election since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "#Election2016 since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "(presidential debate OR US election 2016) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
        ],
        "stance_targets": {
            "trump": {
                "label": "Donald Trump (2016)",
                "queries": [
                    "#Trump since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#Trump2016 since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "(Donald Trump election) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                ],
                "pro_signals": ["#MAGA", "#TrumpPence16", "#VoteTrump", "#MakeAmericaGreatAgain"],
                "against_signals": ["#NeverTrump", "#TrumpIsUnfit", "#DumpTrump", "#NotMyPresident"],
            },
            "clinton": {
                "label": "Hillary Clinton (2016)",
                "queries": [
                    "#ImWithHer since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#Hillary2016 since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "(Hillary Clinton election) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                ],
                "pro_signals": ["#ImWithHer", "#Hillary2016", "#VoteHillary", "#HillaryForPresident"],
                "against_signals": ["#NeverHillary", "#CrookedHillary", "#LockHerUp", "#DeleteYourAccount"],
            },
        },
    },

    # ── España 2023 (23J) ────────────────────────────────────────────────────
    "españa_2023": {
        "label": "Elecciones Generales España 23J",
        "lang": "es",
        "since": "2023-06-20",
        "until": "2023-07-25",
        "sentiment_queries": [
            "#23J since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "#EleccionesGenerales since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "(elecciones España 2023) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "#EspañaDecide since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
        ],
        "stance_targets": {
            "psoe_sanchez": {
                "label": "PSOE / Pedro Sánchez (23J)",
                "queries": [
                    "(Sanchez OR Sánchez) elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#PSOE since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(#VotaPSOE OR #SanchezPresidente OR #SanchezFuera) since:2023-06-20 until:2023-07-25 lang:es",
                ],
                "pro_signals": ["#VotaPSOE", "#SanchezPresidente", "#PedroSanchez", "#Sanchez"],
                "against_signals": ["#SanchezFuera", "#SanchezDimision", "#SanchezMiente"],
            },
            "pp_feijoo": {
                "label": "PP / Alberto Núñez Feijóo (23J)",
                "queries": [
                    "(Feijoo OR Feijóo) elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#PartidoPopular since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(#VotaPP OR #Feijoo OR #PPFuera) since:2023-06-20 until:2023-07-25 lang:es",
                ],
                "pro_signals": ["#VotaPP", "#Feijoo", "#PartidoPopular", "#ConFeijoo"],
                "against_signals": ["#PPFuera", "#NoAlPP", "#PPCorrupcion"],
            },
            "vox_abascal": {
                "label": "Vox / Santiago Abascal (23J)",
                "queries": [
                    "Abascal elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#Vox since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(#VotaVox OR #VoxFuera OR #AbascalFuera) since:2023-06-20 until:2023-07-25 lang:es",
                ],
                "pro_signals": ["#VotaVox", "#EspañaViva", "#Vox", "#Abascal"],
                "against_signals": ["#VoxFuera", "#AbascalFuera", "#NoAVox"],
            },
        },
    },

    # ── Trump 2024 ───────────────────────────────────────────────────────────
    "trump_2024": {
        "label": "Trump 2024",
        "lang": "en",
        "since": "2024-09-01",
        "until": "2024-11-10",
        "sentiment_queries": [
            "(Trump OR Harris) election since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "#Election2024 since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "(presidential debate 2024 OR US election 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
        ],
        "stance_targets": {
            "trump": {
                "label": "Donald Trump (2024)",
                "queries": [
                    "#Trump2024 since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#MAGA since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "(Donald Trump 2024 election) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                ],
                "pro_signals": ["#MAGA", "#Trump2024", "#VoteTrump", "#TrumpWon", "#FightFightFight"],
                "against_signals": ["#NeverTrump", "#DumpTrump", "#VoteBlue", "#NotMyPresident"],
            },
            "harris": {
                "label": "Kamala Harris (2024)",
                "queries": [
                    "#KamalaHarris since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#Harris2024 since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "(Kamala Harris 2024 election) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                ],
                "pro_signals": ["#Harris2024", "#KamalaHarris", "#VoteHarris", "#WeChooseHarris"],
                "against_signals": ["#NeverKamala", "#KamalaIsUnfit", "#Kamala", "#VoteTrump"],
            },
        },
    },
}


def get_all_queries(campaigns: list[str] | None = None, task: str = "all") -> list[dict]:
    """
    Return flat list of query dicts for the requested campaigns and task type.

    Args:
        campaigns: list of campaign slugs, e.g. ["brexit_2016", "trump_2024"].
                   None = all campaigns.
        task: "sentiment" | "stance" | "all"

    Returns:
        List of dicts with keys: campaign, slug, query, task, target (None for sentiment)
    """
    selected = campaigns or list(CAMPAIGNS.keys())
    result = []

    for camp_slug in selected:
        camp = CAMPAIGNS[camp_slug]

        if task in ("sentiment", "all"):
            for i, q in enumerate(camp["sentiment_queries"]):
                result.append({
                    "campaign": camp_slug,
                    "slug": f"{camp_slug}_sentiment_{i}",
                    "query": q,
                    "task": "sentiment",
                    "target": None,
                    "lang": camp["lang"],
                })

        if task in ("stance", "all"):
            for target_slug, target in camp["stance_targets"].items():
                for i, q in enumerate(target["queries"]):
                    result.append({
                        "campaign": camp_slug,
                        "slug": f"{camp_slug}_{target_slug}_{i}",
                        "query": q,
                        "task": "stance",
                        "target": target_slug,
                        "lang": camp["lang"],
                    })

    return result
