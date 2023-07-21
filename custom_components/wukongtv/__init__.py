"""gree integration."""
from __future__ import annotations
from async_timeout import timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, Config
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import json
import requests
import binascii
import socket
import base64
import time
import datetime
import asyncio
import logging

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
)

from .const import (
    DOMAIN,
    CONF_MODE,
    CONF_UPDATE_INTERVAL,
    COORDINATOR,
    UNDO_UPDATE_LISTENER,
    CONF_STATE_DETECTION_RULES,
    WUKONGTV_DEV,
    DEFAULT_WUKONG_SERVER_PORT,
    DEVICE_WUKONGTV,
    PROP_ETHMAC,
    PROP_WIFIMAC,
    SIGNAL_CONFIG_ENTITY,
)
from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)

TIMEOUT_SECONDS=5

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.MEDIA_PLAYER]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured wukongtv."""
    hass.data.setdefault(DOMAIN, {})    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    mode = entry.data[CONF_MODE]
    update_interval_seconds = entry.options.get(CONF_UPDATE_INTERVAL, 10)

    coordinator = DataUpdateCoordinator(hass, host, name, mode, update_interval_seconds)
    
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = entry.add_update_listener(update_listener)

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
           
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
    

async def update_listener(hass, entry):
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)


class DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data."""

    def __init__(self, hass, host, name, mode, update_interval_seconds):
        """Initialize."""
        update_interval = datetime.timedelta(seconds=update_interval_seconds)

        _LOGGER.debug("Data will be update every %s", update_interval)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)
        self._name = name
        self._host = host
        self._mode = mode
        self._hass = hass
        self._data = {}
        self.times = 0
        

    def is_json(self, jsonstr):
        try:
            json.loads(jsonstr)
        except ValueError:
            return False
        return True
        
    def sendHttpRequest(self, url):
        url +'&t={time}'.format(time=int(time.time()))
        try:            
            resp = requests.get(url,timeout=TIMEOUT_SECONDS)
            _LOGGER.debug(url)
            json_text = resp.text
            if self.is_json(json_text):
                resdata = json.loads(json_text)
            else:
                resdata = resp
            return resdata
        except Exception as e:
            _LOGGER.error("requst url:{url} Error:{err}".format(url=url,err=e))
            return None

    def sendUDPPackage(self, base64Data):
        addr = None
        if self._host != None:
            addr = (self._host, 12305)
        else:
            return False
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _LOGGER.debug(s)
        bytePackge = base64.b64decode(base64Data)
        ret = False
        try:            
            s.sendto(bytePackge,addr)
            ret = True
        except Exception as e:
            _LOGGER.error("requst UDP Error:{err}, Package:{pkg}".format(err=e,pkg=base64Data))
            s.close()
        return ret
        
    async def GetDeviceInfo(self):
        _LOGGER.debug("getdeviceinfo http:"+self._host)
        ret = await self._hass.async_add_executor_job(self.sendHttpRequest,'http://{host}:12104/?action=device_property'.format(host=self._host))
        _LOGGER.debug(ret)
        self._data["deviceinfo"] = ret
        if ret:
            self._data["brand"] = ret.get("brand","WuKong TV")
            self._data["model"] = ret.get("deviceName","WuKong TV")
            self._data["sw_version"] = ret.get("osVersion", "")
        else:
            self._data["brand"] = "WuKong TV"
            self._data["model"] = "WuKong TV"
            self._data["sw_version"] = ""
        
        
    async def GetApps(self):
        _LOGGER.debug("getdeviceinfo http:"+self._host)
        ret = await self._hass.async_add_executor_job(self.sendHttpRequest,'http://{host}:12104/?action=list'.format(host=self._host))
        _LOGGER.debug(ret)
        self._data["apps"] = ret
       
        
    async def GetScreencap(self):
        _LOGGER.debug("getdeviceinfo http:"+self._host)
        ret = await self._hass.async_add_executor_job(self.sendHttpRequest,'http://{host}:12104/?action=screencap'.format(host=self._host))        

        if ret == None:
            if self.times>3:
                self._data["available"] = False
            else:
                self._data["available"] = True
            self.times += 1
            return
        if ret.status_code == 404:
            self._data["available"] = True
        if ret.status_code == 200:
            self._data["screencap"] = ret.content
            self._data["available"] = True
        self.times = 0

        

    async def _async_update_data(self):
        """Update data via DataFetcher."""
        
        
        
        if self._data.get("deviceinfo")==None:
            tasks = [            
                asyncio.create_task(self.GetDeviceInfo()),
            ]
            await asyncio.gather(*tasks)
        
        if self._data.get("apps")==None:
            tasks = [            
                asyncio.create_task(self.GetApps()),
            ]
            await asyncio.gather(*tasks)
            
        tasks = [            
            asyncio.create_task(self.GetScreencap()),
        ]
        await asyncio.gather(*tasks)
        return self._data
        