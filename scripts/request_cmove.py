
from pynetdicom import AE
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove
from pydicom.dataset import Dataset


# DICOM server configuration
ORTHANC_HOST = "127.0.0.1"
ORTHANC_PORT = 4242
ORTHANC_AET = "ORTHANC"

# Destination AE Title
DESTINATION_AET = "REMOTE"

# CT Study Instance UID
STUDY_UID = (
    "1.2.826.0.1.3680043.2.1125.1."
    "4580172341793260085690432059380843"
)


# Create DICOM Application Entity
ae = AE(ae_title="MOVESCU")

ae.add_requested_context(
    StudyRootQueryRetrieveInformationModelMove
)

# Create C-MOVE query
query = Dataset()
query.QueryRetrieveLevel = "STUDY"
query.StudyInstanceUID = STUDY_UID


print("Connecting to Orthanc...")

assoc = ae.associate(
    ORTHANC_HOST,
    ORTHANC_PORT,
    ae_title=ORTHANC_AET
)

if assoc.is_established:
    print("Association established.")
    print("Sending C-MOVE request...")

    responses = assoc.send_c_move(
        query,
        DESTINATION_AET,
        StudyRootQueryRetrieveInformationModelMove
    )

    for status, identifier in responses:
        if status:
            print(
                f"C-MOVE status: 0x{status.Status:04X}"
            )

            if hasattr(status, "NumberOfCompletedSuboperations"):
                print(
                    "Completed:",
                    status.NumberOfCompletedSuboperations
                )

            if hasattr(status, "NumberOfRemainingSuboperations"):
                print(
                    "Remaining:",
                    status.NumberOfRemainingSuboperations
                )

            if hasattr(status, "NumberOfFailedSuboperations"):
                print(
                    "Failed:",
                    status.NumberOfFailedSuboperations
                )
        else:
            print("Connection lost or invalid response.")

    assoc.release()
    print("Association released.")

else:
    print("Could not connect to Orthanc.")
