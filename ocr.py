import cv2
import pytesseract
import re


# =========================================================
# TESSERACT PATH
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# NORMAL OCR
# =========================================================

def normal_ocr(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Enlarge image
    gray = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # Improve contrast
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    # Threshold
    processed = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY +
        cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(
        processed,
        config="--psm 6"
    )

    return text


# =========================================================
# DIGIT OCR
# =========================================================

def digit_ocr(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Enlarge more for handwriting
    gray = cv2.resize(
        gray,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    # Improve contrast
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    processed = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY +
        cv2.THRESH_OTSU
    )[1]

    # ONLY digits
    text = pytesseract.image_to_string(
        processed,
        config=(
            "--psm 6 "
            "-c tessedit_char_whitelist=0123456789"
        )
    )

    return text


# =========================================================
# FIND PHONE NUMBER
# =========================================================

def find_phone(text):

    # Remove strange OCR characters
    cleaned = re.sub(
        r"[^0-9\s]",
        " ",
        text
    )

    # -----------------------------------------------------
    # Direct 10 digit number
    # -----------------------------------------------------

    match = re.search(
        r"(?<!\d)[6-9]\d{9}(?!\d)",
        cleaned
    )

    if match:

        return match.group()


    # -----------------------------------------------------
    # Number with spaces
    # Example:
    # 98765 43210
    # -----------------------------------------------------

    digits = re.sub(
        r"\D",
        "",
        text
    )

    # Search every possible 10-digit sequence
    for i in range(
        max(0, len(digits) - 20)
    ):

        candidate = digits[i:i + 10]

        if len(candidate) == 10:

            if candidate[0] in "6789":

                return candidate


    return None


# =========================================================
# MAIN OCR FUNCTION
# =========================================================

def extract_text(image_path):

    image = cv2.imread(image_path)

    if image is None:

        raise ValueError(
            "Unable to read uploaded image."
        )


    # =====================================================
    # NORMAL OCR
    # =====================================================

    normal_text = normal_ocr(
        image
    )


    # =====================================================
    # DIGIT OCR
    # =====================================================

    digit_text = digit_ocr(
        image
    )


    # =====================================================
    # FIND PHONE
    # =====================================================

    phone = find_phone(
        digit_text
    )


    # If digit OCR failed, try normal OCR
    if phone is None:

        phone = find_phone(
            normal_text
        )


    # =====================================================
    # ADD PHONE TO OCR TEXT
    # =====================================================

    final_text = normal_text.strip()


    if phone:

        final_text += (
            "\nPhone OCR Result: "
            + phone
        )


    # =====================================================
    # DEBUG INFORMATION
    # =====================================================

    final_text += (
        "\n\n--- DIGIT OCR ---\n"
        + digit_text.strip()
    )


    return final_text