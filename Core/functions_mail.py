import streamlit as st
from Core.DB_Connection import get_connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import pandas as pd
from datetime import datetime
from Core.functions import *

# DB helpers

def delete_mail_claim_by_insurance(ins_num: str):

    # ---------- Validation ----------
    if not ins_num:
        return False, "Insurance number is required"

    if not ins_num.isdigit() or len(ins_num) != 5:
        return False, "Insurance number must be exactly 5 digits"

    # ---------- Build insuranceNum ----------
    ins_year = f"20{ins_num[:2]}"
    insurance_numyear = f"{ins_num}/{ins_year}"

    engine = get_connection()

    try:
        # ---------- Transaction ----------
        with engine.begin() as conn:

            # Fetch complainID
            result = conn.execute(
                text("""
                    SELECT complainID
                    FROM ComplainsDetails_mail
                    WHERE insuranceNum = :ins
                """),
                {"ins": insurance_numyear}
            ).fetchone()

            if not result:
                return False, f"No claim found for insurance number {insurance_numyear}"

            complain_id = result[0]

            # Delete ALL attachments first (Prevents FK constraint errors)
            conn.execute(
                text("DELETE FROM AttachmentsFile WHERE complainID = :cid"),
                {"cid": complain_id}
            )

            # Delete main claim
            conn.execute(
                text("""
                    DELETE FROM ComplainsDetails_mail
                    WHERE insuranceNum = :ins
                """),
                {"ins": insurance_numyear}
            )

        return True, f"Claim {insurance_numyear} deleted successfully"

    except Exception as e:
        return False, f"Database error while deleting claim: {e}"
        

