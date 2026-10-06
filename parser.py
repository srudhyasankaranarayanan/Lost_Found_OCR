import cv2
import numpy as np
import easyocr
import re


# =========================================================
# EASY OCR READER
# =========================================================

reader = easyocr.Reader(
    ["en"],
    gpu=False,
    verbose=False
)


# =========================================================
# IMAGE DECODING
# =========================================================

def _decode_image(image_bytes):

    array = np.frombuffer(
        image_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            "The uploaded image could not be read."
        )

    return image


# =========================================================
# RESIZE IMAGE
# =========================================================

def _resize_image(image, max_size=1400):

    height, width = image.shape[:2]

    largest_side = max(height, width)

    if largest_side <= max_size:
        return image

    scale = max_size / largest_side

    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def _make_variants(image):

    original = image

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    return [
        original,
        enhanced
    ]


# =========================================================
# CLEAN OCR TEXT
# =========================================================

def _clean_line(text):

    text = str(text)

    text = text.replace("—", "-")
    text = text.replace("–", "-")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# FIELD LABELS
# =========================================================

FIELD_LABELS = [
    "owner",
    "owner name",
    "belongs to",

    "item",
    "item name",
    "lost item",
    "object",

    "description",
    "details",
    "item description",
    "about",

    "contact",
    "contact person",
    "phone",
    "mobile",

    "found by",
    "finder",
    "finder name",
    "reported by",

    "found at",
    "found location",
    "location",
    "last seen",
    "place found",
    "found near",

    "date",
    "date lost",
    "date found",

    "id",
    "id number",
    "serial",
    "serial number",
    "registration",
    "registration number",
    "roll number",
    "student id",
    "reference",
    "reference number"
]


# =========================================================
# CHECK FIELD LABEL
# =========================================================

def _is_field_label(line):

    clean = line.lower().strip()
    clean = clean.rstrip(":")

    for label in FIELD_LABELS:

        if clean == label:
            return True

    return False


# =========================================================
# GET LABEL AND VALUE
# =========================================================

def _get_label_and_value(line):

    clean = line.strip()

    sorted_labels = sorted(
        FIELD_LABELS,
        key=len,
        reverse=True
    )

    for label in sorted_labels:

        pattern = (
            r"^"
            + re.escape(label)
            + r"\s*:\s*(.*)$"
        )

        match = re.match(
            pattern,
            clean,
            flags=re.IGNORECASE
        )

        if match:

            colon_index = clean.find(":")

            if colon_index >= 0:

                value = clean[
                    colon_index + 1:
                ].strip()

                return label, value

    return None, None


# =========================================================
# EXTRACT MULTI-LINE VALUE
# =========================================================

def _extract_multiline_value(
    lines,
    labels
):

    labels_lower = [
        label.lower()
        for label in labels
    ]

    for i, line in enumerate(lines):

        clean = line.strip()
        lower = clean.lower()

        for label in labels_lower:

            # -----------------------------------------
            # Example:
            # Item: Scooter Key
            # -----------------------------------------

            pattern = (
                r"^"
                + re.escape(label)
                + r"\s*:\s*(.*)$"
            )

            match = re.match(
                pattern,
                lower,
                flags=re.IGNORECASE
            )

            if match:

                colon_index = clean.find(":")

                if colon_index == -1:
                    continue

                value = clean[
                    colon_index + 1:
                ].strip()

                collected = []

                if value:
                    collected.append(value)

                # -------------------------------------
                # Collect continuation lines
                # -------------------------------------

                j = i + 1

                while j < len(lines):

                    next_line = lines[j].strip()

                    if not next_line:
                        j += 1
                        continue

                    if _is_field_label(
                        next_line
                    ):
                        break

                    next_label, _ = (
                        _get_label_and_value(
                            next_line
                        )
                    )

                    if next_label:
                        break

                    if re.fullmatch(
                        r"[6-9]\d{9}",
                        next_line
                    ):
                        break

                    if _normalize_date(
                        next_line
                    ):
                        break

                    collected.append(
                        next_line
                    )

                    j += 1

                    if len(collected) >= 3:
                        break

                if collected:

                    return " ".join(
                        collected
                    ).strip()

                return None

            # -----------------------------------------
            # Example:
            #
            # Item:
            # Scooter
            # Key
            # -----------------------------------------

            if lower.rstrip(":") == label:

                collected = []

                j = i + 1

                while j < len(lines):

                    next_line = lines[j].strip()

                    if not next_line:
                        j += 1
                        continue

                    if _is_field_label(
                        next_line
                    ):
                        break

                    next_label, _ = (
                        _get_label_and_value(
                            next_line
                        )
                    )

                    if next_label:
                        break

                    if re.fullmatch(
                        r"[6-9]\d{9}",
                        next_line
                    ):
                        break

                    if _normalize_date(
                        next_line
                    ):
                        break

                    collected.append(
                        next_line
                    )

                    j += 1

                    if len(collected) >= 3:
                        break

                if collected:

                    return " ".join(
                        collected
                    ).strip()

    return None


