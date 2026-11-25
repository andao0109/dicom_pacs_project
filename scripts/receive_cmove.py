
import os
from pathlib import Path

from pynetdicom import AE, evt
from pynetdicom.sop_class import CTImageStorage


# ==============================
# Configuration
# ==============================

AE_TITLE = "REMOTE"
PORT = 11112

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "data" / "cmove_received"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# C-STORE Handler
# ==============================

def handle_store(event):
    try:
        ds = event.dataset
        ds.file_meta = event.file_meta

        filename = f"{ds.SOPInstanceUID}.dcm"
        filepath = OUTPUT_DIR / filename

        ds.save_as(filepath, enforce_file_format=True)

        print(f"Received: {filename}")

        return 0x0000

    except Exception as e:
        print(f"Storage error: {e}")
        return 0xC210


# ==============================
# Start DICOM Receiver
# ==============================

handlers = [
    (evt.EVT_C_STORE, handle_store)
]

ae = AE(ae_title=AE_TITLE)

ae.add_supported_context(CTImageStorage)

print("================================")
print("DICOM C-MOVE RECEIVER")
print("================================")
print(f"AE Title : {AE_TITLE}")
print(f"Port     : {PORT}")
print(f"Output   : {OUTPUT_DIR}")
print("Waiting for incoming DICOM images...")

ae.start_server(
    ("0.0.0.0", PORT),
    evt_handlers=handlers,
    block=True
)
