from pathlib import Path

from .base import NiconicoUserIconCacheStorageManager


class NiconicoUserIconCacheStorageFileManager(NiconicoUserIconCacheStorageManager):
    def __init__(
        self,
        niconico_user_icon_dir: Path,
    ):
        self.niconico_user_icon_dir = niconico_user_icon_dir

    def __create_niconico_user_icon_path(
        self,
        file_key: str,
        content_type: str,
    ) -> Path:
        niconico_user_icon_dir = self.niconico_user_icon_dir

        suffix: str | None = None
        if content_type == "image/jpeg":
            suffix = ".jpg"
        elif content_type == "image/png":
            suffix = ".png"
        elif content_type == "image/gif":
            suffix = ".gif"
        else:
            raise Exception(
                f"Unsupported content_type: {content_type}",
            )

        file_name = f"{file_key}{suffix}"
        return niconico_user_icon_dir / file_name

    def check_exists(
        self,
        file_key: str,
        content_type: str,
    ) -> bool:
        path = self.__create_niconico_user_icon_path(
            file_key=file_key,
            content_type=content_type,
        )
        return path.exists()

    def save(
        self,
        file_key: str,
        content_type: str,
        content: bytes,
    ) -> None:
        path = self.__create_niconico_user_icon_path(
            file_key=file_key,
            content_type=content_type,
        )
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_bytes(content)
