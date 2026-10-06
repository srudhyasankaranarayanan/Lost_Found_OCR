import streamlit as st
from PIL import Image, ImageOps
import io
import hashlib

from parser import extract_text

from executor import find_matches

from database import (
    create_table,
    add_lost_item,
    get_lost_items,
    get_active_lost_items,
    get_found_items,
    delete_lost_item,
    mark_item_as_found
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Lost & Found OCR",
    page_icon="🔎",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

create_table()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .detect-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    .match-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 18px;
    }

    .success-card {
        background: #ecfdf5;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #10b981;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TITLE
# =========================================================

st.title(
    "🔎 Smart Lost & Found OCR"
)

st.caption(
    "Upload a found item's image and find possible "
    "matches from the reported lost-item database."
)


# =========================================================
# SIDEBAR
# =========================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📌 Report Lost Item",
        "📷 Find Found Item",
        "📋 Lost Items"
    ]
)


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    active_items = get_active_lost_items()

    found_items = get_found_items()

    st.header(
        "Welcome"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Reported Lost Items",
            len(active_items)
        )

    with col2:

        st.metric(
            "Found / Matched Items",
            len(found_items)
        )

    with col3:

        st.metric(
            "OCR Matching",
            "Ready"
        )

    st.info(
        "Workflow: Upload image → OCR extracts useful "
        "information → matching engine compares it "
        "with lost-item reports."
    )

    st.subheader(
        "How it works"
    )

    st.write(
        """
        1. A user reports a lost item.
        2. Another user finds the item and uploads its image.
        3. OCR reads the visible information.
        4. The system extracts item, description,
           location, date and finder information.
        5. The matching engine compares the found item
           with active lost-item reports.
        6. If the match score reaches 90% or above,
           the item is automatically marked as Found.
        7. The item is removed from the active Lost Items list.
        """
    )


# =========================================================
# REPORT LOST ITEM
# =========================================================

elif page == "📌 Report Lost Item":

    st.header(
        "📌 Report a Lost Item"
    )

    with st.form(
        "lost_item_form"
    ):

        owner_name = st.text_input(
            "Owner Name *"
        )

        item_name = st.text_input(
            "Item Name *"
        )

        description = st.text_area(
            "Description",
            placeholder=(
                "Example: Black leather wallet "
                "with college ID card..."
            )
        )

        contact = st.text_input(
            "Contact Number *"
        )

        location = st.text_input(
            "Last Seen Location",
            placeholder=(
                "Example: College Library"
            )
        )

        date_lost = st.date_input(
            "Date Lost"
        )

        submitted = st.form_submit_button(
            "Save Lost Item",
            type="primary"
        )

        if submitted:

            if not owner_name.strip():

                st.error(
                    "Please enter the owner name."
                )

            elif not item_name.strip():

                st.error(
                    "Please enter the item name."
                )

            elif not contact.strip():

                st.error(
                    "Please enter a contact number."
                )

            else:

                try:

                    add_lost_item(
                        owner_name.strip(),
                        item_name.strip(),
                        description.strip(),
                        contact.strip(),
                        location.strip(),
                        str(date_lost)
                    )

                    st.success(
                        "✅ Lost item reported successfully!"
                    )

                except Exception as error:

                    st.error(
                        f"Could not save lost item: {error}"
                    )


# =========================================================
# FIND FOUND ITEM
# =========================================================

