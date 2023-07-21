"""Support for functionality to interact with wukongtv devices."""
from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from datetime import datetime
import functools
import logging
import time
import os
import requests
import socket,base64
from typing import Any, Concatenate, ParamSpec, TypeVar
from urllib.parse import quote
import json
import voluptuous as vol
from homeassistant.components import media_source
import homeassistant.util.dt as dt_util

from homeassistant.components import persistent_notification
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.components.media_player.browse_media import (
    async_process_play_media_url,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_COMMAND,
    ATTR_CONNECTIONS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_SW_VERSION,
    CONF_HOST,
    CONF_NAME,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator


from .const import (
    DOMAIN, 
    CONF_MODE, 
    CONF_UPDATE_INTERVAL,
    COORDINATOR,
    BUTTON_TYPES,
)

_LOGGER = logging.getLogger(__name__)

ATTR_WUKONG_RESPONSE = "wukong_response"
ATTR_DEVICE_PATH = "device_path"
ATTR_HDMI_INPUT = "hdmi_input"
ATTR_LOCAL_PATH = "local_path"

SERVICE_CONTROL_COMMAND = "control_command"
SERVICE_OPEN_COMMAND = "open_command"
SERVICE_INSTALL_COMMAND = "Install_command"
SERVICE_CLEAN_COMMAND = "clean_command"
SERVICE_CONNECT_COMMAND = "connect_command"
SERVICE_QUEUE_COMMAND = "queue_command"

PREFIX_WuKongTV = "WuKong TV"


WuKongTV_STATES = {
    "off": MediaPlayerState.OFF,
    "idle": MediaPlayerState.IDLE,
    "standby": MediaPlayerState.STANDBY,
    "playing": MediaPlayerState.PLAYING,
    "paused": MediaPlayerState.PAUSED,
}

SUPPORT_WuKongTV = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.SEEK
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.CLEAR_PLAYLIST
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.BROWSE_MEDIA
)


import logging

_LOGGER = logging.getLogger(__name__)

