"""Constants for the wukongtv integration."""

DOMAIN = "wukongtv"

WUKONGTV_DEV = DOMAIN

######### CONF KEY
CONF_NAME = "name"
CONF_HOST = "host"
CONF_MODE = "mode"

COORDINATOR = "coordinator"
CONF_UPDATE_INTERVAL = "update_interval_seconds"

UNDO_UPDATE_LISTENER = "undo_update_listener"

CONF_BUTTONS = "buttons"
CONF_SWITCHS = "switchs"
CONF_MEDIAPLAY = "mediaplay"
CONF_STATE_DETECTION_RULES = "state_detection_rules"

CONF_TURN_OFF_COMMAND = "turn_off_command"
CONF_TURN_ON_COMMAND = "turn_on_command"

DEFAULT_WUKONG_SERVER_PORT = 5037
DEFAULT_DEVICE_CLASS = "auto"
DEFAULT_EXCLUDE_UNNAMED_APPS = False
DEFAULT_GET_SOURCES = True
DEFAULT_PORT = 5555
DEFAULT_SCREENCAP = True

DEVICE_WUKONGTV = "wukongtv"
DEVICE_CLASSES = [DEFAULT_DEVICE_CLASS, DEVICE_WUKONGTV]

PROP_ETHMAC = "ethmac"
PROP_SERIALNO = "serialno"
PROP_WIFIMAC = "wifimac"

SIGNAL_CONFIG_ENTITY = "wukongtv_config"


