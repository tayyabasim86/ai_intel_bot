import os, json, gspread
from google.oauth2.service_account import Credentials

# Prefilled defaults
SHEET_ID_DEFAULT  = "1W32pKtWXhBVg7GKZVDq3XvjbX9Q5u5zZ-AlDVjzrkU0"
SHEET_TAB_DEFAULT = "Sheet1"

REQUIRED_HEADERS = ['Type','Source','Title','Author/Company','Date','ExecutiveSummary','BusinessInsight','RelevanceScore','Link','CanonicalLink','PrimaryOrSecondary','DedupeKey','Status']

def _auth_client():
    keyfile = os.getenv("GCP_SERVICE_ACCOUNT_JSON_FILE")
    info = None
    if keyfile and os.path.exists(keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            info = json.load(f)
    else:
        raw = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        if raw:
            info = json.loads(raw)
    if not info:
        raise RuntimeError("Service account JSON not provided. Use GCP_SERVICE_ACCOUNT_JSON or GCP_SERVICE_ACCOUNT_JSON_FILE.")
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    print("[DEBUG] Using SA:", info.get("client_email"))
    return gspread.authorize(creds)

def _ensure_headers(ws):
    first_row = ws.row_values(1)
    if first_row != REQUIRED_HEADERS:
        if first_row:
            ws.delete_row(1)
        ws.insert_row(REQUIRED_HEADERS, 1)

def open_sheet(sheet_id: str | None = None, tab: str | None = None):
    gc = _auth_client()
    sheet_id = sheet_id or os.getenv("SHEET_ID") or SHEET_ID_DEFAULT
    tab = (tab or os.getenv("SHEET_TAB") or SHEET_TAB_DEFAULT or "Sheet1").strip()

    print("[DEBUG] Using SHEET_ID:", sheet_id)
    print("[DEBUG] Using SHEET_TAB:", tab)

    sh = gc.open_by_key(sheet_id)
    print("[INFO] Opened spreadsheet title ->", sh.title)

    # Robust: check existing worksheets first (avoid false negatives)
    ws = None
    for w in sh.worksheets():
        if w.title.strip() == tab:
            ws = w
            break

    if ws is None:
        try:
            ws = sh.add_worksheet(title=tab, rows=200, cols=len(REQUIRED_HEADERS))
            print(f"[INFO] Created worksheet -> {tab}")
        except Exception as e:
            print("[WARN] add_worksheet failed, trying to fetch by title:", e)
            # If race or API quirk, fetch by title again
            ws = sh.worksheet(tab)

    _ensure_headers(ws)
    return ws


def existing_keys(ws) -> set:
    try:
        vals = ws.col_values(12)[1:]
    except Exception:
        vals = []
    return {v for v in vals if v}

def append_rows(ws, rows):
    if not rows:
        return
    ws.append_rows(rows, value_input_option="RAW")