SERVER_TYPE_AV = 0
SERVER_TYPE_CONTROL = 1
TIMEOUT_SECONDS=5

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the wukongtv Mediaplayer."""
    config = entry.data
    name = config[CONF_NAME]
    mode = config[CONF_MODE]
    host = config[CONF_HOST]
    unique_id = f"wukongtvmediaplay-{host}"
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    dev = WuKongTV(hass, coordinator, unique_id, name, host, mode)
    async_add_entities([dev])


    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        "send_open_command",
        {vol.Required("appid"): cv.string},
        "SendOpenCommand",
    )
    platform.async_register_entity_service(
        "send_install_command",
        {vol.Required("appurl"): cv.string},
        "SendInstallCommand",
    )
    platform.async_register_entity_service(
        "send_control_command",
        {vol.Required("code"): cv.string},
        "SendControlCommand",
    )
    platform.async_register_entity_service(
        "send_clean_command", {}, "SendCleanCommand",
    )
    platform.async_register_entity_service(
        "send_connect_command", {}, "SendConnectCommand",
    )


class WuKongTV(MediaPlayerEntity):
    """WuKongTV Device"""
    def __init__(self, hass, coordinator, unique_id, name, host, mode):
        """Initialize the WuKongTV Player."""
        self._hass = hass
        self._unique_id = unique_id
        self._coordinator = coordinator
        self._name = name
        self._host = host
        self._mode = mode
        self._volume = None
        self._muted = None
        self._state = None
        self._media_id = None
        self._mediatitle = None
        self._state = None
        self._source = None
        sw_version = ""
        self._attr_device_info = {
            "identifiers": {(DOMAIN, host)},
            "name": name,
            "manufacturer": coordinator.data["brand"],
            "model": self._coordinator.data["model"],
            "sw_version": self._coordinator.data["sw_version"],
        }
                   
    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
 
    async def async_update(self) -> None:
        """Retrieve the latest data."""
        await self._coordinator.async_request_refresh()
        respState = self._coordinator.data.get("available")
        if respState:
            self._state = WuKongTV_STATES["idle"]
            app_list = [d['label']+"|"+d['pkg'] for d in self._coordinator.data["apps"]]
            self._attr_source_list = app_list
            self._attr_source = self._source
        else:
            self._state = None 
            self._attr_source_list = None
        
    def _wukong_screencap(self) -> bytes | None:
        """Take a screen capture from the device."""
        return self._coordinator.data.get("screencap")
        
    async def async_get_media_image(self) -> tuple[bytes | None, str | None]:
        """Fetch current playing image."""
        if (
            not self._wukong_screencap
            or self.state in {MediaPlayerState.OFF, None}
            or not self.available
        ):
            return None, None

        media_data = self._wukong_screencap()
        if media_data:
            return media_data, "image/png"

        #If an exception occurred and the device is no longer available, write the state
        if not self.available:
            self.async_write_ha_state()

        return None, None

    @property
    def media_image_hash(self) -> str | None:
        """Hash value for media image."""
        return f"{datetime.now().timestamp()}" if self._wukong_screencap else None
        
    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        """Implement the websocket media browsing helper."""
        return await media_source.async_browse_media(
            self.hass,
            media_content_id,
            content_filter=lambda item: item.media_content_type.startswith(""),
        )

    async def async_play_media(self, media_type: str, media_id: str, **kwargs):
        didl_metadata: str | None = None
        title: str = ""
        """Play a piece of media."""
        if media_source.is_media_source_id(media_id):
            sourced_media = await media_source.async_resolve_media(self.hass, media_id, self.entity_id)
            media_type = sourced_media.mime_type
            media_id = sourced_media.url
            
            if sourced_metadata := getattr(sourced_media, "didl_metadata", None):
                didl_metadata = didl_lite.to_xml_string(sourced_metadata).decode(
                    "utf-8"
                )
                title = sourced_metadata.title

        # If media ID is a relative URL, we serve it from HA.
        media_id = async_process_play_media_url(self.hass, media_id)
        self._path = os.path.dirname(media_id)
        mediatitle = os.path.basename(media_id)
        url = 'http://{host}:12104/?action=pushscreen_new&what=274'.format(host=self._host)
        data = [{"filepath":mediatitle,"mimetype":media_type}]
        ret = await self._hass.async_add_executor_job(self.sendHttpPost,url,data)
        _LOGGER.debug(ret)
        #http://{ha}:12105/?action=pull_video&mimetype=video/mp4&videopath={mediatitle}
        _LOGGER.debug("source media_id： %s", media_id)
                     
        self._media_id = media_id

            
                 

    @property
    def name(self):
        """Return the name of the device."""
        return self._name
        
    @property    
    def unique_id(self):
        """Return a unique_id for this entity."""
        return "mediaplayer_" + self._unique_id
        
    @property
    def available(self):
        """Return True if entity is available."""
        return self._state != None

    @property
    def state(self):
        """Return the state of the device."""
        return self._state
        
    @property
    def device_class(self):
        """Return the state of the device."""
        return "tv"
        
    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        supported_features = 0

        #supported_features |= MediaPlayerEntityFeature.PLAY
        #supported_features |= MediaPlayerEntityFeature.STOP
        #supported_features |= MediaPlayerEntityFeature.VOLUME_SET
        supported_features |= MediaPlayerEntityFeature.VOLUME_STEP
        supported_features |= MediaPlayerEntityFeature.TURN_OFF
        supported_features |= MediaPlayerEntityFeature.SELECT_SOURCE
        
        if self._muted !=None:
            supported_features |= MediaPlayerEntityFeature.VOLUME_MUTE

        supported_features |= (
           MediaPlayerEntityFeature.PLAY_MEDIA
           | MediaPlayerEntityFeature.BROWSE_MEDIA
        )
     

        return supported_features
        
    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted
            
    @property
    def media_content_id(self):
        """Content ID of current playing media."""
        return self._media_id
                
    @property
    def media_title(self):
        """Title of current playing media."""
        return self._mediatitle
    
    async def async_turn_on(self) -> None:
        # """Turn on the device."""
        pass

    async def async_turn_off(self) -> None:
        """Turn off the device."""
        if self._mode == 'UDP':
            return self.sendUDPPackage(BUTTON_TYPES["tv_power"]['package'])
        else:
            return self.SendControlCommand(None,BUTTON_TYPES["tv_power"]['code'])
            

    async def async_select_source(self, source: str) -> None:
        """Select input source.

        If the source starts with a '!', then it will close the app instead of
        opening it.
        """
        if isinstance(source, str):
            source_ = source.split("|")[1].lstrip()
            await self._hass.async_add_executor_job(self.SendOpenCommand, source_)
            self._source = source

                
    def media_play(self):
        """Send play commmand."""
        pass

    def media_pause(self):
        """Send pause command."""
        pass
        
    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        pass
        
    async def async_volume_down(self) -> None:
        """Send volume down command."""
        if self._mode == 'UDP':
            return self.sendUDPPackage(BUTTON_TYPES["tv_voldown"]['package'])
        else:
            return self.SendControlCommand(None,BUTTON_TYPES["tv_voldown"]['code'])

    async def async_volume_up(self) -> None:
        """Send volume up command."""
        if self._mode == 'UDP':
            return self.sendUDPPackage(BUTTON_TYPES["tv_volup"]['package'])
        else:
            return self.SendControlCommand(None,BUTTON_TYPES["tv_volup"]['code'])
        
    async def async_mute_volume(self, mute: bool):
        """Send mute_volume command."""
        pass

    async def async_media_stop(self):
        """Send stop command."""
        pass

    def play_media(self, media_id: str, **kwargs):
        """Send play_media commmand."""
        # Replace this with calling your media player play media function.
        pass
        
        

    def SendControlCommand(self, code: str):

        if self._mode == 'UDP':            
            if code == None:
                _LOGGER.error('Command Code is nil!')
                return
            if code in BUTTON_TYPES.keys():
                package = BUTTON_TYPES[code]["package"]
                _LOGGER.debug(package)
                return self.sendUDPPackage(package)
            else:
                _LOGGER.error('Code Error!')
                return


        code = ''        
        if code == None:
            _LOGGER.error('Command Code is nil!')
            return
        url = 'http://{host}:8899/send?key={code}'.format(host=self._host, code=code)
        _LOGGER.debug(url)
        return self.sendHttpRequest(url)

    def SendOpenCommand(self, appid: str):
        if appid == None:
            _LOGGER.error('Appid is nil!')
            return
        url = 'http://{host}:12104/?action=open&pkg={appid}'.format(host=self._host, appid=appid)
        _LOGGER.debug(url)
        return self.sendHttpRequest(url)

    def SendInstallCommand(self, appUrl: str):
        if appUrl == None:
            _LOGGER.error('appUrl is nil!')
            return

        url = 'http://{host}:12104/?action=install&url={appUrl}'.format(host=self._host, appUrl=appUrl)
        _LOGGER.debug('url:%s' % url)
        return self.sendHttpRequest(url)

    def SendCleanCommand(self):
        url = 'http://{host}:12104/?action=clean'.format(host=self._host)
        _LOGGER.debug('url:%s' % url)
        return self.sendHttpRequest(url)

    def SendConnectCommand(self):
        package=BUTTON_TYPES["tv_connect"]["package"]
        _LOGGER.debug('package:%s' % package)
        self.sendUDPPackage(package)

    def SendCommandQueue(self,call):
        cmdQueue = call.data.get('cmdQueue')
        for cmd in cmdQueue:

            code = cmd.get('code')
            delay = cmd.get('delay')

            if code == None:
                return
            if delay == None:
                delay = 1000
            if self._mode == 'UDP':
                if code in PACKAGES.keys():
                    package = PACKAGES[code]
                    self.sendUDPPackage(package)
                    time.sleep(delay / 1000)
                else:

                    _LOGGER.error('Code Error! code:{cd}'.format(cd=code))
                    return
            else:
                self.SendControlCommand(None,code)
                time.sleep(delay / 1000)

    def sendHttpRequest(self,url):
        url +'&t={time}'.format(time=int(time.time()))
        headerstr = {"User-Agent": "wk/ykios"}
        try:
            resp = requests.get(url,headers=headerstr,timeout=TIMEOUT_SECONDS)
            if resp.status_code and resp.text == 'success':
                return True
            return False
        except Exception as e:
            _LOGGER.error("requst url:{url} Error:{err}".format(url=url,err=e))
            return False
            
    def sendHttpPost(self,url,data):
        url +'&t={time}'.format(time=int(time.time()))
        headerstr = {"User-Agent": "wk/ykios","Content-Type": "text/json;charset=utf-8"}
        headerstr2 = {"User-Agent": "remote/3.7.6 (iPhone; iOS 16.5.1; Scale/3.00)"}
        try:
            resp = requests.post(url, headers=headerstr, json = data,timeout=TIMEOUT_SECONDS)
            if resp.status_code and resp.text == 'success':
                return True
            return False
        except Exception as e:
            _LOGGER.error("requst url:{url} Error:{err}".format(url=url,err=e))
            return False

    def sendUDPPackage(self,base64Data):
        addr = (self._host, 12305)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytePackge = base64.b64decode(base64Data)
        ret = True
        _LOGGER.debug('package_base64Data:%s' % base64Data)
        try:
            s.sendto(bytePackge,addr)
            ret = False
        except Exception as e:
            _LOGGER.error("requst UDP Error:{err}, Package:{pkg}".format(err=e,pkg=base64Data))
            s.close()

        return ret
        
