import json
import os

# Manual mapping of RomM slugs to device folder names and platform icons for es systems
# This is sometimes needed to match custom system folders with defaults, for example ES-DE uses roms/gc and some Batocera forks use roms/gamecube
# https://gitlab.com/es-de/emulationstation-de/-/blob/master/resources/systems/unix/es_systems.xml

# EmulationStation custom folder map
ES_FOLDER_MAP = {
    # "slug": ("es-system", "icon"),
    "ngc": ("gamecube", "ngc"),  # Nintendo GameCube
    "n3ds": ("3ds", "3ds"),  # Nintendo 3DS
    "genesis": ("genesis", "genesis-slash-megadrive"),  # Sega Genesis / Megadrive
    "megadrive": ("megadrive", "genesis-slash-megadrive"),  # Sega Genesis / Megadrive
    "mastersystem": ("mastersystem", "sega-master-system"),  # Sega Mastersystem
}

# Manual mapping of RomM slugs for MuOS default platforms
MUOS_SUPPORTED_PLATFORMS_FS_MAP = {
    "acpc": "Amstrad",
    "arcade": "Arcade",
    "arduboy": "Arduboy",
    "atari2600": "Atari 2600",
    "atari5200": "Atari 5200",
    "atari7800": "Atari 7800",
    "jaguar": "Atari Jaguar",
    "lynx": "Atari Lynx",
    "atari-st": "Atari ST-STE-TT-Falcon",
    "wonderswan": "Bandai WonderSwan-Color",
    "wonderswan-color": "Book Reader",
    "cave-story": "Cave Story",
    "chailove": "ChaiLove",
    "chip-8": "CHIP-8",
    "colecovision": "ColecoVision",
    "amiga": "Commodore Amiga",
    "c128": "Commodore C128",
    "c64": "Commodore C64",
    "cbm-ii": "Commodore CBM-II",
    "cpet": "Commodore PET",
    "vic-20": "Commodore VIC-20",
    "dos": "DOS",
    "doom": "Doom",
    "ports": "External - Ports",
    "fairchild-channel-f": "Fairchild ChannelF",
    "vectrex": "GCE - Vectrex",
    "galaksija": "Galaksija Retro Computer",
    "g-and-w": "Handheld Electronic - Game and Watch",
    "j2me": "Java J2ME",
    "karaoke": "Karaoke",
    "lowres": "Lowres NX",
    "lua": "Lua Engine",
    "odyssey--1": "Magnavox Odyssey - VideoPac",
    "intellivision": "Mattel - Intellivision",
    "media-player": "Media Player",
    "mega-duck-slash-cougar-boy": "Mega Duck",
    "msx": "Microsoft - MSX",
    "turbografx-16-slash-pc-engine-cd": "NEC PC Engine CD",
    "supergrafx": "NEC PC Engine SuperGrafx",
    "turbografx16--1": "NEC PC Engine",
    "pc-8000": "NEC PC-8000 - PC-8800 series",
    "pc-fx": "NEC PC-FX",
    "pc-9800-series": "NEC PC98",
    "nds": "Nintendo DS",
    "fds": "Nintendo FDS",
    "gba": "Nintendo Game Boy Advance",
    "gbc": "Nintendo Game Boy Color",
    "gb": "Nintendo Game Boy",
    "n64": "Nintendo N64",
    "nes": "Nintendo NES-Famicom",
    "famicom": "Nintendo NES-Famicom",
    "snes": "Nintendo SNES-SFC",
    "sfam": "Nintendo SNES-SFC",
    "pokemon-mini": "Nintendo Pokemon Mini",
    "virtualboy": "Nintendo Virtual Boy",
    "onscripter": "Onscripter",
    "openbor": "OpenBOR",
    "pico-8": "PICO-8",
    "philips-cd-i": "Philips CDi",
    "quake": "Quake",
    "rpg-maker": "RPG Maker 2000 - 2003",
    "neogeoaes": "SNK Neo Geo",
    "neogeomvs": "SNK Neo Geo",
    "neo-geo-cd": "SNK Neo Geo CD",
    "neo-geo-pocket": "SNK Neo Geo Pocket - Color",
    "neo-geo-pocket-color": "SNK Neo Geo Pocket - Color",
    "scummvm": "ScummVM",
    "sega32": "Sega 32X",
    "naomi": "Sega Atomiswave Naomi",
    "dc": "Sega Dreamcast",
    "gamegear": "Sega Game Gear",
    "sega-master-system": "Sega Master System",
    "genesis-slash-megadrive": "Sega Mega Drive - Genesis",
    "sega-pico": "Sega Pico",
    "segacd": "Sega Mega CD - Sega CD",
    "sg1000": "Sega SG-1000",
    "saturn": "Sega Saturn",
    "x1": "Sharp X1",
    "sharp-x68000": "Sharp X68000",
    "sinclair-zx81": "Sinclair ZX 81",
    "zxs": "Sinclair ZX Spectrum",
    "ps": "Sony Playstation",
    "psp": "Sony Playstation Portable",
    "tic-80": "TIC-80",
    "ti-83": "Texas Instruments TI-83",
    "3do": "The 3DO Company - 3DO",
    "uzebox": "Uzebox",
    "vemulator": "VeMUlator",
    "vircon-32": "Vircon32",
    "wasm-4": "WASM-4",
    "watara-slash-quickshot-supervision": "Watara Supervision",
    "wolfenstein-3d": "Wolfenstein 3D",
}

