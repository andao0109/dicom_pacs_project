
import argparse
from collections import Counter
from pathlib import Path

from pydicom import dcmread
from pynetdicom import AE


# PACS configuration
PACS_IP = "127.0.0.1"
PACS_PORT = 4242
PACS_AET = "ORTHANC"

MODALITY_AET = "IMAGING_SENDER"

PROJECT_DIR = Path(__file__).resolve().parent.parent


def sort_key(item):
    """Keep images in study/series/instance order when those fields exist."""
    _, header = item
    instance = header.get("InstanceNumber", 0)
    try:
        instance = int(instance)
    except (TypeError, ValueError):
        instance = 0

    return (
        str(header.get("StudyInstanceUID", "")),
        str(header.get("SeriesInstanceUID", "")),
        instance,
    )


parser = argparse.ArgumentParser(
    description="Send CT, MR, X-ray, or other DICOM images to the PACS."
)
parser.add_argument(
    "dicom_dir",
    nargs="?",
    default=PROJECT_DIR / "data" / "real_series" / "chest_xray",
    type=Path,
    help="Folder containing DICOM files (default: data/real_series/brain_mri)",
)
args = parser.parse_args()
dicom_dir = args.dicom_dir
if not dicom_dir.is_absolute():
    dicom_dir = PROJECT_DIR / dicom_dir

if not dicom_dir.is_dir():
    raise SystemExit(f"DICOM directory does not exist: {dicom_dir}")

# Read headers first.  SOP Class, rather than Modality, determines the
# presentation context, so this works for CT, MR, CR/DX X-ray, etc.
dicom_images = []
for file_path in dicom_dir.rglob("*.dcm"):
    try:
        header = dcmread(str(file_path), stop_before_pixels=True)
        dicom_images.append((file_path, header))
    except Exception as error:
        print(f"Skipped unreadable file: {file_path.name} ({error})")

dicom_images.sort(key=sort_key)

if not dicom_images:
    raise SystemExit(f"No readable .dcm files found in: {dicom_dir}")

modality_counts = Counter(str(header.get("Modality", "Unknown")) for _, header in dicom_images)
print(f"Found {len(dicom_images)} DICOM files: {dict(modality_counts)}")

# Register every SOP Class found in the selected folder before associating.
ae = AE(ae_title=MODALITY_AET)
for sop_class_uid in {header.SOPClassUID for _, header in dicom_images}:
    ae.add_requested_context(sop_class_uid)

assoc = ae.associate(PACS_IP, PACS_PORT, ae_title=PACS_AET)
if not assoc.is_established:
    raise SystemExit("Failed to establish DICOM Association.")

print("DICOM Association established successfully.")

success_count = 0
failed_count = 0
for file_path, _ in dicom_images:
    ds = dcmread(str(file_path))
    status = assoc.send_c_store(ds)

    if status and status.Status == 0x0000:
        success_count += 1
        print(f"Sent: {file_path.name} ({ds.get('Modality', 'Unknown')})")
    else:
        failed_count += 1
        print(f"Failed: {file_path.name}")

print("\nDICOM Transfer Summary")
print(f"Total files: {len(dicom_images)}")
print(f"Successful: {success_count}")
print(f"Failed: {failed_count}")

assoc.release()
print("DICOM Association released.")