elif page == "📷 Find Found Item":

    st.header(
        "📷 Scan Found Item"
    )

    st.write(
        "Upload a clear image of a found-item notice. "
        "The system will extract the information and "
        "compare it with active lost-item reports."
    )

    # =====================================================
    # UPLOAD
    # =====================================================

    uploaded_file = st.file_uploader(
        "Upload image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]
    )

    if uploaded_file:

        file_bytes = uploaded_file.getvalue()

        file_hash = hashlib.md5(
            file_bytes
        ).hexdigest()

        # =================================================
        # RESET WHEN NEW IMAGE
        # =================================================

        if (
            "uploaded_file_hash"
            not in st.session_state
            or
            st.session_state[
                "uploaded_file_hash"
            ] != file_hash
        ):

            st.session_state[
                "uploaded_file_hash"
            ] = file_hash

            st.session_state.pop(
                "ocr_result",
                None
            )

            st.session_state.pop(
                "match_results",
                None
            )

            st.session_state.pop(
                "auto_found_item_id",
                None
            )

        # =================================================
        # DISPLAY IMAGE
        # =================================================

        try:

            image = Image.open(
                io.BytesIO(
                    file_bytes
                )
            )

            image = ImageOps.exif_transpose(
                image
            )

            st.image(
                image,
                caption="Uploaded Found Item",
                width=500
            )

        except Exception as error:

            st.error(
                f"Unable to open image: {error}"
            )

            st.stop()

        # =================================================
        # SCAN BUTTON
        # =================================================

        if st.button(
            "🔍 Scan & Find Match",
            type="primary",
            use_container_width=True
        ):

            try:

                # -----------------------------------------
                # PREPARE IMAGE
                # -----------------------------------------

                with st.spinner(
                    "🖼️ Preparing image..."
                ):

                    scan_image = Image.open(
                        io.BytesIO(
                            file_bytes
                        )
                    )

                    scan_image = ImageOps.exif_transpose(
                        scan_image
                    )

                    if scan_image.mode != "RGB":

                        scan_image = (
                            scan_image.convert(
                                "RGB"
                            )
                        )

                    scan_image.thumbnail(
                        (1400, 1400),
                        Image.Resampling.LANCZOS
                    )

                    buffer = io.BytesIO()

                    scan_image.save(
                        buffer,
                        format="JPEG",
                        quality=90
                    )

                    processed_bytes = (
                        buffer.getvalue()
                    )

                # -----------------------------------------
                # OCR
                # -----------------------------------------

                with st.spinner(
                    "🔎 Reading information from image..."
                ):

                    result = extract_text(
                        processed_bytes
                    )

                st.session_state[
                    "ocr_result"
                ] = result

                st.session_state.pop(
                    "match_results",
                    None
                )

                st.session_state.pop(
                    "auto_found_item_id",
                    None
                )

                st.success(
                    "✅ Image scanned successfully!"
                )

            except Exception as error:

                st.error(
                    f"OCR failed: {error}"
                )

                st.stop()

        # =================================================
        # OCR RESULT
        # =================================================

        if "ocr_result" in st.session_state:

            result = st.session_state[
                "ocr_result"
            ]

            information = result.get(
                "information",
                {}
            )

            item = information.get(
                "item"
            )

            description = information.get(
                "description"
            )

            location = information.get(
                "location"
            )

            date = information.get(
                "date"
            )

            finder_name = information.get(
                "finder_name"
            )

            phone = information.get(
                "phone"
            )

            email = information.get(
                "email"
            )

            identifier = information.get(
                "identifier"
            )

            # =================================================
            # DETECTED INFORMATION
            # =================================================

            st.divider()

            st.subheader(
                "📝 Detected Information"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "🎒 **Item**"
                )

                st.write(
                    item
                    if item
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "📝 **Description**"
                )

                st.write(
                    description
                    if description
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "📍 **Found Location**"
                )

                st.write(
                    location
                    if location
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "📅 **Found Date**"
                )

                st.write(
                    date
                    if date
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            with col2:

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "👤 **Finder Name**"
                )

                st.write(
                    finder_name
                    if finder_name
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "📞 **Finder Phone**"
                )

                st.write(
                    phone
                    if phone
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "📧 **Email**"
                )

                st.write(
                    email
                    if email
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="detect-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    "🆔 **ID / Serial Number**"
                )

                st.write(
                    identifier
                    if identifier
                    else "Not detected"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            # =================================================
            # OCR CONFIDENCE
            # =================================================

            confidence = result.get(
                "average_confidence",
                0
            )

            st.metric(
                "🔎 Overall OCR Confidence",
                f"{confidence:.1f}%"
            )

            # =================================================
            # COMPLETE OCR TEXT
            # =================================================

            with st.expander(
                "🔍 View Complete Scanned Text"
            ):

                ocr_text = result.get(
                    "text",
                    ""
                )

                if ocr_text.strip():

                    st.text_area(
                        "Complete OCR Output",
                        ocr_text,
                        height=200,
                        disabled=True
                    )

                else:

                    st.warning(
                        "No text was detected."
                    )

                lines = result.get(
                    "lines",
                    []
                )

                if lines:

                    st.write(
                        "**OCR confidence by detected text:**"
                    )

                    for line in lines:

                        line_confidence = line.get(
                            "confidence",
                            0
                        )

                        st.write(
                            f"**{line.get('text', '')}** "
                            f"— {line_confidence:.1f}%"
                        )

            # =================================================
            # MATCHING
            # =================================================

            st.divider()

            st.subheader(
                "🎯 Possible Lost Item Matches"
            )

            # =================================================
            # RUN MATCHING
            # =================================================

            if (
                "match_results"
                not in st.session_state
            ):

                items = get_active_lost_items()

                if not items:

                    st.session_state[
                        "match_results"
                    ] = []

                else:

                    with st.spinner(
                        "🎯 Comparing with lost-item database..."
                    ):

                        try:

                            matches = find_matches(
                                result.get(
                                    "text",
                                    ""
                                ),
                                items,
                                minimum_score=35,
                                information=information
                            )

                            st.session_state[
                                "match_results"
                            ] = matches

                        except Exception as error:

                            st.error(
                                f"Matching failed: {error}"
                            )

                            st.session_state[
                                "match_results"
                            ] = []

            # =================================================
            # GET MATCHES
            # =================================================

            matches = st.session_state.get(
                "match_results",
                []
            )

            # =================================================
            # MATCH FOUND
            # =================================================

            if matches:

                best_match = matches[0]

                best_score = float(
                    best_match.get(
                        "match_score",
                        0
                    )
                )

                # =================================================
                # 90% OR ABOVE
                # =================================================

                if best_score >= 90:

                    item_id = best_match.get(
                        "id"
                    )

                    # ---------------------------------------------
                    # AUTOMATICALLY MARK AS FOUND
                    # ---------------------------------------------

                    if (
                        item_id
                        and
                        st.session_state.get(
                            "auto_found_item_id"
                        ) != item_id
                    ):

                        try:

                            updated = mark_item_as_found(
                                item_id
                            )

                            if updated:

                                st.session_state[
                                    "auto_found_item_id"
                                ] = item_id

                        except Exception as error:

                            st.error(
                                "Could not update item status: "
                                f"{error}"
                            )

                    # =================================================
                    # SUCCESS MESSAGE
                    # =================================================

                    st.success(
                        "🎉 Product Found Successfully!"
                    )

                    st.info(
                        "✅ The found product has been "
                        "successfully matched with the lost product."
                    )

                    st.markdown(
                        '<div class="success-card">',
                        unsafe_allow_html=True
                    )

                    st.subheader(
                        "🎯 Successfully Matched Lost Item"
                    )

                    st.write(
                        "### 🟢 Strong Match"
                    )

                    st.metric(
                        "Match Score",
                        f"{best_score:.1f}%"
                    )

                    match_col1, match_col2 = (
                        st.columns(2)
                    )

                    with match_col1:

                        st.write(
                            "**👤 Owner:** "
                            f"{best_match.get(
                                'owner_name',
                                'Not provided'
                            )}"
                        )

                        st.write(
                            "**🎒 Item:** "
                            f"{best_match.get(
                                'item_name',
                                'Not provided'
                            )}"
                        )

                        st.write(
                            "**📝 Description:** "
                            f"{best_match.get(
                                'description'
                            ) or 'Not provided'}"
                        )

                    with match_col2:

                        st.write(
                            "**📞 Owner Contact:** "
                            f"{best_match.get(
                                'contact',
                                'Not provided'
                            )}"
                        )

                        st.write(
                            "**📍 Last Seen:** "
                            f"{best_match.get(
                                'location'
                            ) or 'Not provided'}"
                        )

                        st.write(
                            "**📅 Date Lost:** "
                            f"{best_match.get(
                                'date_lost'
                            ) or 'Not provided'}"
                        )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                    st.success(
                        "📞 Please contact the owner using "
                        "the contact number above to return "
                        "the item."
                    )

                    st.info(
                        "📌 This item has automatically been "
                        "removed from the active Lost Items list."
                    )

                # =================================================
                # BELOW 90%
                # =================================================

                else:

                    st.warning(
                        "⚠️ A possible match was found, "
                        "but the confidence is below 90%."
                    )

                    for index, match in enumerate(
                        matches
                    ):

                        score = float(
                            match.get(
                                "match_score",
                                0
                            )
                        )

                        if score >= 60:

                            status_text = (
                                "🟡 Possible Match"
                            )

                        else:

                            status_text = (
                                "🔵 Weak Match"
                            )

                        st.markdown(
                            '<div class="match-card">',
                            unsafe_allow_html=True
                        )

                        st.subheader(
                            f"🎒 Possible Match #{index + 1}"
                        )

                        st.write(
                            f"### {status_text}"
                        )

                        st.metric(
                            "Match Score",
                            f"{score:.1f}%"
                        )

                        match_col1, match_col2 = (
                            st.columns(2)
                        )

                        with match_col1:

                            st.write(
                                "**👤 Owner:** "
                                f"{match.get(
                                    'owner_name',
                                    'Not provided'
                                )}"
                            )

                            st.write(
                                "**🎒 Item:** "
                                f"{match.get(
                                    'item_name',
                                    'Not provided'
                                )}"
                            )

                            st.write(
                                "**📝 Description:** "
                                f"{match.get(
                                    'description'
                                ) or 'Not provided'}"
                            )

                        with match_col2:

                            st.write(
                                "**📞 Owner Contact:** "
                                f"{match.get(
                                    'contact',
                                    'Not provided'
                                )}"
                            )

                            st.write(
                                "**📍 Last Seen:** "
                                f"{match.get(
                                    'location'
                                ) or 'Not provided'}"
                            )

                            st.write(
                                "**📅 Date Lost:** "
                                f"{match.get(
                                    'date_lost'
                                ) or 'Not provided'}"
                            )

                        st.markdown(
                            "</div>",
                            unsafe_allow_html=True
                        )

            # =================================================
            # NO MATCH
            # =================================================

            else:

                active_items = (
                    get_active_lost_items()
                )

                if not active_items:

                    st.info(
                        "📭 There are no active lost-item "
                        "reports in the database."
                    )

                else:

                    st.warning(
                        "No reliable lost-item "
                        "match was found."
                    )

                    st.info(
                        "💡 Try uploading a clearer image "
                        "or make sure the lost-item report "
                        "contains accurate item and "
                        "location details."
                    )