def update_mail_claim_by_insurance(ins_num, data):

    # Validity Check

    if not ins_num:
        return False, "Insurance number is required."

    if not ins_num.isdigit():
        return False, "Insurance number must contain digits only."

    if len(ins_num) != 5:
        return False, "Insurance number must be exactly 5 digits."



    insurance_numyear = f"{ins_num}/20{ins_num[:2]}"

    engine = get_connection()

    # Convert dropdown text to IDs
    location_id = get_id_by_value("IATACodes", "iataID", "IATA", data["complain_location"])
    commodity_id = get_id_by_value("CommodityType", "id", "type", data["commodity"])
    complain_type_id = get_id_by_value("ComplainsType", "compliantypeID", "complainDescription", data["claim_type"])
    status_id = get_id_by_value("Status", "statusID", "status", data["status"])

    Exchange_acc = get_exchange_rate(data["acc_currency"],'EGP')
    Exchange_req = get_exchange_rate(data["req_currency"],'EGP')
    
    Exchange_acc_usd = get_exchange_rate(data["acc_currency"],'USD')
    Exchange_req_usd = get_exchange_rate(data["req_currency"],'USD')

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE ComplainsDetails_mail
                SET
                    mailNum = :mailNum,
                    mailDate = :mailDate,
                    route = :route,
                    complainLocationID = :complainLocationID,
                    Sector = :Sector,
                    fltNum = :fltNum,
                    fltDate = :fltDate,
                    CommodityID = :CommodityID,
                    weight_Kg = :weight_Kg,
                    totalParcelsNum = :totalParcelsNum,
                    damages_lossesParcelsNum = :damages_lossesParcelsNum,
                    complainTypeID = :complainTypeID,
                    claimantName = :claimantName,
                    claimantType = :claimantType,
                    complainReceivedDate = :complainReceivedDate,
                    compansationRequested = :compansationRequested,
                    compansationRequestedCurrency = :compansationRequestedCurrency,
                    compansationRequestedDate = :compansationRequestedDate,
                    compansationAccepted = :compansationAccepted,
                    compansationAcceptedCurrency = :compansationAcceptedCurrency,
                    compansationAcceptedDate = :compansationAcceptedDate,
                    statusID = :statusID,
                    Notes = :Notes,
                    claim_other = :claim_other,
                    status_other = :other_status,
                    addedBy = :addedBy,        
                    addedDate = :addedDate,
                    insuranceSentDate = :insurance_sent_date,
                    ExchangeEGP_requested = :ex_req,
                    ExchangeEGP_accepted = :ex_acc,
                    ExchangeUSD_requested = :ex_req_usd,
                    ExchangeUSD_accepted = :ex_acc_usd                 
                WHERE insuranceNum = :insuranceNum
            """), {
                "mailNum": data["mail1"] + data["mail2"],
                "mailDate": data["mail_date"],
                "route": " ".join(data["route"]),
                "complainLocationID": location_id,
                "Sector": data["sector"],
                "fltNum": data["flight_num"],
                "fltDate": data["flight_date"],
                "CommodityID": commodity_id,
                "weight_Kg": data["weight"],
                "totalParcelsNum": data["total_parcels"],
                "damages_lossesParcelsNum": data["damaged"],
                "complainTypeID": complain_type_id,
                "claimantName": data["claimant_name"],
                "claimantType": data["claimant_type"],
                "complainReceivedDate": data["receive_date"],
                "compansationRequested": data["req_amount"],
                "compansationRequestedCurrency": get_id_by_value("Currency", "currencyId", "Alpha_Code", data["req_currency"]),
                "compansationRequestedDate": data["req_date"] if data.get("req_date") else None,
                "compansationAccepted": data["acc_amount"],
                "compansationAcceptedCurrency": get_id_by_value("Currency", "currencyId", "Alpha_Code", data["acc_currency"]),
                "compansationAcceptedDate": data["acc_date"] if data.get("acc_date") else None,
                "statusID": status_id,
                "Notes": data["notes"],
                "claim_other": data["other_claim"],
                "other_status": data["other_status"],
                "addedBy": st.session_state.get("code"),
                "addedDate": datetime.now(),
                "insurance_sent_date": data["insurance_sent_date"],
                "ex_req": Exchange_req * data["req_amount"],
                "ex_acc": Exchange_acc * data["acc_amount"],
                "ex_req_usd": Exchange_req_usd * data["req_amount"],
                "ex_acc_usd": Exchange_acc_usd * data["acc_amount"],
                "insuranceNum": insurance_numyear
            })

        return True, "Updated successfully."

    except Exception as e:
        return False, str(e)


def insert_mail_claim(data):
    insurance_num = data.get("insurance_num")

    # Validity Check

    if not insurance_num:
        return False, "Insurance number is required."

    if not insurance_num.isdigit():
        return False, "Insurance number must contain digits only."

    if len(insurance_num) != 5:
        return False, "Insurance number must be exactly 5 digits."

    
    engine = get_connection()


    insurance_numyear = f"{insurance_num}/20{insurance_num[:2]}"

    # Convert dropdown text to IDs
    location_id = get_id_by_value("IATACodes", "iataID", "IATA", data["complain_location"])
    commodity_id = get_id_by_value("CommodityType", "id", "type", data["commodity"])
    complain_type_id = get_id_by_value("ComplainsType", "compliantypeID", "complainDescription", data["claim_type"])
    status_id = get_id_by_value("Status", "statusID", "status", data["status"])
    req_currency_id = get_id_by_value("Currency", "currencyId", "Alpha_Code", data["req_currency"])
    acc_currency_id = get_id_by_value("Currency", "currencyId", "Alpha_Code", data["acc_currency"])

    Exchange_acc = get_exchange_rate(data["acc_currency"],'EGP')
    Exchange_req = get_exchange_rate(data["req_currency"],'EGP')

    Exchange_acc_usd = get_exchange_rate(data["acc_currency"],'USD')
    Exchange_req_usd = get_exchange_rate(data["req_currency"],'USD')

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO ComplainsDetails_mail (
                    insuranceNum,
                    pending,
                    mailNum,
                    mailDate,
                    route,
                    complainLocationID,
                    Sector,
                    fltNum,
                    fltDate,
                    CommodityID,
                    weight_Kg,
                    totalParcelsNum,
                    damages_lossesParcelsNum,
                    complainTypeID,
                    claimantName,
                    claimantType,
                    complainReceivedDate,
                    compansationRequested,
                    compansationRequestedCurrency,
                    compansationRequestedDate,
                    compansationAccepted,
                    compansationAcceptedCurrency,
                    compansationAcceptedDate,
                    statusID,
                    Notes,
                    claim_other,
                    status_other,
                    addedBy,
                    addedDate,
                    ExchangeEGP_requested, 
                    ExchangeEGP_accepted,
                    ExchangeUSD_requested,
                    ExchangeUSD_accepted,
                    insuranceSentDate
                )
                VALUES (
                    :insuranceNum,
                    'False',
                    :mailNum,
                    :mailDate,
                    :route,
                    :complainLocationID,
                    :Sector,
                    :fltNum,
                    :fltDate,
                    :CommodityID,
                    :weight_Kg,
                    :totalParcelsNum,
                    :damages_lossesParcelsNum,
                    :complainTypeID,
                    :claimantName,
                    :claimantType,
                    :complainReceivedDate,
                    :compansationRequested,
                    :compansationRequestedCurrency,
                    :compansationRequestedDate,
                    :compansationAccepted,
                    :compansationAcceptedCurrency,
                    :compansationAcceptedDate,
                    :statusID,
                    :Notes,
                    :claim_other,
                    :status_other,
                    :addedBy,
                    :addedDate,
                    :ex_req,
                    :ex_acc,
                    :ex_req_usd,
                    :ex_acc_usd,
                    :insurance_sent_date
                )
            """), {
                "insuranceNum": insurance_numyear,
                "mailNum": data["mail1"] + data["mail2"],
                "mailDate": data["mail_date"],
                "route": " ".join(data["route"]),
                "complainLocationID": location_id,
                "Sector": data["sector"],
                "fltNum": data["flight_num"],
                "fltDate": data["flight_date"],
                "CommodityID": commodity_id,
                "weight_Kg": data["weight"],
                "totalParcelsNum": data["total_parcels"],
                "damages_lossesParcelsNum": data["damaged"],
                "complainTypeID": complain_type_id,
                "claimantName": data["claimant_name"],
                "claimantType": data["claimant_type"],
                "complainReceivedDate": data["receive_date"],
                "compansationRequested": data["req_amount"],
                "compansationRequestedCurrency": req_currency_id,
                "compansationRequestedDate": data["req_date"],
                "compansationAccepted": data["acc_amount"],
                "compansationAcceptedCurrency": acc_currency_id,
                "compansationAcceptedDate": data["acc_date"],
                "statusID": status_id,
                "Notes": data["notes"],
                "claim_other": data["other_claim"],
                "status_other": data["other_status"],
                "addedBy": st.session_state.get("code"),
                "addedDate": datetime.now(),
                "ex_req": Exchange_req * data["req_amount"],
                "ex_acc": Exchange_acc * data["acc_amount"],
                "ex_req_usd":Exchange_req_usd * data["req_amount"],
                "ex_acc_usd":Exchange_acc_usd * data["acc_amount"],
                "insurance_sent_date": data["insurance_sent_date"]
            })

        return True, "Claim added successfully"

    except IntegrityError as e:
        # This is the REAL pyodbc error
        orig = e.orig
        msg = str(orig)

        #DUPLICATE KEY
        if "2601" in msg or "2627" in msg:
            return False, "Data duplication: this record already exists."

        # NOT NULL VIOLATION
        if "515" in msg:
            return False, "Missing required data. Please fill all mandatory fields."

        return False, "Database integrity error."

    except Exception as e:
        return False, f"Unexpected error: {str(e)}"



