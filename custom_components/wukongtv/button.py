"""
Demo platform that has two fake switches.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
from homeassistant.components.button import ButtonEntity
from homeassistant.const import DEVICE_DEFAULT_NAME

from homeassistant.components.button import PLATFORM_SCHEMA
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.const import CONF_HOST
import voluptuous as vol

import time
import logging
import requests
import socket,base64

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
)

from .const import (
    DOMAIN, 
    CONF_BUTTONS, 
    CONF_MODE, 
    CONF_UPDATE_INTERVAL,
    COORDINATOR,
    BUTTON_TYPES,
    )
    
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add Switchentities from a config_entry."""      
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    host = config_entry.data[CONF_HOST]
    name = config_entry.data[CONF_NAME]
    mode = config_entry.data[CONF_MODE]
    state = False
    assumed = True
    
    buttons = []    
    
    for button in BUTTON_TYPES:
        buttons.append(WuKongButton(hass, button, coordinator, host, name, state, assumed, mode))
        _LOGGER.debug(button)
        
    async_add_entities(buttons, False)
    
class WuKongButton(ButtonEntity):
    """Representation of a demo switch."""
    _attr_has_entity_name = True

    def __init__(self, hass, kind, coordinator, host, name, state, assumed, mode):
        """Initialize the WuKongButton switch."""
        self.kind = kind
        self._state = state
        self._assumed = assumed
        self._attr_device_info = {
            "identifiers": {(DOMAIN, host)},
            "name": name,
            "manufacturer": "wukongtv",
            "model": "WuKong TV",
            "sw_version": "",
        }
        self._attr_device_class = BUTTON_TYPES[self.kind]['device_class']
        self._attr_entity_registry_enabled_default = True
        
        self._hass = hass
        self._host = host

        self._mode = mode
        self._icon = BUTTON_TYPES[self.kind]['icon']
        self._code = BUTTON_TYPES[self.kind]['code']
        self._package = BUTTON_TYPES[self.kind]['package']
        self._name = f"{BUTTON_TYPES[self.kind]['name']}"
        self._unique_id = f"wukong_button_{name}_{self.kind}"
        
        self._appid = BUTTON_TYPES[self.kind].get('appid')
        self._appurl = BUTTON_TYPES[self.kind].get('appurl')

    @property
    def should_poll(self):

        return False

    @property
    def name(self):
        """Return the name."""
        return self._name
        
    @property
    def unique_id(self):
        return self._unique_id

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def assumed_state(self):
        """Return if the state is based on assumptions."""
        return self._assumed

    @property
    def state(self):
        """Return true if switch is on."""
        return self._state

    def press(self, **kwargs):
        """Press the button."""
        self._state = self.sendCode()
        self.schedule_update_ha_state()


    def sendCode(self):
        s = WuKongService(self._hass, self._host, self._mode)
        if self._appid:
            return s.SendOpenCommand(None,self._appid)
        if self._appurl:
            return s.SendInstallCommand(None,self._appurl)
        if self._code == 999:
            return s.SendCleanCommand(None)
        if self._mode == 'UDP':
            _LOGGER.debug(self._package)
            return s.sendUDPPackage(self._package)
        else:
            _LOGGER.debug(self._code)
            return s.SendControlCommand(None,self._code)

class WuKongService(object):

    def __init__(self, hass, host, mode):
        self._host = host
        self._hass = hass
        self._mode = mode

    def SendControlCommand(self,call,selfcode=None):

        if self._mode == 'UDP':
            code = call.data.get('code')
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
        if selfcode == None:
            code = call.data.get('code')
            if code == None:
                _LOGGER.error('Command Code is nil!')
                return
        else:
            code = selfcode
        url = 'http://{host}:8899/send?key={code}'.format(host=self._host, code=code)
        _LOGGER.debug(url)
        return self.sendHttpRequest(url)

    def SendOpenCommand(self,call,selfappid=None):
        appid = ''
        if selfappid == None:
            appid = call.data.get('appid')
            if appid == None:
                _LOGGER.error('Appid is nil!')
                return
        else:
            appid = selfappid
        url = 'http://{host}:12104/?action=open&pkg={appid}'.format(host=self._host, appid=appid)
        _LOGGER.debug(url)
        return self.sendHttpRequest(url)

    def SendInstallCommand(self,call,selfappUrl=None):
        appUrl = ''
        if selfappUrl ==None:
            appUrl = call.data.get('appUrl')
            if appUrl == None:
                _LOGGER.error('appUrl is nil!')
                return
        else:
            appUrl = selfappUrl
        url = 'http://{host}:12104/?action=install&url={appUrl}'.format(host=self._host,appUrl=appUrl)
        _LOGGER.debug('url:%s' % url)
        return self.sendHttpRequest(url)

    def SendCleanCommand(self,call):
        url = 'http://{host}:12104/?action=clean'.format(host=self._host)
        _LOGGER.debug('url:%s' % url)
        return self.sendHttpRequest(url)

    def SendConnectCommand(self,call):
        host = call.data.get('host',self._host)
        if host == None:
            host = self._host
            if host == None:
                _LOGGER.error('host is nil!')
                return
        package=BUTTON_TYPES["tv_connect"]["package"]
        _LOGGER.debug('package:%s' % package)
        self.sendUDPPackage(package,host)

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
        try:
            resp = requests.get(url)
            if resp.status_code and resp.text == 'success':
                return False
            return True
        except Exception as e:
            _LOGGER.error("requst url:{url} Error:{err}".format(url=url,err=e))
            return False

    def sendUDPPackage(self,base64Data,host=None):
        addr = None
        if host != None:
            addr = (host, 12305)
        else:
            addr = (self._host, 12305)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytePackge = base64.b64decode(base64Data)
        ret = True
        try:
            s.sendto(bytePackge,addr)
            ret = False
        except Exception as e:
            _LOGGER.error("requst UDP Error:{err}, Package:{pkg}".format(err=e,pkg=base64Data))
            s.close()

        return ret
        
    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update Bjtoon health code entity."""
        #await self._coordinator.async_request_refresh()  