MUOS_SUPPORTED_PLATFORMS = frozenset(MUOS_SUPPORTED_PLATFORMS_FS_MAP.keys())
MUOS_SUPPORTED_PLATFORMS_FS = frozenset(MUOS_SUPPORTED_PLATFORMS_FS_MAP.values())

SPRUCEOS_SUPPORTED_PLATFORMS_FS_MAP = {
    "amiga": "AMIGA",
    "acpc": "CPC",
    "arcade": "ARCADE",
    "arduboy": "ARDUBOY",
    "atari2600": "ATARI",
    "atari8bit": "EIGHTHUNDRED",
    "atari5200": "FIFTYTWOHUNDRED",
    "atari7800": "SEVENTYEIGHTHUNDRED",
    "lynx": "LYNX",
    "sufami": "SUFAMI",
    "wonderswan": "WS",
    "wonderswan-color": "WSC",
    "cps1": "CPS1",
    "cps2": "CPS2",
    "cps3": "CPS3",
    "colecovision": "COLECO",
    "c64": "COMMODORE",
    "vic-20": "VIC20",
    "doom": "DOOM",
    "fairchild-channel-f": "FAIRCHILD",
    "fds": "FDS",
    "g-and-w": "GW",
    "vectrex": "VECTREX",
    "odyssey-2-slash-videopac-g7000": "ODYSSEY",
    "mame2003plus": "MAME2003PLUS",
    "intellivision": "INTELLIVISION",
    "mega-duck-slash-cougar-boy": "MEGADUCK",
    "dos": "DOS",
    "msx": "MSX",
    "msx2": "MSX",  # same folder for both MSX and MSX2
    "supergrafx": "SGFX",
    "pcecd": "PCECD",
    "turbografx16--1": "PCE",
    "turbografx-16-slash-pc-engine-cd": "PCE",
    "n64": "N64",
    "nds": "NDS",
    "nes": "FC",
    "gba": "GBA",
    "gbc": "GBC",
    "gb": "GB",
    "pokemon-mini": "POKE",
    "satellaview": "SATELLAVIEW",
    "sgb": "SGB",
    "snes": "SFC",
    "virtualboy": "VB",
    "openbor": "OPENBOR",
    "fake08": "FAKE08",
    "pico": "PICO8",
    "psp": "PSP",
    "quake": "QUAKE",
    "scummvm": "SCUMMVM",
    "sega32": "THIRTYTWOX",
    "segacd": "SEGACD",
    "dc": "DC",
    "gamegear": "GG",
    "msumd": "MSUMD",
    "genesis-slash-megadrive": "MD",
    "mastersystem": "MS",
    "sg1000": "SEGASGONE",
    "sharp-x68000": "X68000",
    "zxspectrum": "ZXS",
    "msu1": "MSU1",
    "neo-geo-cd": "NEOCD",
    "ngp": "NGP",
    "ngpc": "NGPC",
    "neogeoaes": "NEOGEO",
    "neogeomvs": "NEOCD",
    "psx": "PS",
    "saturn": "SATURN",
    "tic80": "TIC",
    "videopac-g7400": "VIDEOPAC",
    "supervision": "SUPERVISION",
    "wolf3d": "WOLF",
}

# Manual mapping of RomM slugs for SpruceOS default platforms
SPRUCEOS_SUPPORTED_PLATFORMS = frozenset(SPRUCEOS_SUPPORTED_PLATFORMS_FS_MAP.keys())
SPRUCEOS_SUPPORTED_PLATFORMS_FS = frozenset(
    SPRUCEOS_SUPPORTED_PLATFORMS_FS_MAP.values()
)

