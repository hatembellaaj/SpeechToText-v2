"""
Vocabulaire Thermor — noms de produits, concurrents et distributeurs.
Utilisé comme initial_prompt pour Whisper afin d'améliorer la reconnaissance
des termes techniques et noms de marques.
"""

# ── Produits Thermor (nomenclature 2025) ─────────────────────────────────────
THERMOR_PRODUCTS = [
    # Radiateurs chaleur douce
    "Mythik", "Équateur 4", "Équateur 5", "Bilbao 4", "Ovation 3",
    "Kenya 4", "Ingénio 4", "Baléares 2", "Ténérife", "Amadeus 3",
    "Évidence 2", "Mozaïk",
    # Sèche-serviettes
    "Symphonik", "Allure Virtuose", "Allure Classique", "Riviera 2",
    "Riva 4", "Riva 5", "Corsaire 2", "Majorque", "Illico 3", "Toscane",
    # Chauffe-eau thermodynamique
    "Aéromax Split 3", "Aéromax 6", "Aéromax 5", "Aéromax Access",
    "Aéromax Piscine 2",
    # PAC air-eau
    "Auréa", "Auréa Compact", "Aérolia 2", "Aérolia 2 Duo", "Aérolia 1 Duo",
    # PAC air-air
    "Nagano Gainable",
    # Chauffe-eau électrique
    "Stéatis", "Malicio 3", "Duralis Connect", "Duralis", "Inoxis",
    "Blindé", "Ristretto",
    # Chauffage tertiaire
    "Airtherm Digital",
]

# ── Familles de produits ──────────────────────────────────────────────────────
THERMOR_FAMILIES = [
    "radiateur chaleur douce", "sèche-serviettes électrique",
    "chauffe-eau thermodynamique", "chauffe-eau électrique",
    "PAC air-eau", "PAC air-air", "pompe à chaleur",
    "chauffage tertiaire", "ballon thermodynamique",
]

# ── Concurrents ───────────────────────────────────────────────────────────────
COMPETITORS = [
    "Daikin", "Altherma", "Atlantic", "Alfea", "Viessmann", "Vitocal",
    "Mitsubishi Electric", "Ecodan", "De Dietrich", "Alezio",
    "Saunier Duval", "GeniaAir", "Bosch", "Compress", "Panasonic", "Aquarea",
    "Hitachi", "Yutaki", "Ariston", "Nuos", "Lydos",
    "Acova", "Sauter", "Intuis", "Haier", "Aldes",
]

# ── Termes métier call center Thermor ─────────────────────────────────────────
BUSINESS_TERMS = [
    "installateur", "chantier", "mise en service", "dimensionnement",
    "devis", "SAV", "garantie", "numéro de série", "référence produit",
    "commande", "livraison", "distributeur", "grossiste",
    "thermostat connecté", "Cozytouch", "application Thermor",
    "PAC", "pompe à chaleur", "CET", "VMC", "ECS",
    "R290", "R32", "fluide frigorigène",
    "kWh", "COP", "SCOP", "ERP",
    "churn", "conquête", "cross-sell",
]


def build_whisper_initial_prompt() -> str:
    """
    Construit un prompt initial pour Whisper qui améliore la reconnaissance
    des noms de produits, marques et termes techniques Thermor.
    """
    all_terms = THERMOR_PRODUCTS + COMPETITORS + BUSINESS_TERMS
    # Whisper utilise le prompt initial pour calibrer le vocabulaire attendu
    return (
        "Conversation téléphonique entre un conseiller Thermor et un installateur professionnel. "
        "Produits mentionnés : " + ", ".join(THERMOR_PRODUCTS[:20]) + ". "
        "Concurrents possibles : " + ", ".join(COMPETITORS[:10]) + "."
    )


