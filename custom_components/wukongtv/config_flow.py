"""Config flow for wukongtv ac integration."""

from __future__ import annotations

import logging
import requests
import binascii
import socket
import base64
import re
import sys
import time
import asyncio
import voluptuous as vol
from hashlib import md5

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode
from collections import OrderedDict

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
)

from .const import (
    DOMAIN, 
    CONF_SWITCHS, 
    CONF_MODE, 
    CONF_UPDATE_INTERVAL, 
    CONF_TURN_ON_COMMAND,
    CONF_TURN_OFF_COMMAND,
    )
from configparser import ConfigParser
try: import simplejson
except ImportError: import json as simplejson

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """handle config flow for this integration"""
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)
        
        
    def __init__(self):
        """Initialize."""
        self._errors = {}
    
    def sendHttpRequest(self,url):
        url +'&t={time}'.format(time=int(time.time()))
        try:            
            resp = requests.get(url,timeout=30)
            _LOGGER.debug(url)
            _LOGGER.debug("resp.status_code")
            _LOGGER.debug(resp.status_code)
            if resp.status_code==200:
                return True
            else:
                return False
        except Exception as e:
            _LOGGER.error("requst url:{url} Error:{err}".format(url=url,err=e))
            return False

    async def async_step_user(self, user_input={}):
        self._errors = {}
        if user_input is not None:
            config_data = {}
            host = user_input[CONF_HOST]
            name = user_input[CONF_NAME]
            mode = user_input[CONF_MODE]
          
            
            self._host = host
            self._name = name
            self._mode = mode

            response = await self.hass.async_add_executor_job(
                self.sendHttpRequest, 'http://{host}:12104/?action=screencap'.format(host=host)
            )
            _LOGGER.debug("response")
            _LOGGER.debug(response)

            if response == False:
                self._errors["base"] = "unkown"
                return await self._show_config_form(user_input)

            _LOGGER.debug(
                "wukongtv successfully, save data for wukongtv: %s",
                host,
            )
            await self.async_set_unique_id(f"climate.wukongtv-{self._host}")
            self._abort_if_unique_id_configured()

            config_data[CONF_HOST] = host
            config_data[CONF_NAME] = name
            config_data[CONF_MODE] = mode

            return self.async_create_entry(title=f"wukongtv-{host}", data=config_data)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):

        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default = "")] = str
        data_schema[vol.Required(CONF_HOST, default = "192.168.8.8")] = str        
        data_schema[vol.Required(CONF_MODE, default = "UDP")] = str
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )


class OptionsFlow(config_entries.OptionsFlow):
    """Config flow options for autoamap."""

    def __init__(self, config_entry):
        """Initialize autoamap options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, 10),
                    ): vol.All(vol.Coerce(int), vol.Range(min=3, max=30)),
                    vol.Optional(
                        CONF_TURN_ON_COMMAND,
                        default=self.config_entry.options.get(CONF_TURN_ON_COMMAND, self.config_entry.data.get(CONF_TURN_ON_COMMAND, "None"))
                    ): vol.All(vol.Coerce(str)),
                    vol.Optional(
                        CONF_TURN_OFF_COMMAND,
                        default=self.config_entry.options.get(CONF_TURN_OFF_COMMAND, self.config_entry.data.get(CONF_TURN_OFF_COMMAND, "None"))
                    ): vol.All(vol.Coerce(str)),
                }
            ),
        )