# =========================================================
# LOST ITEMS
# =========================================================

elif page == "📋 Lost Items":

    st.header(
        "📋 Lost Items"
    )

    # =====================================================
    # ACTIVE LOST ITEMS
    # =====================================================

    active_items = (
        get_active_lost_items()
    )

    st.subheader(
        "🔴 Active Lost Items"
    )

    if not active_items:

        st.success(
            "🎉 No active lost items!"
        )

    else:

        st.write(
            f"**Total active lost items: "
            f"{len(active_items)}**"
        )

        st.divider()

        for item in active_items:

            item_id = item.get(
                "id"
            )

            item_name = item.get(
                "item_name",
                "Unknown Item"
            )

            owner_name = item.get(
                "owner_name",
                "Unknown Owner"
            )

            with st.expander(
                f"#{item_id} — "
                f"{item_name} — "
                f"{owner_name}"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**👤 Owner:** "
                        f"{owner_name}"
                    )

                    st.write(
                        f"**🎒 Item:** "
                        f"{item_name}"
                    )

                    st.write(
                        f"**📝 Description:** "
                        f"{item.get('description') or 'Not provided'}"
                    )

                    st.write(
                        f"**📞 Contact:** "
                        f"{item.get('contact') or 'Not provided'}"
                    )

                with col2:

                    st.write(
                        f"**📍 Last Seen:** "
                        f"{item.get('location') or 'Not provided'}"
                    )

                    st.write(
                        f"**📅 Date Lost:** "
                        f"{item.get('date_lost') or 'Not provided'}"
                    )

                    st.write(
                        "**📌 Status:** 🔴 Lost"
                    )

                st.divider()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_lost_{item_id}"
                ):

                    try:

                        delete_lost_item(
                            item_id
                        )

                        st.success(
                            "✅ Item deleted successfully."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Could not delete item: {error}"
                        )

    # =====================================================
    # FOUND ITEMS
    # =====================================================

    st.divider()

    st.subheader(
        "🟢 Found / Matched Items"
    )

    found_items = (
        get_found_items()
    )

    if not found_items:

        st.info(
            "No items have been successfully matched yet."
        )

    else:

        st.write(
            f"**Total found items: "
            f"{len(found_items)}**"
        )

        for item in found_items:

            item_id = item.get(
                "id"
            )

            item_name = item.get(
                "item_name",
                "Unknown Item"
            )

            owner_name = item.get(
                "owner_name",
                "Unknown Owner"
            )

            with st.expander(
                f"#{item_id} — "
                f"{item_name} — "
                f"{owner_name}"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**👤 Owner:** "
                        f"{owner_name}"
                    )

                    st.write(
                        f"**🎒 Item:** "
                        f"{item_name}"
                    )

                    st.write(
                        f"**📝 Description:** "
                        f"{item.get('description') or 'Not provided'}"
                    )

                    st.write(
                        f"**📞 Contact:** "
                        f"{item.get('contact') or 'Not provided'}"
                    )

                with col2:

                    st.write(
                        f"**📍 Last Seen:** "
                        f"{item.get('location') or 'Not provided'}"
                    )

                    st.write(
                        f"**📅 Date Lost:** "
                        f"{item.get('date_lost') or 'Not provided'}"
                    )

                    st.write(
                        "**📌 Status:** 🟢 Found"
                    )

                st.divider()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_found_{item_id}"
                ):

                    try:

                        delete_lost_item(
                            item_id
                        )

                        st.success(
                            "✅ Item deleted successfully."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Could not delete item: {error}"
                        )