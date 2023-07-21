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
from urllib.parse import quote
import voluptuous as vol
import json
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

TIMEOUT_SECONDS=5

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
        self._coordinator = coordinator
        self.kind = kind
        self._state = state
        self._assumed = assumed
        self._attr_device_info = {
            "identifiers": {(DOMAIN, host)},
            "name": name,
            "manufacturer": coordinator.data["brand"],
            "model": self._coordinator.data["model"],
            "sw_version": self._coordinator.data["sw_version"],
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
        
        self._action = BUTTON_TYPES[self.kind].get('action')
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
        if self._action:
            return s.SendActionCommand(self._action, self._appid, self._appurl)
        if self._code == 999:
            return s.SendCleanCommand()
        if self._mode == 'UDP':
            _LOGGER.debug(self._package)
            return s.sendUDPPackage(self._package)
        else:
            _LOGGER.debug(self._code)
            return s.SendControlCommand(self._code)

class WuKongService(object):

    def __init__(self, hass, host, mode):
        self._host = host
        self._hass = hass
        self._mode = mode

    def SendControlCommand(self,selfcode=None):

        if self._mode == 'UDP':
            code = selfcode
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
            _LOGGER.error('Command Code is nil!')
            return
        else:
            code = selfcode
        url = 'http://{host}:8899/send?key={code}'.format(host=self._host, code=code)
        _LOGGER.debug(url)
        return self.sendHttpRequest(url)

    def SendActionCommand(self, selfaction, selfappid=None, selfappurl=None):
        if selfaction == None:
            _LOGGER.error('Action is nil!')
            return
        if selfaction == "open":
            url = 'http://{host}:12104/?action={action}&pkg={appid}'.format(host=self._host, action=selfaction, appid=selfappid)
        elif selfaction == "install":
            url = 'http://{host}:12104/?action={action}&url={url}'.format(host=self._host, action=selfaction, url=quote(selfappurl))
        elif selfaction == "childlock":
            url = 'http://{host}:12104/?action={action}&timer=0'.format(host=self._host, action=selfaction)
        else:
            url = 'http://{host}:12104/?action={action}'.format(host=self._host, action=selfaction)
        _LOGGER.debug(url)
        return self.sendHttpRequest(url)
    

    def SendCleanCommand(self):
        url = 'http://{host}:12104/?action=clean'.format(host=self._host)
        _LOGGER.debug('url:%s' % url)
        return self.sendHttpRequest(url)

    def SendConnectCommand(self):
        if self._host == None:
            _LOGGER.error('host is nil!')
            return
        package=BUTTON_TYPES["tv_connect"]["package"]
        _LOGGER.debug('package:%s' % package)
        self.sendUDPPackage(package,self._host)
        
    def sendHttpRequest(self,url):
        url +'&t={time}'.format(time=int(time.time()))
        try:
            resp = requests.get(url,timeout=TIMEOUT_SECONDS)
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
        """Update entity."""
        #await self._coordinator.async_request_refresh()  