# =========================================================
# NORMALIZE DATE
# =========================================================

def _normalize_date(value):

    if not value:
        return None

    value = str(value).strip()

    value = value.replace(
        "—",
        "-"
    )

    value = value.replace(
        "–",
        "-"
    )

    value = value.replace(
        "_",
        "-"
    )

    value = re.sub(
        r"\s*[-/.]\s*",
        "-",
        value
    )

    value = re.sub(
        r"(\d{1,2})\s+"
        r"(\d{1,2})\s+"
        r"(\d{4})",
        r"\1-\2-\3",
        value
    )

    # DD-MM-YYYY

    match = re.search(
        r"\b(\d{1,2})-"
        r"(\d{1,2})-"
        r"(\d{4})\b",
        value
    )

    if match:

        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        if (
            1 <= day <= 31
            and
            1 <= month <= 12
        ):

            return (
                f"{day:02d}-"
                f"{month:02d}-"
                f"{year}"
            )

    # YYYY-MM-DD

    match = re.search(
        r"\b(\d{4})-"
        r"(\d{1,2})-"
        r"(\d{1,2})\b",
        value
    )

    if match:

        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        if (
            1 <= day <= 31
            and
            1 <= month <= 12
        ):

            return (
                f"{day:02d}-"
                f"{month:02d}-"
                f"{year}"
            )

    return None


# =========================================================
# EXTRACT DATE
# =========================================================

def _extract_date(
    lines,
    full_text
):

    date = _extract_multiline_value(
        lines,
        [
            "date",
            "date lost",
            "date found"
        ]
    )

    if date:

        normalized = _normalize_date(
            date
        )

        if normalized:
            return normalized

    for line in lines:

        date = _normalize_date(
            line
        )

        if date:
            return date

    date = _normalize_date(
        full_text
    )

    if date:
        return date

    patterns = [

        r"\b\d{1,2}\s*[-—–./]\s*"
        r"\d{1,2}\s*[-—–./]\s*"
        r"\d{4}\b",

        r"\b\d{1,2}\s+"
        r"\d{1,2}\s+"
        r"\d{4}\b",

        r"\b\d{4}\s*[-—–./]\s*"
        r"\d{1,2}\s*[-—–./]\s*"
        r"\d{1,2}\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            full_text
        )

        if match:

            date = _normalize_date(
                match.group(0)
            )

            if date:
                return date

    return None


# =========================================================
# EXTRACT PHONE
# =========================================================

def _extract_phone(full_text):

    patterns = [

        r"(?:\+91[\s-]?)?[6-9]\d{9}",

        r"\b[6-9]\d{9}\b",

        r"\b\d{5}[\s-]\d{5}\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            full_text
        )

        if match:

            phone = re.sub(
                r"\D",
                "",
                match.group(0)
            )

            if (
                len(phone) == 12
                and
                phone.startswith("91")
            ):
                phone = phone[2:]

            if len(phone) == 10:
                return phone

    return None


