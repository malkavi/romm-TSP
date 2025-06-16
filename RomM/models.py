from collections import namedtuple

Rom = namedtuple(
    "Rom",
    [
        "id",
        "name",
        "fs_name",
        "platform_slug",
        "fs_extension",
        "fs_size",
        "fs_size_bytes",
        "multi",
        "languages",
        "regions",
        "revision",
        "tags",
    ],
)
Collection = namedtuple("Collection", ["id", "name", "rom_count", "virtual"])
Platform = namedtuple("Platform", ["id", "display_name", "slug", "rom_count"])
Save = namedtuple(
    "Saves", 
    [
        "id",
        "rom_id",
        "user_id",
        "file_name",
        "file_name_no_tags",
        "file_name_no_ext",
        "file_extension",
        "file_path",
        "file_size_bytes",
        "full_path",
        "download_path",
        "created_at",
        "updated_at",
        "emulator",
        "screenshot",
        "platform_slug",  # platform slug for the download path
        "rom_name",  # name of the rom for the download path
        "is_state",  # True if this is a save state, False if it's a save
    ])
ScreenShot = namedtuple(
    "screenshot",
    [
        "id",
        "rom_id",
        "user_id",
        "file_name",
        "file_name_no_tags",
        "file_name_no_ext",
        "file_extension",
        "file_path",
        "file_size_bytes",
        "full_path",
        "download_path",
        "created_at",
        "updated_at",
    ]) 
