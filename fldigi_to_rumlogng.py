import socket

import logging
import logging.handlers
import os
import pathlib
import re

# Logging Parameters
LOG_FILE: str = "fldigi_to_rumlog.log"
LOG_MAX_SIZE: int = 1_000_000
LOG_COUNT: int = 3
LOG_ENCODING: str = "utf-8"

TARGET_IP: str = "127.0.01"
TARGET_PORT: int = 65532

# Anchor file paths to the script's own directory rather than the current
# working directory
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

PREFIX_RE: str = r"^(([A-Z0-9]{1,3})[0-9])[A-Z]{1,4}(?:/[A-Z0-9]+)?$"

# Configure logging to a rotating file (caps log at ~1 MB, keeping up to 3
# old copies) so it doesn't grow too big over all QSOs being logged.
logging.basicConfig(
    handlers=[
        logging.handlers.RotatingFileHandler(
            SCRIPT_DIR / LOG_FILE, 
            maxBytes=LOG_MAX_SIZE, backupCount=LOG_COUNT, encoding=LOG_ENCODING
        )
    ],
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Maps the FLDigi macro environment variable names to the ADIF field names
# expected by the QRZ Logbook API.
key_map: dict[str, str] = {
    'FLDIGI_LOGBOOK_ARRL_SECT_IN': 'arrl_sect',
    'FLDIGI_LOGBOOK_BAND': 'band',
    'FLDIGI_LOGBOOK_CALL': 'call',
    'FLDIGI_LOGBOOK_CLASS_IN': 'class',
    'FLDIGI_LOGBOOK_CONTINENT': 'cont',
    'FLDIGI_LOGBOOK_COUNTRY': 'country',
    'FLDIGI_LOGBOOK_COUNTY': 'cnty',
    'FLDIGI_LOGBOOK_CQZ': 'cqz',
    'FLDIGI_LOGBOOK_DATE_OFF': 'qso_date_off',
    'FLDIGI_LOGBOOK_DATE': 'qso_date',
    'FLDIGI_LOGBOOK_DXCC': 'dxcc',
    'FLDIGI_LOGBOOK_FREQUENCY': 'freq',
    'FLDIGI_LOGBOOK_IOTA': 'iota',
    'FLDIGI_LOGBOOK_ITUZ': 'ituz',
    'FLDIGI_LOGBOOK_LOCATOR': 'gridsquare',
    'FLDIGI_LOGBOOK_MODE': 'mode',
    'FLDIGI_LOGBOOK_NAME': 'name',
    'FLDIGI_LOGBOOK_NOTES': 'notes',
    'FLDIGI_LOGBOOK_QSL_VIA': 'qsl_via',
    'FLDIGI_LOGBOOK_QTH': 'qth',
    'FLDIGI_LOGBOOK_RST_IN': 'rst_rcvd',
    'FLDIGI_LOGBOOK_RST_OUT': 'rst_sent',
    'FLDIGI_LOGBOOK_SERNO_IN': 'srx',
    'FLDIGI_LOGBOOK_SERNO_OUT': 'stx',
    'FLDIGI_LOGBOOK_STATE': 'state',
    'FLDIGI_LOGBOOK_TIME_OFF': 'time_off',
    'FLDIGI_LOGBOOK_TIME_ON': 'time_on',
    'FLDIGI_LOGBOOK_TX_PWR': 'tx_pwr',
    'FLDIGI_LOGBOOK_VE_PROV': 've_prov',
}

def get_callsign_prefix(callsign):
    # The regex pattern (Group 1 captures the full prefix)
    pattern = r'^(([A-Z0-9]{1,3})[0-9])[A-Z]{1,4}(?:/[A-Z0-9]+)?$'
    
    # Clean input and force uppercase to match the regex
    cleaned_input = str(callsign).strip().upper()
    
    match = re.match(pattern, cleaned_input)
    if match:
        return match.group(1)  # Returns the full prefix (e.g., 'W1', '3B8')
    return ""

def dict_to_xml(root: str, contact: dict[str, str]) -> str:
    xml_ver: str = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml_text: str = f"<{root}>\n"
    xml_text += "\n".join([f"\t<{key}>{val}</{key}>" for key, val in contact.items()])
    xml_text += f"\n</{root}>\n"
    xml_text = xml_ver + xml_text
    return xml_text
    


def main() -> None:
    logging.info('Starting transmission of new log entry to RumlogNG.')
    

    # fields: dict[str, str] = {
    #     adif_name: os.getenv(env_var, "").strip()
    #     for env_var, adif_name in key_map.items()
    # }

    contest_name: str = "RTTYOPS-WW-RTTY"
    my_call: str = "N3BMC"
    call: str = "WA0CGZ"
    call_prefix: str = get_callsign_prefix(call)
    if call_prefix == "":
        logging.warning('Unable to extract a call sign prefix.')
    band: str = "14.0"
    rx_freq: str = "140880"
    tx_freq: str = "140880"
    mode: str = "RTTY"
    rst_sent: str = "599"
    rst_rcv: str = "599"
    gridsquare: str = "FM19nf"
    exchange_in: str = "599 2025"
    exchange_out: str = "599 2026"
    section: str = ""
    comment: str = ""
    qth: str = ""
    name: str = ""
    power: str = ""
    misctext: str = ""
    zone: str = ""
    claimed_qso: str = "1"
    sent_number: str = "001"
    rcv_number: str = "200"
    

    
    contact: dict[str, str] = {
        "app":"Fldigi To Rumlog",
        "contestname":contest_name,
        "timestamp":"2020-01-17 16:43:38",
        "mycall":my_call,
        "band":band,
        "rxfreq":rx_freq,
        "txfreq":tx_freq,
        "mode":"rtty",
        "call":call,
        "wxprefix":call_prefix,
        "mode":mode,
        "snt":rst_sent,
        "rcv":rst_rcv,
        "sntnr":sent_number,
        "rcvnr":rcv_number,
        "gridsquare":gridsquare,
        "exchangel":exchange_in,
        "SentExchange":exchange_out,
        "section":section,
        "comment":comment,
        "qth":qth,
        "name":name,
        "power":power,
        "misctext":misctext,
        "zone":zone,
        "IsClaimedQso":claimed_qso,


    }

    packet: str = dict_to_xml("contactinfo", contact)
    packet_bytes: bytes = packet.encode("UTF-8")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.sendto(packet_bytes, (TARGET_IP, TARGET_PORT))
        except Exception as e:
            print(f"Caught and error: {e}")
        finally:
            print("Done")

if __name__ == "__main__":
    main()