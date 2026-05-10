import streamlit as st
from Core.functions_mail import *
from streamlit_extras.stylable_container import stylable_container
import base64

# Page
def insurance_claim_page_mail():
    st.subheader("📄 Mail Claim")

    # ---------- session state ----------
    st.session_state.setdefault("data", {})
    st.session_state.setdefault("last_loaded_insurance", None)

    d = st.session_state.data

    st.session_state.setdefault("attachments", [])

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    if "form_reset_key" not in st.session_state:
        st.session_state.form_reset_key = 0

    @st.dialog("File Preview", width="large")
    def show_preview(file_bytes, file_name):
        """Displays the file content in a modal popup."""
        extension = file_name.split('.')[-1].lower()
        
        if extension == "pdf":
            # Encode PDF to Base64 for the iframe
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        
        elif extension in ["png", "jpg", "jpeg", "gif"]:
            st.image(file_bytes, caption=file_name)
        
        else:
            st.warning("Preview not supported for this file type. Please download to view.")
            st.download_button("Download instead", data=file_bytes, file_name=file_name)


    # ---------- Load DB lists ----------
    try:
        iata_codes = fetch_list("SELECT DISTINCT IATA FROM IATACodes")
        commodities = fetch_list("SELECT DISTINCT [type] FROM CommodityType")
        statuses = fetch_list("SELECT DISTINCT [status] FROM Status")
        currencies = fetch_list("SELECT DISTINCT Alpha_Code FROM Currency")
        claim_types = fetch_list("SELECT DISTINCT complainDescription FROM ComplainsType")
    except Exception as e:
        st.error(f"DB ERROR: {e}")
        return


    DEFAULT_DATA = {
        "mail1": "",
        "mail2": "",
        "mail_date": None,
        "route": [],
        "flight_num": "",
        "flight_date": None,
        "sector": "Import",
        "commodity": "",
        "weight": 0.0,
        "total_parcels": 0,
        "damaged": 0,
        "claimant_name": "",
        "claimant_type": "Shipper",
        "complain_location": "",
        "claim_type": "",
        "other_claim": "",
        "status": statuses[0],
        "receive_date": None,
        "req_amount": 0.0,
        "req_currency": "",
        "req_date": None,
        "acc_amount": 0.0,
        "acc_currency": "",
        "acc_date": None,
        "notes": "",
        "insurance_sent_date": None,
        "other_status": ""
    }

    # ================= Insurance Number =================
    c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 2, 2])

    with c1:
        ins_num = st.text_input("Insurance Num", max_chars=5)

        # CLEAR FORM WHEN INSURANCE NUMBER IS EMPTY
        if ins_num == "":
            st.session_state.data = {}
            st.session_state.last_loaded_insurance = None


        # -------- AUTO SEARCH (NO BUTTON) --------
        if ins_num.isdigit() and len(ins_num) == 5:
            ins_year = f"20{ins_num[:2]}"
            insurance_numyear = f"{ins_num}/{ins_year}"

            if st.session_state.last_loaded_insurance != insurance_numyear:
                st.session_state.last_loaded_insurance = insurance_numyear
                row = fetch_mail_claim(insurance_numyear)

                if not row:
                    st.warning("No record found")
                    # CLEAR EVERYTHING
                    st.session_state.data = DEFAULT_DATA.copy()
                    st.rerun()
                    
                else:
                    mail = str(row["mailNum"] or "")
                    st.session_state.data = {
                        "mail1": mail[:4],
                        "mail2": mail[4:],
                        "mail_date": row["mailDate"],
                        "route": row["route"].split() if isinstance(row["route"], str) else [],
                        "flight_num": row["fltNum"],
                        "flight_date": row["fltDate"],
                        "sector": row["Sector"],
                        "commodity": row["commodity"],
                        "weight": row["weight_Kg"],
                        "total_parcels": row["totalParcelsNum"],
                        "damaged": row["damages_lossesParcelsNum"],
                        "claimant_name": row["claimantName"],
                        "claimant_type": row["claimantType"],
                        "complain_location": row["complainLocation"],
                        "claim_type": row["complainType"],
                        "other_claim": row["claim_other"],
                        "status": row["status"],
                        "receive_date": row["complainReceivedDate"],
                        "req_amount": row["compansationRequested"],
                        "req_currency": row["requestedCurrency"],
                        "req_date": row["compansationRequestedDate"],
                        "acc_amount": row["compansationAccepted"],
                        "acc_currency": row["acceptedCurrency"],
                        "acc_date": row["compansationAcceptedDate"],
                        "notes": row["Notes"],
                        "insurance_sent_date": row["insuranceSentDate"],
                        "other_status": row["status_other"]
                    }

                    attachments = fetch_attachments(insurance_numyear)
                    st.session_state.attachments = attachments
                    st.rerun()

    with c2:
        ins_year = f"20{ins_num[:2]}" if len(ins_num) >= 2 else ""
        st.text_input("Year", value=ins_year, disabled=True)

    st.divider()

    # ================= Mail INFO =================
    st.markdown("**mail Info**")

    c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1.5, 3, 1.5, 1.5])
    with c1:
        mail1 = st.text_input("Mail (Prefix)", value=d.get("mail1", ""), max_chars=5)
    with c2:
        mail2 = st.text_input("Mail (Serial)", value=d.get("mail2", ""), max_chars=6)
    with c3:
        mail_date = st.date_input("Mail Date", value=d.get("mail_date") or None)
    with c4:
        route = st.multiselect("Route", iata_codes, default=d.get("route", []))
    with c5:
        flight_num = st.text_input("Flight Num", value=d.get("flight_num", ""))
    with c6:
        flight_date = st.date_input("Flight Date", value=d.get("flight_date") or None)


    c1, c2, c3, c4 = st.columns([1.5, 2, 1, 1])

    with c1:
        sector_options = ["Import", "Export"]

        sector = st.selectbox(
            "Sector",
            sector_options,
            index=None
        )

    with c2:
        commodity_options = commodities

        commodity = st.selectbox(
            "Commodity",
            commodity_options,
            index=None
        )

    with c3:
        weight = st.number_input("Weight KG", 
                                 value=float(d["weight"]) if d.get("weight") is not None else 0.0)
    with c4:
        total_parcels = st.number_input("Total Parcels",
                                        value=int(d["total_parcels"]) if d.get("total_parcels") is not None else 0)


    st.divider()

    # ================= CLAIM DETAILS =================
    st.markdown("**Claim Details**")

    c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
    with c1:
        claimant_name = st.text_input("Claimant Name", value=d.get("claimant_name",""))
    with c2:
        claimant_type_options = ["Shipper","Consignee"] 

        claimant_type = st.selectbox(
            "Claimant Type",
            claimant_type_options,
            index=None
        )

    with c3:
        location_options = iata_codes

        complain_location = st.selectbox(
            "Complain Location",
            location_options,
            index=None
        )

    with c4:
        damaged = st.number_input("Damaged / Losses",
                                value=int(d["damaged"]) if d.get("damaged") is not None else 0)


    c1, c2, c3, c4 = st.columns([2, 2.5, 2, 2.5])
    with c1:
        claim_type_options = claim_types

        claim_type = st.selectbox(
            "Claim Type",
            claim_type_options,
            index=None
        )

    with c2:
        other_claim = st.text_input("Other Claim Description", value=d.get("other_claim",""),
                                    disabled=(claim_type != "Other"))

    with c3:
        status_options = statuses

        status = st.selectbox(
            "Status",
            status_options,
            index=None
        )

    with c4:
        other_status = st.text_input("Other Status Description", value=d.get("other_status", ""))

     # ---------- NEW FIELD: Insurance Sent Date ----------
    c1, c2 = st.columns([2, 2])
    with c1:
        receive_date = st.date_input("Receive Date", value=d.get("receive_date") or None)

    with c2:
        insurance_sent_date = st.date_input(
            "Insurance Sent Date",
            value=d.get("insurance_sent_date") or None
        )

    # ================= COMPENSATION =================
    st.markdown("**Compensation**")

    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 1.5, 0.5, 1.5, 1, 1.5, 0.5, 1.5])
    with c1:
        req_amount = st.number_input("Requested", 
                                     value=float(d["req_amount"]) if d.get("req_amount") is not None else 0.0)
    with c2:
        currency_options = currencies

        req_currency = st.selectbox(
            "Requested Currency",
            currency_options,
            index=None
        )

    with c3:
        st.write("")
        st.write("")
        req_checked = st.checkbox(label="-", value=d.get("req_date") is not None, key="req_checked")
    with c4:
        req_date = st.date_input("Requested Date",
                                 value=d.get("req_date") or None,
                                 disabled=not req_checked)

    with c5:
        acc_amount = st.number_input(
    "Accepted", value=float(d["acc_amount"]) if d.get("acc_amount") is not None else 0.0)

    with c6:
        currency_options = currencies

        acc_currency = st.selectbox(
            "Accepted Currency",
            currency_options,
            index=None
        )

    with c7:
        st.write("")
        st.write("")
        acc_checked = st.checkbox(label="-", value=d.get("acc_date") is not None, key="acc_checked")
    with c8:
        acc_date = st.date_input("Accepted Date",
                                 value=d.get("acc_date") or None,
                                 disabled=not acc_checked)

    notes = st.text_area("Notes", value=d.get("notes",""), height=80)
   

    c1, c4, c2, c5, c3  = st.columns(5)
    with c1:
        with stylable_container(
        key="add_button",
        css_styles="""
            button {
                background-color: #2E7D32 !important;
                color: white !important;
                border-radius: 18px !important;
                border: none !important;
                transition: all 0.2s ease !important;
            }
            button:hover {
                background-color: #f0f2f6 !important;
                border-color: #000000 !important;
                color: #000000 !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            }
        """,
    ):
            add_clicked = st.button("Add", type="secondary", width="stretch")

    if add_clicked:
        st.session_state.data.update({
            "insurance_num": ins_num,
            "mail1": mail1,
            "mail2": mail2,
            "mail_date": mail_date,
            "route": route,
            "flight_num": flight_num,
            "flight_date": flight_date,
            "sector": sector,
            "commodity": commodity,
            "weight": weight,
            "total_parcels": total_parcels,
            "damaged": damaged,
            "claimant_name": claimant_name,
            "claimant_type": claimant_type,
            "complain_location": complain_location,
            "claim_type": claim_type,
            "other_claim": other_claim,
            "other_status": other_status,
            "status": status,
            "receive_date": receive_date,
            "req_amount": req_amount,
            "req_currency": req_currency,
            "req_date": req_date if req_checked else None,
            "acc_amount": acc_amount,
            "acc_currency": acc_currency,
            "acc_date": acc_date if acc_checked else None,
            "notes": notes,
            "insurance_sent_date": insurance_sent_date
        })

        # VALIDATION: damaged cannot exceed total parcels
        if damaged > total_parcels:
            st.error("Damaged parcels cannot be more than Total Parcels.")
            st.stop()  # stops execution, prevents insert


        ok, msg = insert_mail_claim(st.session_state.data)

        if ok:
            insert_log(action="Inserted New mail Record",insurance_num=ins_num)
            st.success(msg)
            st.session_state.last_loaded_insurance = None
            st.rerun()
        else:
            st.error(msg)



    with c2:
        with stylable_container(
        key="update_button",
        css_styles="""
            button {
                background-color: #F59E0B !important;
                color: white !important;
                border-radius: 18px !important;
                border: none !important;
                transition: all 0.2s ease !important;
            }
            button:hover {
                background-color: #f0f2f6 !important;
                border-color: #000000 !important;
                color: #000000 !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            }
        """,
    ):
            update_clicked = st.button("Update", type="secondary",width="stretch")

    if update_clicked:
        st.session_state.data.update({
            "mail1": mail1,
            "mail2": mail2,
            "mail_date": mail_date,
            "route": route,
            "flight_num": flight_num,
            "flight_date": flight_date,
            "sector": sector,
            "commodity": commodity,
            "weight": weight,
            "total_parcels": total_parcels,
            "damaged": damaged,
            "claimant_name": claimant_name,
            "claimant_type": claimant_type,
            "complain_location": complain_location,
            "claim_type": claim_type,
            "other_claim": other_claim,
            "other_status": other_status,
            "status": status,
            "receive_date": receive_date,
            "req_amount": req_amount,
            "req_currency": req_currency,
            "req_date": req_date if req_checked else None,
            "acc_amount": acc_amount,
            "acc_currency": acc_currency,
            "acc_date": acc_date if acc_checked else None,
            "notes": notes,
            "insurance_sent_date": insurance_sent_date
        })

        # VALIDATION: damaged cannot exceed total parcels
        if damaged > total_parcels:
            st.error("Damaged parcels cannot be more than Total Parcels.")
            st.stop()  # stops execution, prevents insert

        ok, msg = update_mail_claim_by_insurance(ins_num, st.session_state.data)
        if ok:
            insert_log(action="Updated mail Record",insurance_num=ins_num)
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    if st.session_state.get("perm_id") == 1:
        with c3:
            with stylable_container(
            key="delete_button",
            css_styles="""
                button {
                    background-color: #C62828 !important;
                    color: white !important;
                    border-radius: 18px !important;
                    transition: all 0.2s ease !important;
                    border: none !important;
                }
                button:hover {
                    background-color: #f0f2f6 !important;
                    border-color: #000000 !important;
                    color: #000000 !important;
                    transform: translateY(-1px);
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
                }
            """,
        ):
                delete_clicked = st.button("Delete", type="secondary", width="stretch")
                

        if delete_clicked:
            ok, msg = delete_mail_claim_by_insurance(ins_num)

            if ok:
                insert_log(action="Deleted mail Record",insurance_num=ins_num)
                st.success(msg)
                st.session_state.data = {}
                st.session_state.attachments = []
                st.session_state.last_loaded_insurance = None
                st.rerun()
            else:
                st.error(msg)


    st.divider()

    # --- 1. Fetch Lists for Dropdowns ---
    try:
        dept_names = fetch_list("SELECT DeptName FROM Department")
        types_desc = fetch_list("SELECT attachTypeDescription FROM AttachmentsType")

    except Exception as e:
        st.error(f"Error loading dropdowns: {e}")


    st.markdown("Upload Attachment")
    uploaded_file = st.file_uploader("Drag & Drop File Here", type=None,key=f"uploader_{st.session_state.uploader_key}")

    c1, c2, c3, c4 = st.columns([1.5,1.8,1.5,2])

    with c1:
        
        selected_type_name = st.selectbox("Attachment Type", options=types_desc, index=None,
                                          key=f"type_{st.session_state.form_reset_key}")

    with c2:
        selected_dept_name = st.selectbox("Department", options=dept_names , index=None,
                                          key=f"dept_{st.session_state.form_reset_key}")

    with c3:
        sent_received_date = st.date_input("Sent/Received Date", value=None,
                                           key=f"date_{st.session_state.form_reset_key}")

    with c1:
        if uploaded_file and ins_num.isdigit() and len(ins_num) == 5:
            if st.button("Upload Attachment", use_container_width=True):
                # 1. Validation: Check if the date is missing
                if selected_type_name is None:
                    st.warning("⚠️ Please enter an attachment type before uploading.")

                elif selected_dept_name is None:
                    st.warning("⚠️ Please enter a department before uploading.")

                elif sent_received_date is None:
                    st.warning("⚠️ Please enter a Sent/Received Date before uploading.")
                
                else:
                    ok, msg = insert_attachment(
                        insurance_num=f"{ins_num}/20{ins_num[:2]}",
                        file=uploaded_file,
                        attach_type=selected_type_name,
                        dept=selected_dept_name,
                        added_by=st.session_state.get("code"),
                        sent_received_date=sent_received_date
                    )
                    if ok:
                        # 1. Update the list IMMEDIATELY in session state
                        updated_list = fetch_attachments(insurance_numyear)
                        st.session_state.attachments = updated_list if updated_list else []

                        # 2. CHANGE THE KEY to reset the uploader
                        st.session_state.uploader_key += 1
                        st.session_state.form_reset_key += 1
                        
                        # 3. Show success message (Toast is non-blocking, Success is persistent)
                        st.success("✅ File Uploaded Successfully!")
                        
                        insert_log(action="New attachment " + file['FileName'] + " added", insurance_num=ins_num)

                        
                        # 4. Rerun to reset the uploader widget
                        st.rerun()
                    else:
                        # IMPORTANT: This will tell you exactly which part of the function failed
                        st.error(f"Upload Failed: {msg}")
                
    if st.session_state.attachments:

        st.markdown("Existing Files")

        for file in st.session_state.attachments:
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 2, 2, 2, 2, 0.8, 0.8, 0.8])
            with col1:
                st.write(f" {file['FileName']}")
            
            with col2:
                st.write(f" {file.get('attachTypeDescription', 'N/A')}")

            with col3:
                st.write(f" {file.get('DeptName', 'N/A')}")

            with col4:
                # Formatting the date to be more readable
                file_date = file.get('sent_receivedDate')
                formatted_date = file_date.strftime("%Y-%m-%d") if file_date else "N/A"
                st.write(f" {formatted_date}")

            with col5:
                # Check if attachSize exists and is not None before dividing
                size_kb = round(file['attachSize'] / 1024, 2) if file.get('attachSize') is not None else 0.0
                st.write(f" {size_kb} KB")

            with col6:
                st.download_button(
                    label="📥",
                    data=file["attachFile"],
                    file_name=file["FileName"],
                    mime="application/octet-stream",
                    key=f"dl_{file['attachID']}",
                    type="tertiary", 
                    width="stretch",
                    help="Download this file",
                    on_click=insert_log,
                    kwargs={
                            "action": f"Attachment {file['FileName']} Downloaded", 
                            "insurance_num": ins_num
                        }
                )

            with col7:
                # CLICK TO PREVIEW
                if st.button("👁️", key=f"v_{file['attachID']}", type="tertiary", help="View this file", width="stretch"):
                    show_preview(file['attachFile'], file['FileName'])
                    insert_log(action="Attachment" + file['FileName'] + " Previewed", insurance_num=ins_num)

            
            with col8:

                if st.button("🗑️", key=f"del_btn_{file['attachID']}", help="Delete this file", type="tertiary", width="stretch"):
                    ok, msg = delete_attachment(file['attachID'])
                    if ok:
                        st.toast(msg)

                        insert_log(action="Attachment" + file['FileName'] + " Deleted", insurance_num=ins_num) 
                        # Refresh the attachment list in state
                        insurance_numyear = f"{ins_num}/20{ins_num[:2]}"
                        # Fetch fresh data
                        updated_files = fetch_attachments(insurance_numyear)
                        
                        # Explicitly update state (if updated_files is None/Empty, it becomes [])
                        st.session_state.attachments = updated_files if updated_files else []
                        st.rerun()
                    else:
                        st.error(msg)