# =========================================================
# EXTRACT EMAIL
# =========================================================

def _extract_email(full_text):

    pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}\b"
    )

    match = re.search(
        pattern,
        full_text
    )

    if match:
        return match.group(0)

    return None


# =========================================================
# EXTRACT OWNER
# =========================================================

def _extract_owner(lines):

    owner = _extract_multiline_value(
        lines,
        [
            "owner",
            "owner name",
            "belongs to"
        ]
    )

    if owner:

        # Don't accidentally return phone/email
        if re.fullmatch(
            r"[\d\s+()-]+",
            owner
        ):
            return None

        if "@" in owner:
            return None

        return owner

    return None


# =========================================================
# EXTRACT ITEM
# =========================================================

def _extract_item(lines):

    item = _extract_multiline_value(
        lines,
        [
            "item",
            "item name",
            "lost item",
            "object"
        ]
    )

    if item:

        return re.sub(
            r"\s+",
            " ",
            item
        ).strip()

    item_keywords = [
        "wallet",
        "phone",
        "mobile",
        "smartphone",
        "watch",
        "bag",
        "backpack",
        "laptop",
        "purse",
        "keys",
        "key",
        "bottle",
        "book",
        "card",
        "umbrella",
        "spectacles",
        "glasses",
        "headphones",
        "earphones",
        "charger",
        "tablet",
        "id card",
        "pouch",
        "scooter"
    ]

    for line in lines:

        lower = line.lower()

        for keyword in item_keywords:

            if keyword in lower:

                if len(line.split()) <= 8:
                    return line.strip()

    return None


# =========================================================
# EXTRACT DESCRIPTION
# =========================================================

def _extract_description(lines):

    description = _extract_multiline_value(
        lines,
        [
            "description",
            "details",
            "item description",
            "about"
        ]
    )

    if description:
        return description

    description_keywords = [
        "black",
        "blue",
        "red",
        "brown",
        "white",
        "leather",
        "small",
        "large",
        "new",
        "old",
        "damaged",
        "peacock",
        "letter",
        "with",
        "contains"
    ]

    possible = []

    for line in lines:

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in description_keywords
        ):

            if not any(
                label in lower
                for label in [
                    "owner:",
                    "contact:",
                    "phone:",
                    "date:",
                    "found at:",
                    "location:"
                ]
            ):

                possible.append(
                    line.strip()
                )

    if possible:

        return " ".join(
            possible[:3]
        )

    return None


# =========================================================
# EXTRACT LOCATION
# =========================================================

def _extract_location(lines):

    location = _extract_multiline_value(
        lines,
        [
            "found at",
            "found location",
            "location",
            "last seen",
            "place found",
            "found near"
        ]
    )

    if location:
        return location

    location_words = [
        "near",
        "library",
        "college",
        "campus",
        "classroom",
        "canteen",
        "lab",
        "bench",
        "building",
        "bus stop",
        "station",
        "office",
        "parking"
    ]

    for line in lines:

        lower = line.lower()

        if any(
            word in lower
            for word in location_words
        ):

            if len(line.split()) <= 15:
                return line.strip()

    return None


# =========================================================
# EXTRACT FINDER NAME
# =========================================================

def _extract_finder_name(lines):

    name = _extract_multiline_value(
        lines,
        [
            "contact",
            "contact person",
            "found by",
            "finder",
            "finder name",
            "reported by"
        ]
    )

    if name:

        if re.fullmatch(
            r"[\d\s+()-]+",
            name
        ):
            return None

        if "@" in name:
            return None

        return name

    return None


# =========================================================
# EXTRACT ID / SERIAL
# =========================================================

