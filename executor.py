import re
from difflib import SequenceMatcher


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text):

    text = str(text or "").lower()

    # OCR correction
    text = text.replace("0", "o")

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def strict_normalize(text):

    text = str(text or "").lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "found",
    "date",
    "near",
    "thank",
    "thanks",
    "item",
    "contact",
    "phone",
    "please",
    "belongs",
    "belong",
    "this",
    "that",
    "the",
    "and",
    "you",
    "your",
    "to",
    "me",
    "at",
    "on",
    "is",
    "if",
    "for",
    "a",
    "an",
    "of",
    "in",
    "last",
    "seen",
    "located",
    "location",
    "bench",
    "there",
    "have",
    "has",
    "with",
    "call"
}


# ============================================================
# TOKENS
# ============================================================

def tokens(text):

    result = set()

    for token in strict_normalize(text).split():

        if (
            len(token) >= 2
            and token not in STOP_WORDS
        ):

            result.add(token)

    return result


# ============================================================
# SIMILARITY
# ============================================================

def similarity(a, b):

    a = normalize(a)
    b = normalize(b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


# ============================================================
# PHONE
# ============================================================

def extract_phone(text):

    text = str(text or "")

    matches = re.findall(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        text
    )

    if matches:

        phone = re.sub(
            r"\D",
            "",
            matches[0]
        )

        if (
            phone.startswith("91")
            and len(phone) == 12
        ):

            phone = phone[2:]

        return phone

    matches = re.findall(
        r"(?<!\d)\d{10,15}(?!\d)",
        text
    )

    if matches:

        return matches[0]

    return ""


# ============================================================
# EMAIL
# ============================================================

def extract_email(text):

    match = re.search(
        r"\b[a-zA-Z0-9._%+-]+"
        r"@[a-zA-Z0-9.-]+"
        r"\.[a-zA-Z]{2,}\b",
        str(text or "")
    )

    if match:

        return match.group(0).lower()

    return ""


# ============================================================
# DATE
# ============================================================

def extract_date(text):

    text = str(text or "")

    patterns = [

        r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b",

        r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b",

        r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if not match:
            continue

        groups = match.groups()

        if len(groups[0]) == 4:

            year = int(groups[0])
            month = int(groups[1])
            day = int(groups[2])

        else:

            day = int(groups[0])
            month = int(groups[1])
            year = int(groups[2])

        if not (
            1 <= month <= 12
            and
            1 <= day <= 31
            and
            1900 <= year <= 2100
        ):

            continue

        return (
            f"{year:04d}-"
            f"{month:02d}-"
            f"{day:02d}"
        )

    return ""


# ============================================================
# IDENTIFIERS
# ============================================================

def extract_identifiers(text):

    identifiers = set()

    email = extract_email(text)

    if email:

        identifiers.add(
            email
        )

    phone = extract_phone(text)

    if phone:

        identifiers.add(
            phone
        )

    raw = strict_normalize(
        text
    )

    numbers = re.findall(
        r"\b\d{6,15}\b",
        raw
    )

    identifiers.update(
        numbers
    )

    codes = re.findall(
        r"\b[a-z]{1,5}\d{2,}[a-z0-9]*\b",
        raw
    )

    identifiers.update(
        codes
    )

    return identifiers


# ============================================================
# LOCATION NORMALIZATION
# ============================================================

def normalize_location(text):

    if not text:
        return ""

    text = str(text).lower()

    replacements = [
        "near",
        "found at",
        "found",
        "location",
        "at",
        "on the",
        "the",
        "bench",
        "beside",
        "inside",
        "outside",
        "in"
    ]

    for word in replacements:

        text = re.sub(
            r"\b" + re.escape(word) + r"\b",
            " ",
            text
        )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# LOCATION SIMILARITY
# ============================================================

def location_similarity(
    found_location,
    lost_location
):

    found = normalize_location(
        found_location
    )

    lost = normalize_location(
        lost_location
    )

    if not found or not lost:

        return 0.0

    if found == lost:

        return 1.0

    found_tokens = set(
        found.split()
    )

    lost_tokens = set(
        lost.split()
    )

    if not found_tokens or not lost_tokens:

        return 0.0

    common = (
        found_tokens
        &
        lost_tokens
    )

    overlap = (
        len(common)
        /
        min(
            len(found_tokens),
            len(lost_tokens)
        )
    )

    sequence_score = SequenceMatcher(
        None,
        found,
        lost
    ).ratio()

    return max(
        overlap,
        sequence_score
    )


# ============================================================
# DESCRIPTION SCORE
# ============================================================

def description_score(
    found_text,
    lost_description
):

    if not lost_description:

        return 0.0

    found_tokens = tokens(
        found_text
    )

    description_tokens = tokens(
        lost_description
    )

    if (
        not found_tokens
        or
        not description_tokens
    ):

        return 0.0

    common = (
        found_tokens
        &
        description_tokens
    )

    if not common:

        return 0.0

    return min(
        len(common) * 3,
        10
    )


# ============================================================
# PREPARE DATABASE ITEM
# ============================================================

def prepare_item(item):

    owner = str(
        item.get(
            "owner_name",
            ""
        )
    )

    item_name = str(
        item.get(
            "item_name",
            ""
        )
    )

    description = str(
        item.get(
            "description",
            ""
        )
    )

    contact = str(
        item.get(
            "contact",
            ""
        )
    )

    location = str(
        item.get(
            "location",
            ""
        )
    )

    date_lost = str(
        item.get(
            "date_lost",
            ""
        )
    )

    searchable = " ".join(
        [
            item_name,
            description,
            location
        ]
    )

    prepared = dict(item)

    prepared["_owner"] = owner
    prepared["_item"] = item_name
    prepared["_description"] = description
    prepared["_contact"] = contact
    prepared["_location"] = location
    prepared["_date"] = date_lost

    prepared["_normalized"] = normalize(
        searchable
    )

    prepared["_tokens"] = tokens(
        searchable
    )

    prepared["_phone"] = extract_phone(
        contact
    )

    prepared["_email"] = extract_email(
        contact
    )

    prepared["_date_normalized"] = extract_date(
        date_lost
    )

    return prepared


# ============================================================
# SCORE MATCH
# ============================================================

def score_match(
    ocr_text,
    item,
    information=None
):

    if not ocr_text and not information:

        return 0.0

    if information is None:

        information = {}

    # --------------------------------------------------------
    # FOUND ITEM INFORMATION
    # --------------------------------------------------------

    found_item = str(
        information.get(
            "item",
            ""
        )
    ).strip()

    found_location = str(
        information.get(
            "location",
            ""
        )
    ).strip()

    found_date = extract_date(
        information.get(
            "date",
            ""
        )
    )

    # --------------------------------------------------------
    # DATABASE INFORMATION
    # --------------------------------------------------------

    db_item = str(
        item.get(
            "_item",
            ""
        )
    ).strip()

    db_description = str(
        item.get(
            "_description",
            ""
        )
    ).strip()

    db_location = str(
        item.get(
            "_location",
            ""
        )
    ).strip()

    db_date = str(
        item.get(
            "_date_normalized",
            ""
        )
    ).strip()

    score = 0.0

    # ========================================================
    # 1. ITEM NAME
    # ========================================================

    if found_item and db_item:

        item_similarity = similarity(
            found_item,
            db_item
        )

        if item_similarity >= 0.92:

            score += 55

        elif item_similarity >= 0.75:

            score += 42

        elif item_similarity >= 0.55:

            score += 25

    # ========================================================
    # 2. LOCATION
    # ========================================================

    if found_location and db_location:

        loc_similarity = location_similarity(
            found_location,
            db_location
        )

        if loc_similarity >= 0.85:

            score += 25

        elif loc_similarity >= 0.65:

            score += 18

        elif loc_similarity >= 0.45:

            score += 10

    # ========================================================
    # 3. DESCRIPTION
    # ========================================================

    score += description_score(
        ocr_text,
        db_description
    )

    # ========================================================
    # 4. DATE
    # ========================================================

    if (
        found_date
        and
        db_date
        and
        found_date == db_date
    ):

        score += 10

    # ========================================================
    # 5. ITEM TOKEN MATCH
    # ========================================================

    if found_item:

        found_item_tokens = tokens(
            found_item
        )

        db_item_tokens = tokens(
            db_item
        )

        common_item_tokens = (
            found_item_tokens
            &
            db_item_tokens
        )

        if common_item_tokens:

            score += min(
                len(common_item_tokens) * 2,
                5
            )

    return round(
        min(
            score,
            100
        ),
        1
    )


# ============================================================
# FIND MATCHES
# ============================================================

def find_matches(
    ocr_text,
    items,
    minimum_score=35,
    information=None
):

    matches = []

    if information is None:

        information = {}

    prepared_items = [
        prepare_item(item)
        for item in items
    ]

    for item in prepared_items:

        found_item = str(
            information.get(
                "item",
                ""
            )
        ).strip()

        # ----------------------------------------------------
        # Require reasonable item similarity
        # ----------------------------------------------------

        if found_item:

            item_similarity = similarity(
                found_item,
                item.get(
                    "_item",
                    ""
                )
            )

            if item_similarity < 0.45:

                continue

        # ----------------------------------------------------
        # Calculate score
        # ----------------------------------------------------

        score = score_match(
            ocr_text,
            item,
            information
        )

        if score < minimum_score:

            continue

        # ----------------------------------------------------
        # Create clean result
        # ----------------------------------------------------

        result = dict(item)

        internal_fields = [
            "_owner",
            "_item",
            "_description",
            "_contact",
            "_location",
            "_date",
            "_normalized",
            "_tokens",
            "_phone",
            "_email",
            "_date_normalized"
        ]

        for key in internal_fields:

            result.pop(
                key,
                None
            )

        # ----------------------------------------------------
        # Use ONE standard key
        # ----------------------------------------------------

        result["match_score"] = score

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if score >= 90:

            result["status"] = (
                "Strong Match"
            )

        elif score >= 60:

            result["status"] = (
                "Possible Match"
            )

        else:

            result["status"] = (
                "Weak Match"
            )

        matches.append(
            result
        )

    # ========================================================
    # SORT
    # ========================================================

    matches.sort(
        key=lambda x:
        x.get(
            "match_score",
            0
        ),
        reverse=True
    )

    return matches[:10]