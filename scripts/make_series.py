
import os
from datetime import datetime

import numpy as np
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import (
    generate_uid,
    CTImageStorage,
    ExplicitVRLittleEndian,
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

OUTPUT_DIR = os.path.join("data", "demo_series")

NUM_SLICES = 100
IMAGE_SIZE = 512

PIXEL_SPACING = [0.7, 0.7]  # mm
SLICE_THICKNESS = 1.0       # mm
SLICE_SPACING = 1.0         # mm

NOISE_SIGMA = 8.0           # HU


# ============================================================
# 2. CREATE SYNTHETIC ABDOMINAL CT IMAGE
# ============================================================


def create_ct_slice(slice_index):

    size = IMAGE_SIZE

    y, x = np.mgrid[-1:1:complex(size), -1:1:complex(size)]

    # Normalized position along Z
    z = (slice_index - (NUM_SLICES - 1) / 2) / NUM_SLICES

    # Initialize image with air
    image = np.full((size, size), -1000.0, dtype=np.float32)

    # Body contour: slight variation along Z
    body_mask = (
        (x / (0.78 - 0.025 * abs(z))) ** 2 +
        (y / (0.88 - 0.02 * abs(z))) ** 2
    ) <= 1.0

    image[body_mask] = -100.0

    # Internal soft tissue
    internal_mask = (
        (x / 0.70) ** 2 +
        (y / 0.78) ** 2
    ) <= 1.0

    image[internal_mask] = 40.0

    # Liver: changes in size and position along Z
    liver_scale = 1.0 - 0.18 * abs(z)

    liver_mask = (
        ((x + 0.25) / (0.27 * liver_scale)) ** 2 +
        ((y + 0.05) / (0.38 * liver_scale)) ** 2
    ) <= 1.0

    image[liver_mask] = 65.0

    # Spleen
    spleen_scale = 1.0 - 0.12 * abs(z)

    spleen_mask = (
        ((x - 0.40) / (0.13 * spleen_scale)) ** 2 +
        ((y + 0.08) / (0.22 * spleen_scale)) ** 2
    ) <= 1.0

    image[spleen_mask] = 55.0

    # Right kidney
    kidney_scale = 1.0 - 0.10 * abs(z)

    kidney_right = (
        ((x + 0.35) / (0.12 * kidney_scale)) ** 2 +
        ((y - 0.22) / (0.20 * kidney_scale)) ** 2
    ) <= 1.0

    image[kidney_right] = 35.0

    # Left kidney
    kidney_left = (
        ((x - 0.30) / (0.12 * kidney_scale)) ** 2 +
        ((y - 0.22) / (0.20 * kidney_scale)) ** 2
    ) <= 1.0

    image[kidney_left] = 35.0

    # Aorta
    aorta_mask = (
        ((x - 0.02) / 0.055) ** 2 +
        ((y - 0.12) / 0.055) ** 2
    ) <= 1.0

    image[aorta_mask] = 40.0

    # Vertebra
    vertebra_mask = (
        (x / 0.12) ** 2 +
        ((y - 0.48) / 0.11) ** 2
    ) <= 1.0

    image[vertebra_mask] = 300.0

    # Add Gaussian noise
    rng = np.random.default_rng(seed=slice_index)

    noise = rng.normal(
        loc=0.0,
        scale=NOISE_SIGMA,
        size=(size, size)
    )

    image += noise

    # Convert to signed 16-bit pixel values
    image = np.clip(image, -32768, 32767)

    return image.astype(np.int16)


# ============================================================
# 3. WRITE ONE DICOM SLICE
# ============================================================

def save_dicom_slice(
    pixel_array,
    slice_index,
    study_uid,
    series_uid,
    frame_uid,
    study_date,
    study_time,
):

    sop_uid = generate_uid()

    file_meta = FileMetaDataset()

    file_meta.MediaStorageSOPClassUID = CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = sop_uid
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()

    filename = os.path.join(
        OUTPUT_DIR,
        f"CT_{slice_index + 1:04d}.dcm"
    )

    ds = FileDataset(
        filename,
        {},
        file_meta=file_meta,
        preamble=b"\0" * 128
    )

    # Patient information
    ds.PatientName = "NGUYEN^VAN^A"
    ds.PatientID = "551249"
    ds.PatientBirthDate = "20051106"
    ds.PatientSex = "M"

    # Study information
    ds.StudyInstanceUID = study_uid
    ds.StudyDate = study_date
    ds.StudyTime = study_time
    ds.StudyID = "STUDY001"
    ds.StudyDescription = "Demo CT"

    # Series information
    ds.SeriesInstanceUID = series_uid
    ds.SeriesNumber = 1
    ds.SeriesDescription = "Demo CT Series"
    ds.Modality = "CT"

    # Instance information
    ds.SOPClassUID = CTImageStorage
    ds.SOPInstanceUID = sop_uid
    ds.InstanceNumber = slice_index + 1

    # Image geometry
    ds.FrameOfReferenceUID = frame_uid

    ds.Rows = IMAGE_SIZE
    ds.Columns = IMAGE_SIZE

    ds.PixelSpacing = PIXEL_SPACING
    ds.SliceThickness = SLICE_THICKNESS
    ds.SpacingBetweenSlices = SLICE_SPACING

    ds.ImageOrientationPatient = [
        1, 0, 0,
        0, 1, 0
    ]

    x_position = -((IMAGE_SIZE - 1) * PIXEL_SPACING[1]) / 2
    y_position = -((IMAGE_SIZE - 1) * PIXEL_SPACING[0]) / 2

    z_position = slice_index * SLICE_SPACING

    ds.ImagePositionPatient = [
        x_position,
        y_position,
        z_position
    ]

    ds.SliceLocation = z_position

    # Pixel information
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"

    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1

    # Convert stored pixel values to HU
    ds.RescaleIntercept = 0
    ds.RescaleSlope = 1
    ds.RescaleType = "HU"

    ds.WindowCenter = 40
    ds.WindowWidth = 400

    # Acquisition information
    ds.KVP = 120
    ds.XRayTubeCurrent = 100

    # Pixel data
    ds.PixelData = pixel_array.tobytes()

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Save DICOM file
    ds.save_as(filename, enforce_file_format=True)

    return filename


# ============================================================
# 4. GENERATE COMPLETE CT SERIES
# ============================================================

def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    study_uid = generate_uid()
    series_uid = generate_uid()
    frame_uid = generate_uid()

    now = datetime.now()

    study_date = now.strftime("%Y%m%d")
    study_time = now.strftime("%H%M%S.%f")

    print("Generating synthetic abdominal CT...")
    print(f"Number of slices: {NUM_SLICES}")
    print(f"Image size: {IMAGE_SIZE} x {IMAGE_SIZE}")

    for i in range(NUM_SLICES):

        pixel_array = create_ct_slice(i)

        filename = save_dicom_slice(
            pixel_array,
            i,
            study_uid,
            series_uid,
            frame_uid,
            study_date,
            study_time
        )

        print(f"[{i + 1:03d}/{NUM_SLICES}] {filename}")

    print("\nCT SERIES GENERATION COMPLETED")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Study UID: {study_uid}")
    print(f"Series UID: {series_uid}")


if __name__ == "__main__":
    main()