def _extract_identifier(lines):

    identifier_labels = [
        "id",
        "id number",
        "serial",
        "serial number",
        "registration",
        "registration number",
        "roll number",
        "student id",
        "reference",
        "reference number"
    ]

    identifier = _extract_multiline_value(
        lines,
        identifier_labels
    )

    if identifier:
        return identifier

    for line in lines:

        matches = re.findall(
            r"\b[A-Z]{1,5}[-/]?\d{2,10}\b",
            line,
            flags=re.IGNORECASE
        )

        if matches:
            return matches[0]

    return None


# =========================================================
# EXTRACT ALL INFORMATION
# =========================================================

def _extract_information(
    lines,
    full_text
):

    return {

        # NEW
        "owner": _extract_owner(
            lines
        ),

        "item": _extract_item(
            lines
        ),

        "description": _extract_description(
            lines
        ),

        "location": _extract_location(
            lines
        ),

        "date": _extract_date(
            lines,
            full_text
        ),

        "finder_name": _extract_finder_name(
            lines
        ),

        "phone": _extract_phone(
            full_text
        ),

        "email": _extract_email(
            full_text
        ),

        "identifier": _extract_identifier(
            lines
        )
    }


# =========================================================
# MAIN OCR FUNCTION
# =========================================================

def extract_text(image_bytes):

    image = _decode_image(
        image_bytes
    )

    image = _resize_image(
        image,
        max_size=1400
    )

    variants = _make_variants(
        image
    )

    all_results = []

    # =====================================================
    # OCR
    # =====================================================

    for variant in variants:

        results = reader.readtext(

            variant,

            detail=1,

            paragraph=False,

            width_ths=0.7,

            height_ths=0.5,

            text_threshold=0.45,

            low_text=0.25,

            link_threshold=0.4
        )

        for result in results:

            if len(result) < 3:
                continue

            bbox = result[0]
            text = result[1]
            confidence = float(result[2])

            text = _clean_line(
                text
            )

            if not text:
                continue

            xs = [
                point[0]
                for point in bbox
            ]

            ys = [
                point[1]
                for point in bbox
            ]

            center_x = (
                sum(xs) / len(xs)
            )

            center_y = (
                sum(ys) / len(ys)
            )

            all_results.append(
                {
                    "text": text,
                    "confidence": confidence,
                    "x": center_x,
                    "y": center_y
                }
            )

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique = {}

    for result in all_results:

        key = re.sub(
            r"[^a-z0-9]",
            "",
            result["text"].lower()
        )

        if not key:
            continue

        if (
            key not in unique
            or
            result["confidence"]
            >
            unique[key]["confidence"]
        ):

            unique[key] = result

    cleaned_results = list(
        unique.values()
    )

    # =====================================================
    # SORT BY READING ORDER
    # =====================================================

    cleaned_results.sort(
        key=lambda item: (
            round(
                item["y"] / 20
            ),
            item["x"]
        )
    )

    cleaned_results = cleaned_results[:50]

    # =====================================================
    # OCR LINES
    # =====================================================

    lines = [
        item["text"]
        for item in cleaned_results
    ]

    # =====================================================
    # COMPLETE OCR TEXT
    # =====================================================

    full_text = "\n".join(
        lines
    )

    # =====================================================
    # AVERAGE CONFIDENCE
    # =====================================================

    if cleaned_results:

        average_confidence = (
            sum(
                item["confidence"]
                for item in cleaned_results
            )
            /
            len(cleaned_results)
        )

    else:

        average_confidence = 0.0

    # =====================================================
    # STRUCTURED INFORMATION
    # =====================================================

    information = _extract_information(
        lines,
        full_text
    )

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "text": full_text,

        "lines": [
            {
                "text": item["text"],
                "confidence": round(
                    item["confidence"] * 100,
                    1
                )
            }
            for item in cleaned_results
        ],

        "average_confidence": round(
            average_confidence * 100,
            1
        ),

        "information": information
    }