TRIMUI_STOCK_SUPPORTED_PLATFORMS_FS_MAP = {
    "acpc": "Amstrad",
    "arcade": "ARCADE",
    "arduboy": "Arduboy",
    "atari2600": "ATARI2600",
    "atari5200": "Atari 5200",
    "atari7800": "ATARI7800",
    "jaguar": "Atari Jaguar",
    "lynx": "LYNX",
    "atari-st": "Atari ST-STE-TT-Falcon",
    "wonderswan": "Bandai WonderSwan-Color",
    "wonderswan-color": "Book Reader",
    "cave-story": "Cave Story",
    "chailove": "ChaiLove",
    "chip-8": "CHIP-8",
    "colecovision": "ColecoVision",
    "amiga": "Commodore Amiga",
    "c128": "Commodore C128",
    "c64": "Commodore C64",
    "cbm-ii": "Commodore CBM-II",
    "cpet": "Commodore PET",
    "vic-20": "Commodore VIC-20",
    "dos": "DOS",
    "doom": "Doom",
    "ports": "PORTS",
    "fairchild-channel-f": "Fairchild ChannelF",
    "vectrex": "GCE - Vectrex",
    "galaksija": "Galaksija Retro Computer",
    "g-and-w": "Handheld Electronic - Game and Watch",
    "j2me": "Java J2ME",
    "karaoke": "Karaoke",
    "lowres": "Lowres NX",
    "lua": "Lua Engine",
    "odyssey--1": "Magnavox Odyssey - VideoPac",
    "intellivision": "Mattel - Intellivision",
    "media-player": "Media Player",
    "mega-duck-slash-cougar-boy": "Mega Duck",
    "msx": "Microsoft - MSX",
    "turbografx-16-slash-pc-engine-cd": "NEC PC Engine CD",
    "supergrafx": "NEC PC Engine SuperGrafx",
    "turbografx16--1": "NEC PC Engine",
    "pc-8000": "NEC PC-8000 - PC-8800 series",
    "pc-fx": "NEC PC-FX",
    "pc-9800-series": "NEC PC98",
    "nds": "NDS",
    "fds": "Nintendo FDS",
    "gba": "GBA",
    "gbc": "GBC",
    "gb": "GB",
    "n64": "N64",
    "nes": "FC",
    "famicom": "FC",
    "snes": "SFC",
    "sfam": "SFC",
    "pokemon-mini": "Nintendo Pokemon Mini",
    "virtualboy": "Nintendo Virtual Boy",
    "onscripter": "Onscripter",
    "openbor": "OPENBOR",
    "pico-8": "PICO8",
    "philips-cd-i": "Philips CDi",
    "quake": "Quake",
    "rpg-maker": "EASYRPG",
    "neogeoaes": "NEOGEO",
    "neogeomvs": "NEOGEO",
    "neo-geo-cd": "NEOGEO",
    "neo-geo-pocket": "NGP",
    "neo-geo-pocket-color": "NGP",
    "scummvm": "ScummVM",
    "sega-32x": "Sega 32X",
    "naomi": "Sega Atomiswave Naomi",
    "dc": "DC",
    "gamegear": "GG",
    "sega-master-system": "MS",
    "genesis-slash-megadrive": "MD",
    "sega-pico": "Sega Pico",
    "segacd": "Sega Mega CD - Sega CD",
    "sg1000": "Sega SG-1000",
    "saturn": "SS",
    "x1": "Sharp X1",
    "sharp-x68000": "Sharp X68000",
    "sinclair-zx81": "Sinclair ZX 81",
    "zxs": "Sinclair ZX Spectrum",
    "ps": "PS",
    "psp": "PSP",
    "tic-80": "TIC-80",
    "ti-83": "Texas Instruments TI-83",
    "3do": "The 3DO Company - 3DO",
    "uzebox": "Uzebox",
    "vemulator": "VeMUlator",
    "vircon-32": "Vircon32",
    "wasm-4": "WASM-4",
    "watara-slash-quickshot-supervision": "Watara Supervision",
    "wolfenstein-3d": "Wolfenstein 3D",
}

# Manual mapping of RomM slugs for TrimUI default platforms
TRIMUI_STOCK_SUPPORTED_PLATFORMS = frozenset(TRIMUI_STOCK_SUPPORTED_PLATFORMS_FS_MAP.keys())
TRIMUI_STOCK_SUPPORTED_PLATFORMS_FS = frozenset(
    TRIMUI_STOCK_SUPPORTED_PLATFORMS_FS_MAP.values()
)

_env_maps = None
_env_platforms = None


def _load_env_maps() -> dict[str, str]:
    raw = os.getenv("CUSTOM_MAPS")
    if not raw:
        return {}
    try:
        loaded = json.loads(raw)
        return loaded
    except json.JSONDecodeError as e:
        print(f"Error: CUSTOM_MAPS is an invalid JSON format: {e}")
        return {}
    except Exception as e:
        print(f"Error: Unexpected error: {e}")
        return {}


def init_env_maps():
    global _env_maps
    global _env_platforms
    if _env_maps is None:
        _env_maps = _load_env_maps()
    if _env_platforms is None:
        _env_platforms = frozenset(_env_maps.keys())