BUTTON_TYPES = {
    "tv_connect": {
        "name": "连接",
        "device_class": "restart",
        "icon": "mdi:lan-connect",
        "package": "AAC4EwEzAp4AAAgmAAABNAAAAAAAAABEeyJuYW1lIjoiSG9tZSBBc3Npc3RhbnQiLCJjaGFubmVsIjoiaUFwcFN0b3JlIiwiZGV2IjoiaU9TIn0=",
        "code": ""
    },
    "tv_up": {
        "name": "上",
        "device_class": "restart",
        "icon": "mdi:arrow-up-bold-circle",
        "package": "AAC4EwEzAp4AAAghAAAAEwAAAAAAAAAA",
        "code": 19
    },
    "tv_down": {
        "name": "下",
        "device_class": "restart",
        "icon": "mdi:arrow-down-bold-circle",
        "package": "AAC4EwEzAp4AAAghAAAAFAAAAAAAAAAA",
        "code": 20
    },
    "tv_left": {
        "name": "左",
        "device_class": "restart",
        "icon": "mdi:arrow-left-bold-circle",
        "package": "AAC4EwEzAp4AAAghAAAAFQAAAAAAAAAA",
        "code": 21
    },
    "tv_right": {
        "name": "右",
        "device_class": "restart",
        "icon": "mdi:arrow-right-bold-circle",
        "package": "AAC4EwEzAp4AAAghAAAAFgAAAAAAAAAA",
        "code": 22
    },
    "tv_home": {
        "name": "首页",
        "device_class": "restart",
        "icon": "mdi:home",
        "package": "AAC4EwEzAp4AAAghAAAAAwAAAAAAAAAA",
        "code": 3
    },
    "tv_ok": {
        "name": "确认",
        "device_class": "restart",
        "icon": "mdi:adjust",
        "package": "AAC4EwEzAp4AAAghAAAAFwAAAAAAAAAA",
        "code": 23
    },
    "tv_back": {
        "name": "返回",
        "device_class": "restart",
        "icon": "mdi:backup-restore",
        "package": "AAC4EwEzAp4AAAghAAAABAAAAAAAAAAA",
        "code": 4
    },
    "tv_volup": {
        "name": "音量加",
        "device_class": "restart",
        "icon": "mdi:volume-high",
        "package": "AAC4EwEzAp4AAAghAAAAGAAAAAAAAAAA",
        "code": 24
    },
    "tv_voldown": {
        "name": "音量减",
        "device_class": "restart",
        "icon": "mdi:volume-medium",
        "package": "AAC4EwEzAp4AAAghAAAAGQAAAAAAAAAA",
        "code": 25
    },
    "tv_power": {
        "name": "电源",
        "device_class": "restart",
        "icon": "mdi:power",
        "package": "AAC4EwEzAp4AAAghAAAAGgAAAAAAAAAA",
        "code": 26
    },
    "tv_menu": {
        "name": "菜单",
        "device_class": "restart",
        "icon": "mdi:menu",
        "package": "AAC4EwEzAp4AAAghAAAAUgAAAAAAAAAA",
        "code": 82
    },
    "tv_1": {
        "name": "1",
        "device_class": "restart",
        "icon": "mdi:numeric-1-box",
        "package": "AAC4EwEzAp4AAAghAAAACAAAAAAAAAAA",
        "code": 8
    },
    "tv_2": {
        "name": "2",
        "device_class": "restart",
        "icon": "mdi:numeric-2-box",
        "package": "AAC4EwEzAp4AAAghAAAACQAAAAAAAAAA",
        "code": 9
    },
    "tv_3": {
        "name": "3",
        "device_class": "restart",
        "icon": "mdi:numeric-3-box",
        "package": "AAC4EwEzAp4AAAghAAAACgAAAAAAAAAA",
        "code": 10
    },
    "tv_4": {
        "name": "4",
        "device_class": "restart",
        "icon": "mdi:numeric-4-box",
        "package": "AAC4EwEzAp4AAAghAAAACwAAAAAAAAAA",
        "code": 11
    },
    "tv_5": {
        "name": "5",
        "device_class": "restart",
        "icon": "mdi:numeric-5-box",
        "package": "AAC4EwEzAp4AAAghAAAADAAAAAAAAAAA",
        "code": 12
    },
    "tv_6": {
        "name": "6",
        "device_class": "restart",
        "icon": "mdi:numeric-6-box",
        "package": "AAC4EwEzAp4AAAghAAAADQAAAAAAAAAA",
        "code": 13
    },
    "tv_7": {
        "name": "7",
        "device_class": "restart",
        "icon": "mdi:numeric-7-box",
        "package": "AAC4EwEzAp4AAAghAAAADgAAAAAAAAAA",
        "code": 14
    },
    "tv_8": {
        "name": "8",
        "device_class": "restart",
        "icon": "mdi:numeric-8-box",
        "package": "AAC4EwEzAp4AAAghAAAADwAAAAAAAAAA",
        "code": 15
    },
    "tv_9": {
        "name": "9",
        "device_class": "restart",
        "icon": "mdi:numeric-9-box",
        "package": "AAC4EwEzAp4AAAghAAAAEAAAAAAAAAAA",
        "code": 16
    },
    "tv_0": {
        "name": "0",
        "device_class": "restart",
        "icon": "mdi:numeric-0-box",
        "package": "AAC4EwEzAp4AAAghAAAABwAAAAAAAAAA",
        "code": 7
    },
    "tv_clean": {
        "name": "清理",
        "device_class": "restart",
        "icon": "mdi:notification-clear-all",
        "package": "AAC4EwEzAp4AAAghAAAABwAAAAAAAAAA",
        "code": 999
    },
    "tv_clean_cache": {
        "name": "清理加速",
        "device_class": "restart",
        "icon": "mdi:notification-clear-all",
        "package": "",
        "code": 0,
        "action": "clean_cache"
    },
    "tv_opensetting": {
        "name": "设置",
        "device_class": "restart",
        "icon": "mdi:apps",
        "package": "",
        "code": 0,
        "action": "opensetting"
    },
    "tv_childlock": {
        "name": "锁屏",
        "device_class": "restart",
        "icon": "mdi:play-box-lock-outline",
        "package": "",
        "code": 0,
        "action": "childlock"
    },
    "tv_install_dangbeimarket": {
        "name": "安装当贝市场",
        "device_class": "restart",
        "icon": "mdi:open-in-app",
        "package": "",
        "code": 0,
        "action": "install",
        "appurl": "http://yaokong.wukongtv.com/appstore/yaokong.php?p=com.dangbeimarket&source=wukong" #网址必须是yaokong.wukongtv.com下才能安装，否则提示非法网址。
    },
}