def fetch_mail_claim(insurance_num):
    query = """
        SELECT
            cd.insuranceNum,
            cd.mailNum,
            cd.mailDate,
            cd.route,
            iata.IATA AS complainLocation,
            cd.Sector,
            cd.fltNum,
            cd.fltDate,
            com.[type] AS commodity,
            cd.weight_Kg,
            cd.totalParcelsNum,
            cd.damages_lossesParcelsNum,
            ct.complainDescription AS complainType,
            cd.claimantName,
            cd.claimantType,
            cd.complainReceivedDate,
            cd.compansationRequested,
            c.Alpha_Code AS requestedCurrency,
            cd.compansationRequestedDate,
            cd.compansationAccepted,
            cc.Alpha_Code AS acceptedCurrency,
            cd.compansationAcceptedDate,
            stt.status,
            cd.Notes,
            cd.claim_other,
            cd.insuranceSentDate,
            cd.status_other

        FROM ComplainsDetails_mail cd
        LEFT JOIN IATACodes iata ON iata.iataID = cd.complainLocationID
        LEFT JOIN CommodityType com ON com.id = cd.CommodityID
        LEFT JOIN ComplainsType ct ON ct.compliantypeID = cd.complainTypeID
        LEFT JOIN Status stt ON stt.statusID = cd.statusID
        LEFT JOIN Currency c ON c.currencyId = cd.compansationRequestedCurrency
        LEFT JOIN Currency cc ON cc.currencyId = cd.compansationAcceptedCurrency

        WHERE cd.insuranceNum = ?
    """
    engine = get_connection()
    df = pd.read_sql(query, engine, params=(insurance_num,))
    return None if df.empty else df.iloc[0].to_dict()






