# ============================================================
# LOST ITEMS
# ============================================================

elif page == "📋 Lost Items":

    st.title("📋 Lost Items")

    st.write(
        "View reported lost items and manage their current status."
    )

    # --------------------------------------------------------
    # GET ITEMS
    # --------------------------------------------------------

    items = get_lost_items()

    if not items:

        st.info(
            "No lost items have been reported yet."
        )

    else:

        # ----------------------------------------------------
        # SEPARATE ACTIVE AND RETURNED ITEMS
        # ----------------------------------------------------

        active_items = []
        returned_items = []

        for item in items:

            status = str(
                item.get(
                    "status",
                    "Lost"
                )
            ).strip().lower()

            if status == "returned":

                returned_items.append(item)

            else:

                active_items.append(item)

        # ====================================================
        # ACTIVE LOST ITEMS
        # ====================================================

        st.subheader(
            "🔴 Active Lost Items"
        )

        if not active_items:

            st.success(
                "🎉 No active lost items."
            )

        else:

            st.write(
                f"Currently lost: **{len(active_items)}**"
            )

            for index, item in enumerate(
                active_items
            ):

                with st.container(
                    border=True
                ):

                    # ----------------------------------------
                    # ITEM TITLE
                    # ----------------------------------------

                    item_name = item.get(
                        "item_name",
                        "Unknown Item"
                    )

                    st.markdown(
                        f"### 🎒 {item_name}"
                    )

                    # ----------------------------------------
                    # DETAILS
                    # ----------------------------------------

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"👤 **Owner:** "
                            f"{item.get('owner_name', 'Not provided')}"
                        )

                        st.write(
                            f"📝 **Description:** "
                            f"{item.get('description', 'Not provided')}"
                        )

                        st.write(
                            f"📞 **Contact:** "
                            f"{item.get('contact', 'Not provided')}"
                        )

                    with col2:

                        st.write(
                            f"📍 **Last Seen:** "
                            f"{item.get('location', 'Not provided')}"
                        )

                        st.write(
                            f"📅 **Date Lost:** "
                            f"{item.get('date_lost', 'Not provided')}"
                        )

                        st.write(
                            "🔴 **Status:** Lost"
                        )

                    st.divider()

                    # ----------------------------------------
                    # ACTION BUTTONS
                    # ----------------------------------------

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "✅ Mark as Returned",
                            key=f"returned_{index}"
                        ):

                            try:

                                update_item_status(
                                    item["id"],
                                    "Returned"
                                )

                                st.success(
                                    "Item marked as returned successfully!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Could not update item: {e}"
                                )

                    with col2:

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{index}"
                        ):

                            try:

                                delete_lost_item(
                                    item["id"]
                                )

                                st.success(
                                    "Lost item deleted successfully!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Could not delete item: {e}"
                                )

        # ====================================================
        # RETURNED ITEMS
        # ====================================================

        st.divider()

        st.subheader(
            "✅ Returned Items"
        )

        if not returned_items:

            st.info(
                "No items have been marked as returned yet."
            )

        else:

            st.write(
                f"Successfully returned: **{len(returned_items)}**"
            )

            for index, item in enumerate(
                returned_items
            ):

                with st.container(
                    border=True
                ):

                    item_name = item.get(
                        "item_name",
                        "Unknown Item"
                    )

                    st.markdown(
                        f"### 🎒 {item_name}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"👤 **Owner:** "
                            f"{item.get('owner_name', 'Not provided')}"
                        )

                        st.write(
                            f"📝 **Description:** "
                            f"{item.get('description', 'Not provided')}"
                        )

                        st.write(
                            f"📞 **Contact:** "
                            f"{item.get('contact', 'Not provided')}"
                        )

                    with col2:

                        st.write(
                            f"📍 **Last Seen:** "
                            f"{item.get('location', 'Not provided')}"
                        )

                        st.write(
                            f"📅 **Date Lost:** "
                            f"{item.get('date_lost', 'Not provided')}"
                        )

                        st.success(
                            "✅ Status: Returned"
                        )

                    # ----------------------------------------
                    # DELETE RETURNED ITEM
                    # ----------------------------------------

                    if st.button(
                        "🗑️ Delete Record",
                        key=f"delete_returned_{index}"
                    ):

                        try:

                            delete_lost_item(
                                item["id"]
                            )

                            st.success(
                                "Record deleted successfully!"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Could not delete record: {e}"
                            )