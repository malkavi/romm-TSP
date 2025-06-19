import os
from typing import Optional

import platform_maps
from models import Rom, Save

import re
import time


class Filesystem:
    _instance: Optional["Filesystem"] = None

    # Check if app is running on muOS
    is_muos = os.path.exists("/mnt/mmc/MUOS")

    # Check is app is running on SpruceOS
    is_spruceos = os.path.exists("/mnt/SDCARD/spruce")
    
    # Check is app is running on TrimUI
    is_trimui_stock = os.path.exists("/mnt/SDCARD/Roms") or (os.getenv("CFW_NAME", "") == "TrimUI")

    # Storage paths for ROMs
    _sd1_roms_storage_path: str
    _sd2_roms_storage_path: str | None

    # Storage paths for SAVEs
    _saves_storage_path: str | None

    # Storage paths for STATEs
    _states_storage_path: str | None

    # Resources path: Use current working directory + "resources"
    resources_path = os.path.join(os.getcwd(), "resources")

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Filesystem, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Optionally ensure resources directory exists (not required for roms dir)
        if not os.path.exists(self.resources_path):
            os.makedirs(self.resources_path, exist_ok=True)

        # ROMs storage path
        if os.environ.get("ROMS_STORAGE_PATH", "") != "":
            # if the environment variable is set, use it
            self._sd1_roms_storage_path = os.environ["ROMS_STORAGE_PATH"]
            self._sd2_roms_storage_path = None
        else:
            if self.is_muos:
                self._sd1_roms_storage_path = "/mnt/mmc/ROMS"
                self._sd2_roms_storage_path = "/mnt/sdcard/ROMS"
            elif self.is_spruceos:
                self._sd1_roms_storage_path = "/mnt/SDCARD/Roms"
                self._sd2_roms_storage_path = None
            elif self.is_trimui_stock:
                self._sd1_roms_storage_path = "/mnt/SDCARD/Roms"
                self._sd2_roms_storage_path = None    
            else:
                # Go up two levels from the script's directory (e.g., from roms/ports/romm to roms/)
                base_path = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
                # Default to the ROMs directory, overridable via environment variable
                self._sd1_roms_storage_path = os.environ.get("ROMS_STORAGE_PATH", base_path)
                self._sd2_roms_storage_path = None

        # Ensure the ROMs storage path exists
        if self._sd2_roms_storage_path and not os.path.exists(
            self._sd2_roms_storage_path
        ):
            os.mkdir(self._sd2_roms_storage_path)

        # Set the default SD card based on the existence of the storage path
        self._current_sd = int(
            os.getenv(
                "DEFAULT_SD_CARD",
                1 if os.path.exists(self._sd1_roms_storage_path) else 2,
            )
        )

        # SAVEs storage path
        self._saves_storage_path = os.environ.get("SAVES_STORAGE_PATH", None)
        # SAVEs storage folder
        self._saves_storage_folder = int(os.environ.get("SAVES_STORAGE_FOLDER", 0))

        # STATEs storage path
        self._states_storage_path = os.environ.get("STATES_STORAGE_PATH", None)
        # SAVEs storage folder
        self._states_storage_folder = int(os.environ.get("STATES_STORAGE_FOLDER", 0))

    ###
    # PRIVATE METHODS
    ###
    def _get_sd1_roms_storage_path(self) -> str:
        """Return the base ROMs storage path."""
        return self._sd1_roms_storage_path

    def _get_sd2_roms_storage_path(self) -> Optional[str]:
        """Return the secondary ROMs storage path if available."""
        return self._sd2_roms_storage_path

    def _get_platform_storage_dir_from_mapping(self, platform: str) -> str:
        """
        Return the platform-specific storage path,
        using MUOS mapping if on muOS,
        or SpruceOS mapping if on SpruceOS,
        or TrimUI mapping if on TrimUI,
        or using ES mapping if available.
        """

        # First check if the platform has an entry in the ES map
        platform_dir = platform_maps.ES_FOLDER_MAP.get(platform, platform)

        # If the ES map returns a tuple, use the first element of the tuple
        if isinstance(platform_dir, tuple):
            platform_dir = platform_dir[0]

        # If running on muOS, override the platform_dir with the MUOS mapping
        if self.is_muos:
            platform_dir = platform_maps.MUOS_SUPPORTED_PLATFORMS_FS_MAP.get(
                platform, platform_dir
            )

        if self.is_spruceos:
            platform_dir = platform_maps.SPRUCEOS_SUPPORTED_PLATFORMS_FS_MAP.get(
                platform, platform_dir
            )
        
        if self.is_trimui_stock:
            platform_dir = platform_maps.TRIMUI_STOCK_SUPPORTED_PLATFORMS_FS_MAP.get(
                platform, platform_dir
            )

        if platform_maps._env_maps and platform in platform_maps._env_platforms:
            platform_dir = platform_maps._env_maps.get(platform, platform_dir)

        return platform_dir

    def _get_sd1_platforms_storage_path(self, platform: str) -> str:
        platforms_dir = self._get_platform_storage_dir_from_mapping(platform)
        return os.path.join(self._sd1_roms_storage_path, platforms_dir)

    def _get_sd2_platforms_storage_path(self, platform: str) -> Optional[str]:
        if self._sd2_roms_storage_path:
            platforms_dir = self._get_platform_storage_dir_from_mapping(platform)
            return os.path.join(self._sd2_roms_storage_path, platforms_dir)
        return None

    def _get_saves_storage_path(self, platform: str, emulator: str) -> str:
        saves_dir = ""
        saves_path = self._saves_storage_path
        # 0: Directly in the path
        if self._saves_storage_folder == 1:
            # 1: Use Core name subfolder
            saves_dir = emulator
            if saves_dir is None:
                saves_dir = ""
        elif self._saves_storage_folder == 2:
            # 2: Use platform name subfolder (Knulli)
            saves_dir = self._get_platform_storage_dir_from_mapping(platform)
        elif self._saves_storage_folder == 3:
            # 3: Use content path (with the rom, ignore saves path)
            saves_path = self._sd1_roms_storage_path
        if saves_path is None:
            return None
        return os.path.join(saves_path, saves_dir)
    
    def _get_states_storage_path(self, platform: str, emulator: str) -> str:
        states_dir = ""
        states_path = self._states_storage_path
        # 0: Directly in the path
        if self._states_storage_folder == 1:
            # 1: Use Core name subfolder
            states_dir = emulator
            if states_dir is None:
                states_dir = ""
        elif self._states_storage_folder == 2:
            # 2: Use platform name subfolder (Knulli)
            states_dir = self._get_platform_storage_dir_from_mapping(platform)
        elif self._states_storage_folder == 3:
            # 3: Use content path (with the rom, ignore states path)
            states_path = self._sd1_roms_storage_path
        if states_path is None:
            return None
        return os.path.join(states_path, states_dir)

    ###
    # PUBLIC METHODS
    ###

    def switch_sd_storage(self) -> None:
        """Switch the current SD storage path."""
        if self._current_sd == 1:
            self._current_sd = 2
        else:
            self._current_sd = 1

    def get_roms_storage_path(self) -> str:
        """Return the current SD storage path."""
        if self._current_sd == 2 and self._sd2_roms_storage_path:
            return self._sd2_roms_storage_path

        return self._sd1_roms_storage_path

    def get_platforms_storage_path(self, platform: str) -> str:
        """Return the storage path for a specific platform."""
        if self._current_sd == 2:
            storage_path = self._get_sd2_platforms_storage_path(platform)
            if storage_path:
                return storage_path

        return self._get_sd1_platforms_storage_path(platform)

    def is_rom_in_device(self, rom: Rom) -> bool:
        """Check if a ROM exists in the storage path."""
        rom_path = os.path.join(
            self.get_platforms_storage_path(rom.platform_slug),
            rom.fs_name if not rom.multi else f"{rom.fs_name}.m3u",
        )
        return os.path.exists(rom_path)
    
    def is_save_state_in_device(self, platform_slug, save: Save) -> bool:
        """Check if a ROM exists in the storage path."""
        # TODO: Implement a more robust check for save states
        # Get server/file time from tag
        _date_pattern = r"\[([0-9]{4}.[0-9]{1,2}.[0-9]{1,2} [0-9]{1,2}-[0-9]{1,2}).*\]"
        _date = re.findall(_date_pattern, save.file_name)
        # Get real path, without the time tag
        _fs_name = save.rom_name + "." + save.file_extension
        # Compare real path file creation/modification time with the save time tag
        save_path = os.path.join(
            self.get_saves_states_storage_path(False, platform_slug, save.emulator),
            _fs_name,
        )
        state_path = os.path.join(
            self.get_saves_states_storage_path(True, platform_slug, save.emulator),
            _fs_name,
        )

        if os.path.exists(save_path) or os.path.exists(state_path):
            if len(_date) == 0:
                # If no date tag, just check if the file exists
                return os.path.exists(save_path) or os.path.exists(state_path)
            
            _ceate_time = 0.0
            _mod_time = 0.0
            # Get the file access and modification time
            if os.path.exists(save_path):
                _ceate_time = os.path.getatime(save_path)
                _mod_time = os.path.getmtime(save_path)
            elif os.path.exists(state_path):
                _ceate_time = os.path.getatime(state_path)
                _mod_time = os.path.getmtime(state_path)

            _c_ti = time.ctime(_ceate_time)
            _m_ti = time.ctime(_mod_time)

            _T_stamp_cre = time.strftime("%Y-%m-%d %H-%M", time.strptime(_c_ti))
            _T_stamp_mod = time.strftime("%Y-%m-%d %H-%M", time.strptime(_m_ti))

            return (_T_stamp_cre == _date[0]) or (_T_stamp_mod == _date[0])
        else:
            return False
    
    def get_saves_states_storage_path(self, sel_state, platform: str, emulator: str) -> str:
        """Return the storage path for a specific save/state."""
        if sel_state:
            # Save state path
            return self._get_states_storage_path(platform, emulator)
        # Save path
        return self._get_saves_storage_path(platform, emulator)
