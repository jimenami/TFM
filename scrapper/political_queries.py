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
            "#EUref since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "(European Union referendum OR EU vote) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "(Brexit vote OR Brexit campaign) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "(Nigel Farage OR Boris Johnson OR David Cameron) Brexit since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "#UKinEU since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "(immigration Brexit OR sovereignty Brexit) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
            "(NHS Brexit OR economy Brexit OR trade Brexit) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
        ],
        "stance_targets": {
            "leave": {
                "label": "Leave (Brexit)",
                "queries": [
                    "#VoteLeave since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "#LeaveEU since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "(Vote Leave OR leave campaign) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "(leave EU OR leave europe OR Brexit leave) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "#TakeControl since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "(take back control OR sovereignty EU) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                ],
                "pro_signals": ["#VoteLeave", "#TakeControl", "#Brexit", "#LeaveEU", "#BetterOffOut"],
                "against_signals": ["#StrongerIn", "#VoteRemain", "#Remain", "#IN"],
            },
            "remain": {
                "label": "Remain (Brexit)",
                "queries": [
                    "#StrongerIn since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "#VoteRemain since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "#Remain since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "(stay EU OR remain europe OR stay in EU) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "#BetterInEurope since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
                    "(remain campaign OR pro-EU OR pro EU) since:2016-04-15 until:2016-06-30 lang:en -filter:retweets",
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
            "#USElection2016 since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "(American politics 2016 OR vote 2016) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "(swing state OR battleground state 2016) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "(Republican Democratic nominee 2016) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "(WikiLeaks election OR FBI Clinton) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "(White House 2016 OR president 2016) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
            "(debate Trump Clinton 2016) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
        ],
        "stance_targets": {
            "trump": {
                "label": "Donald Trump (2016)",
                "queries": [
                    "#Trump since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#Trump2016 since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#MAGA since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "(Donald Trump election president) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#MakeAmericaGreatAgain since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#TrumpPence16 since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#NeverTrump since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "(Trump wall OR Trump immigration OR Trump trade) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                ],
                "pro_signals": ["#MAGA", "#TrumpPence16", "#VoteTrump", "#MakeAmericaGreatAgain", "#Trump2016"],
                "against_signals": ["#NeverTrump", "#TrumpIsUnfit", "#DumpTrump", "#NotMyPresident"],
            },
            "clinton": {
                "label": "Hillary Clinton (2016)",
                "queries": [
                    "#ImWithHer since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#Hillary2016 since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#HillaryForPresident since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "(Hillary Clinton election president) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#CrookedHillary since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#LockHerUp since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "#NeverHillary since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
                    "(Clinton email OR Clinton foundation OR Clinton scandal) since:2016-09-01 until:2016-11-15 lang:en -filter:retweets",
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
            "#EleccionesGenerales23 since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "(campaña electoral España 2023) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "(debate electoral 2023 OR debate TV elecciones) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "(gobierno España 2023 OR coalicion OR investidura) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "(voto España OR urnas 23J OR jornada electoral) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "#VotaEspaña since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "(política española 2023 OR Congreso diputados 2023) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
            "(economía España elecciones OR inflación España 2023) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
        ],
        "stance_targets": {
            "psoe_sanchez": {
                "label": "PSOE / Pedro Sánchez (23J)",
                "queries": [
                    "(Sanchez OR Sánchez) elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#PSOE since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#VotaPSOE since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#SanchezPresidente since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#SanchezFuera since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#SanchezDimision since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(Pedro Sanchez presidente OR Pedro Sanchez gobierno) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(PSOE coalicion OR PSOE Podemos OR PSOE Sumar) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                ],
                "pro_signals": ["#VotaPSOE", "#SanchezPresidente", "#PedroSanchez", "#Sanchez", "#PSOE"],
                "against_signals": ["#SanchezFuera", "#SanchezDimision", "#SanchezMiente", "#NoPSOE"],
            },
            "pp_feijoo": {
                "label": "PP / Alberto Núñez Feijóo (23J)",
                "queries": [
                    "(Feijoo OR Feijóo) elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#PartidoPopular since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#VotaPP since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#Feijoo since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#PPFuera since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#PPCorrupcion since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(Feijoo presidente OR PP gobierno OR PP mayoria) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(PP Vox pacto OR PP derecha OR PP coalicion) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                ],
                "pro_signals": ["#VotaPP", "#Feijoo", "#PartidoPopular", "#ConFeijoo", "#PPGana"],
                "against_signals": ["#PPFuera", "#NoAlPP", "#PPCorrupcion", "#FeijooMiente"],
            },
            "vox_abascal": {
                "label": "Vox / Santiago Abascal (23J)",
                "queries": [
                    "Abascal elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#Vox since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#VotaVox since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#VoxFuera since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#AbascalFuera since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(Vox extrema derecha OR Vox ultraderecha) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(Abascal presidente OR Vox gobierno OR Vox PP) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#EspañaViva since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                ],
                "pro_signals": ["#VotaVox", "#EspañaViva", "#Vox", "#Abascal", "#VoxEspaña"],
                "against_signals": ["#VoxFuera", "#AbascalFuera", "#NoAVox", "#StopVox"],
            },
            "sumar_diaz": {
                "label": "Sumar / Yolanda Díaz (23J) — incluye Podemos (Ione Belarra)",
                "queries": [
                    "Sumar elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#Sumar since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#VotaSumar since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#YolandaDiaz since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(Yolanda Diaz OR Yolanda Díaz) elecciones since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "(Podemos Sumar OR izquierda unida Sumar) since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                    "#SumarFuera since:2023-06-20 until:2023-07-25 lang:es -filter:retweets",
                ],
                "pro_signals": ["#VotaSumar", "#YolandaDiaz", "#Sumar", "#SumarGana"],
                "against_signals": ["#SumarFuera", "#NoASumar"],
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
            "#USElection2024 since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "(vote 2024 OR American election 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "(swing state 2024 OR battleground 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "(Republican Democrat 2024 OR White House 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "(abortion economy immigration 2024 election) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "(debate Harris Trump 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
            "(early voting 2024 OR election day 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
        ],
        "stance_targets": {
            "trump": {
                "label": "Donald Trump (2024)",
                "queries": [
                    "#Trump2024 since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#MAGA since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#VoteTrump since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "(Donald Trump 2024 president) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#TrumpVance2024 since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#NeverTrump since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#FightFightFight since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "(Trump rally OR Trump speech OR Trump policy 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                ],
                "pro_signals": ["#MAGA", "#Trump2024", "#VoteTrump", "#TrumpWon", "#FightFightFight", "#TrumpVance2024"],
                "against_signals": ["#NeverTrump", "#DumpTrump", "#VoteBlue", "#NotMyPresident", "#TrumpIsUnfit"],
            },
            "harris": {
                "label": "Kamala Harris (2024)",
                "queries": [
                    "#KamalaHarris since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#Harris2024 since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#VoteHarris since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "(Kamala Harris president 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#WeChooseHarris since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#HarrisWalz since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "#NeverKamala since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                    "(Harris policy OR Harris speech OR Harris rally 2024) since:2024-09-01 until:2024-11-10 lang:en -filter:retweets",
                ],
                "pro_signals": ["#Harris2024", "#KamalaHarris", "#VoteHarris", "#WeChooseHarris", "#HarrisWalz"],
                "against_signals": ["#NeverKamala", "#KamalaIsUnfit", "#VoteTrump", "#KamalaFailed"],
            },
        },
    },
}


def get_all_queries(
    campaigns: list[str] | None = None,
    task: str = "all",
    targets: list[str] | None = None,
) -> list[dict]:
    """
    Return flat list of query dicts for the requested campaigns and task type.

    Args:
        campaigns: list of campaign slugs, e.g. ["brexit_2016", "trump_2024"].
                   None = all campaigns.
        task: "sentiment" | "stance" | "all"
        targets: list of stance target slugs to include, e.g. ["sumar_diaz"].
                 None = all targets. Only applies when task includes "stance".

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
                if targets and target_slug not in targets:
                    continue
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
