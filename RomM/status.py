import itertools
import threading
from typing import Optional

from models import Collection, Platform, Rom, Save


class View:
    PLATFORMS = "platform"
    COLLECTIONS = "collection"
    VIRTUAL_COLLECTIONS = "virtual_collection"
    ROMS = "roms"
    ROM_INFO = "rom_info"


class Filter:
    ALL = "all"
    LOCAL = "local"
    REMOTE = "remote"


class Status:
    _instance: Optional["Status"] = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Status, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.valid_host = True
        self.valid_credentials = True

        self.me = None
        self.profile_pic_path = ""

        self.current_view: str = View.PLATFORMS
        self.selected_platform: Optional[Platform] = None
        self.selected_collection: Optional[Collection] = None
        self.selected_virtual_collection: Optional[Collection] = None
        self.selected_rom: Optional[Rom] = None

        self.selected_user_id = 1
        self.selected_states_get = False

        self.show_start_menu = False
        self.show_contextual_menu = False

        self.platforms: list[Platform] = []
        self.collections: list[Collection] = []
        self.roms: list[Rom] = []
        self.roms_to_show: list[Rom] = []
        self.filters = itertools.cycle([Filter.ALL, Filter.LOCAL, Filter.REMOTE])
        self.current_filter = next(self.filters)
        self.saves: list[Save] = []
        self.states: list[Save] = []
        self.saves_states_to_show: list[Save] = []

        self.platforms_ready = threading.Event()
        self.collections_ready = threading.Event()
        self.roms_ready = threading.Event()
        self.download_rom_ready = threading.Event()
        self.saves_ready = threading.Event()
        self.rom_info_ready = threading.Event()
        self.abort_download = threading.Event()
        self.me_ready = threading.Event()
        self.updating = threading.Event()

        # Initialize events what won't launch at startup
        self.roms_ready.set()
        self.saves_ready.set()
        self.rom_info_ready.set()
        self.download_rom_ready.set()
        self.abort_download.set()

        self.multi_selected_roms: list[Rom] = []
        self.download_queue: list[Rom] = []
        self.downloading_rom: Optional[Rom] = None
        self.downloading_rom_position = 0
        self.total_downloaded_bytes = 0
        self.downloaded_percent = 0.0
        self.extracting_rom = False
        self.extracted_percent = 0.0

        self.download_queue_saves: list[Save] = []
        self.downloading_save: Optional[Save] = None
        self.downloading_save_position = 0

    def reset_roms_list(self) -> None:
        self.roms = []