# ── Référentiel des typologies clients Thermor (Lot 1) ───────────────────────
THERMOR_PROFILES = [
    {
        "name": "Conquête",
        "description": (
            "Non-client Thermor effectuant son premier achat (toutes familles). "
            "L'installateur n'a jamais travaillé avec Thermor ou découvre la marque pour la première fois. "
            "Il pose des questions de base sur les produits, les prix, les démarches pour référencer Thermor. "
            "Verbatim typique : 'je n'ai jamais référencé vos produits', 'un confrère m'a recommandé Thermor', "
            "'par où je commence ?', 'comment faire pour passer commande ?'"
        ),
        "keywords": "premier achat, nouveau client, référencement, découverte, jamais commandé",
        "color": "#10B981",
        "order": 1,
        "is_neutral": False,
    },
    {
        "name": "Change",
        "description": (
            "Client Thermor existant sur certaines familles de produits, qui démarre sur une nouvelle famille. "
            "Il installe déjà des produits Thermor (ex. radiateurs) mais aborde une nouvelle famille (ex. PAC air-air). "
            "Il a donc une relation avec Thermor mais pas d'expérience sur cette famille spécifique. "
            "Verbatim typique : 'je pose vos radiateurs depuis des années', 'j'ai jamais installé de PAC', "
            "'c'est ma première pompe à chaleur avec vous', 'vous avez une formation mise en service ?'"
        ),
        "keywords": "nouvelle famille, première installation, formation, montée en gamme",
        "color": "#3B82F6",
        "order": 2,
        "is_neutral": False,
    },
    {
        "name": "Cross sell",
        "description": (
            "Installateur déjà actif sur une famille de produits mais chez un concurrent, "
            "qui démarre cette famille avec Thermor. Il maîtrise la technicité mais veut changer de marque. "
            "Souvent motivé par des problèmes SAV chez le concurrent, ou par les recommandations d'un pair. "
            "Verbatim typique : 'j'installe des PAC air-eau depuis 3 ans mais j'étais chez un concurrent', "
            "'j'ai eu des retours SAV qui me posent problème', 'j'aimerais tester votre gamme Aérolia', "
            "'je maîtrise la famille, je cherche un partenaire plus fiable'"
        ),
        "keywords": "changement de marque, concurrent, SAV concurrent, tester Thermor, migration",
        "color": "#8B5CF6",
        "order": 3,
        "is_neutral": False,
    },
    {
        "name": "Hausse d'usage",
        "description": (
            "Client Thermor existant dont la part d'achats Thermor augmente sur une ou plusieurs familles. "
            "Il est satisfait et accroît sa fidélité à la marque, réduit sa part concurrente. "
            "Il peut demander de meilleures conditions commerciales en échange de volumes plus importants. "
            "Verbatim typique : 'j'ai vraiment augmenté la part de Thermor sur mes chantiers', "
            "'vos modèles connectés, les clients adorent', 'j'ai quasiment arrêté de proposer les autres', "
            "'qu'est-ce que vous pouvez faire pour moi en termes de conditions ?'"
        ),
        "keywords": "augmentation volume, fidélisation, satisfaction, conditions commerciales, croissance",
        "color": "#F59E0B",
        "order": 4,
        "is_neutral": False,
    },
    {
        "name": "Baisse d'usage",
        "description": (
            "Client Thermor existant dont la part d'achats Thermor diminue sur une ou plusieurs familles. "
            "Il s'oriente vers des concurrents, souvent pour des raisons de prix ou d'insatisfaction partielle. "
            "Il reste encore client Thermor mais montre des signaux de désengagement progressif. "
            "Verbatim typique : 'j'ai un peu réduit Thermor ces derniers mois', "
            "'un concurrent m'a fait une remise intéressante', 'j'ai suivi pour cette famille', "
            "'c'est uniquement une question de prix', 'moins convaincu sur cette gamme'"
        ),
        "keywords": "réduction volume, concurrent moins cher, remise, insatisfaction partielle, désengagement",
        "color": "#EF4444",
        "order": 5,
        "is_neutral": False,
    },
    {
        "name": "Churn",
        "description": (
            "Client qui a arrêté ou envisage d'arrêter complètement Thermor sur une famille ou toutes les familles. "
            "Insatisfaction forte, souvent liée à des problèmes SAV répétés, une perte de confiance, "
            "ou un passage définitif à un concurrent. La relation commerciale est rompue ou en voie de l'être. "
            "Verbatim typique : 'ça fait 6 mois que je n'ai plus commandé chez vous', "
            "'j'ai eu deux retours SAV compliqués', 'j'ai perdu confiance', "
            "'j'ai basculé sur une autre marque', 'je ne travaille plus avec Thermor'"
        ),
        "keywords": "arrêt commandes, perte confiance, SAV problème, basculé concurrent, rupture relation",
        "color": "#DC2626",
        "order": 6,
        "is_neutral": False,
    },
    {
        "name": "Non catégorisé",
        "description": (
            "Le comportement du client ne correspond clairement à aucun des 6 profils définis. "
            "La conversation est trop courte, hors-sujet, ou ne contient pas assez d'éléments "
            "pour identifier une intention commerciale ou un comportement d'achat spécifique. "
            "Exemples : demande purement administrative, question technique sans contexte commercial, "
            "appel mal orienté, conversation trop courte."
        ),
        "keywords": "neutre, indéterminé, hors sujet, question technique, administratif",
        "color": "#9CA3AF",
        "order": 7,
        "is_neutral": True,
    },
]
