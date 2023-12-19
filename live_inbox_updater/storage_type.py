from typing import Literal, TypeGuard

StorageType = Literal["file", "s3"]


def validate_storage_type_string(
    string: str,
) -> TypeGuard[StorageType]:
    if string == "file":
        return True

    if string == "s3":
        return True

    return False
