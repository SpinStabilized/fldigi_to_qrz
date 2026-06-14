# FLDigi to QRZ Logbook Uploader

A Python script that takes the currently selected FLDigi logbook entry and
uploads it directly to your [QRZ Logbook](https://www.qrz.com/) via an FLDigi
`<EXEC>` macro.

## How it works

FLDigi's `<EXEC>` macro exports the fields of the selected logbook entry as
`FLDIGI_LOGBOOK_*` environment variables. This script reads those variables,
builds a single ADIF QSO record, and submits it to the
[QRZ Logbook API](https://www.qrz.com/page/logbook30.html) using
`ACTION=INSERT`.

## Requirements

- Python 3.10 or later
- A QRZ Logbook (XML) subscription and API key
- [uv](https://docs.astral.sh/uv/) for running the script and managing its
  dependencies

## Setup

1. Copy `fldigi_to_qrz.py` to a location FLDigi can reach, e.g.
   `~/.fldigi/scripts/` (Linux/macOS) or a folder of your choosing on
   Windows.

2. Create a `.env` file in the **same directory** as `fldigi_to_qrz.py`:

   ```
   QRZ_KEY=your-qrz-logbook-api-key
   ```

   Your API key is available on QRZ under **Logbook Data -> Logbook
   Settings -> API Key**.

   > **Note:** Do not commit `.env` to version control — it grants write
   > access to your QRZ logbook.

3. (Linux/macOS) Make the script executable:

   ```bash
   chmod +x fldigi_to_qrz.py
   ```

4. In FLDigi, open the macro editor (**Configure -> Macros**) and add a
   new macro containing:

   ```
   <EXEC>/path/to/uv run --directory /full/path/to/fldigi_to_qrz.py python fldigi_to_qrz.py</EXEC>
   ```

5. Log a QSO as usual, select the entry in the FLDigi logbook, then press
   the macro key to upload it to QRZ.

## Configuration

| Setting   | Where  | Description                         |
|-----------|--------|--------------------------------------|
| `QRZ_KEY` | `.env` | Your QRZ Logbook API key (required). |

## Field mapping

The script maps the following FLDigi `<EXEC>` environment variables to ADIF
fields:

| FLDigi variable | ADIF field |
|---|---|
| `FLDIGI_LOGBOOK_CALL` | `call` |
| `FLDIGI_LOGBOOK_DATE` | `qso_date` |
| `FLDIGI_LOGBOOK_DATE_OFF` | `qso_date_off` |
| `FLDIGI_LOGBOOK_TIME_ON` | `time_on` |
| `FLDIGI_LOGBOOK_TIME_OFF` | `time_off` |
| `FLDIGI_LOGBOOK_BAND` | `band` |
| `FLDIGI_LOGBOOK_MODE` | `mode` |
| `FLDIGI_LOGBOOK_FREQUENCY` | `freq` |
| `FLDIGI_LOGBOOK_RST_IN` | `rst_rcvd` |
| `FLDIGI_LOGBOOK_RST_OUT` | `rst_sent` |
| `FLDIGI_LOGBOOK_NAME` | `name` |
| `FLDIGI_LOGBOOK_QTH` | `qth` |
| `FLDIGI_LOGBOOK_LOCATOR` | `gridsquare` |
| `FLDIGI_LOGBOOK_COUNTRY` | `country` |
| `FLDIGI_LOGBOOK_STATE` | `state` |
| `FLDIGI_LOGBOOK_COUNTY` | `cnty` |
| `FLDIGI_LOGBOOK_VE_PROV` | `ve_prov` |
| `FLDIGI_LOGBOOK_CONTINENT` | `cont` |
| `FLDIGI_LOGBOOK_DXCC` | `dxcc` |
| `FLDIGI_LOGBOOK_CQZ` | `cqz` |
| `FLDIGI_LOGBOOK_ITUZ` | `ituz` |
| `FLDIGI_LOGBOOK_IOTA` | `iota` |
| `FLDIGI_LOGBOOK_ARRL_SECT_IN` | `arrl_sect` |
| `FLDIGI_LOGBOOK_CLASS_IN` | `class` |
| `FLDIGI_LOGBOOK_SERNO_IN` | `srx` |
| `FLDIGI_LOGBOOK_SERNO_OUT` | `stx` |
| `FLDIGI_LOGBOOK_TX_PWR` | `tx_pwr` |
| `FLDIGI_LOGBOOK_QSL_VIA` | `qsl_via` |
| `FLDIGI_LOGBOOK_NOTES` | `notes` |

Empty fields are omitted from the ADIF record. `call`, `qso_date`, `time_on`,
`band`, and `mode` are required by QRZ and the script will refuse to upload if
any of these are blank.

## Logging

The script writes to `fldigi_to_qrz.log` in the same directory as the script,
rotating automatically once it reaches roughly 1 MB (keeping up to 3 older
copies). The default log level is `INFO`, which records whether each upload
succeeded or failed along with QRZ's response. For more detail (the full ADIF
record sent to QRZ), change `level=logging.INFO` to `level=logging.DEBUG` in
`logging.basicConfig`.

## Troubleshooting

**"QRZ_KEY is not set (check .env)."**
The script couldn't find a `.env` file with `QRZ_KEY` set. Make sure
`.env` is in the same directory as `fldigi_to_qrz.py` and contains a line
like `QRZ_KEY=abcd1234...`.

**"Aborting upload: missing required field(s): ..."**
One of `call`, `qso_date`, `time_on`, `band`, or `mode` was empty in the
selected FLDigi logbook entry. Fill in the missing field(s) in FLDigi
before re-running the macro.

**"QSO upload failed: {'RESULT': 'FAIL', 'REASON': ...}"**
QRZ rejected the record. Check the `REASON` text in `app.log` — common
causes are an invalid/expired API key, a logbook that isn't enabled for
API access, or QRZ flagging the contact as a duplicate.

**`uv: command not found` (from FLDigi)**
FLDigi's `<EXEC>` macro inherits a minimal environment that may not
include the same `PATH` as your shell. If FLDigi can't find `uv`, use the
full path to the `uv` binary in the macro, e.g.
`<EXEC>/path/to/uv run /full/path/to/fldigi_to_qrz.py</EXEC>`.

## Alternative: running without uv

If you'd rather not use `uv`, the dependencies are also listed in
`requirements.txt` for a traditional virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python fldigi_to_qrz.py
```

In this case, point the FLDigi macro at that environment's Python
interpreter directly, e.g. `<EXEC>/full/path/to/venv/bin/python /full/path/to/fldigi_to_qrz.py</EXEC>`.

## License

This project is licensed under the MIT License — see
[LICENSE](LICENSE) for details.