import logging
import aiohttp
import async_timeout
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "league_of_legends"
CONF_REGION = "region"

# Zeit zwischen Updates (Standard: 15 Minuten um API Limits zu schonen)
SCAN_INTERVAL = timedelta(minutes=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_REGION): cv.string,
    vol.Required(CONF_NAME): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the League of Legends sensor."""
    api_key = config[CONF_API_KEY]
    region = config[CONF_REGION]
    full_name = config[CONF_NAME]
    
    session = async_get_clientsession(hass)
    
    # Split Name#Tag
    if "#" in full_name:
        game_name, tag_line = full_name.split("#")
    else:
        _LOGGER.error("Format Error: Name must be in format Name#Tag (e.g. TomTorjäger#007)")
        return

    sensor = LeagueSensor(session, api_key, region, game_name, tag_line)
    async_add_entities([sensor], update_before_add=True)

class LeagueSensor(SensorEntity):
    """Representation of a League of Legends Sensor."""

    def __init__(self, session, api_key, region, game_name, tag_line):
        self._session = session
        self._api_key = api_key
        self._region = region
        self._game_name = game_name
        self._tag_line = tag_line
        self._puuid = None
        self._dd_version = "14.1.1" # Standard, wird geupdated
        self._summoner_id = None
        self._attr_name = f"LoL {game_name}"
        self._attr_unique_id = f"lol_{game_name}_{tag_line}".lower()
        self._attr_icon = "mdi:controller-classic"
        self._state = None
        self._attributes = {}
        self._available = False

    @property
    def native_value(self):
        """Return the state of the sensor (Rank or Level)."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def available(self):
        return self._available

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            headers = {"X-Riot-Token": self._api_key}
            
            # 1. Get PUUID (Account-V1) - Nur einmalig nötig
            if not self._puuid:
                # Hole aktuelle Version für Icons (Data Dragon)
                try:
                    async with self._session.get("https://ddragon.leagueoflegends.com/api/versions.json") as resp_ver:
                        if resp_ver.status == 200:
                            versions = await resp_ver.json()
                            self._dd_version = versions[0]
                except Exception:
                    self._dd_version = "14.1.1" # Fallback

                url_account = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self._game_name}/{self._tag_line}"
                async with async_timeout.timeout(10):
                    async with self._session.get(url_account, headers=headers) as resp:
                        if resp.status != 200:
                            _LOGGER.error("Error fetching Account: %s", resp.status)
                            return
                        data = await resp.json()
                        self._puuid = data.get("puuid")

            # 2. Get Summoner Info (Summoner-V4)
            # ACHTUNG: Hier muss die korrekte Plattform-URL genutzt werden (euw1, eun1, etc.)
            platform_url = f"https://{self._region}.api.riotgames.com"
            
            url_summoner = f"{platform_url}/lol/summoner/v4/summoners/by-puuid/{self._puuid}"
            async with async_timeout.timeout(10):
                async with self._session.get(url_summoner, headers=headers) as resp:
                    if resp.status != 200:
                        _LOGGER.error("Error fetching Summoner: %s", resp.status)
                        return
                    summoner_data = await resp.json()
                    self._summoner_id = summoner_data.get("id")
                    level = summoner_data.get("summonerLevel")
                    profile_icon_id = summoner_data.get("profileIconId")

            # 3. Get Ranked Info (League-V4)
            url_league = f"{platform_url}/lol/league/v4/entries/by-summoner/{self._summoner_id}"
            async with async_timeout.timeout(10):
                async with self._session.get(url_league, headers=headers) as resp:
                    if resp.status != 200:
                        _LOGGER.error("Error fetching Rank: %s", resp.status)
                        return
                    league_data = await resp.json()

            # Daten verarbeiten
            self._attributes["level"] = level
            self._attributes["profile_icon_id"] = profile_icon_id
            
            # Suche Solo/Duo Rank
            solo_q = next((item for item in league_data if item["queueType"] == "RANKED_SOLO_5x5"), None)
            
            if solo_q:
                tier = solo_q.get("tier")
                rank = solo_q.get("rank")
                lp = solo_q.get("leaguePoints")
                wins = solo_q.get("wins")
                losses = solo_q.get("losses")
                winrate = round((wins / (wins + losses)) * 100, 1)
                
                self._state = f"{tier} {rank}" # Hauptstatus: z.B. GOLD IV
                self._attributes["lp"] = lp
                self._attributes["wins"] = wins
                self._attributes["losses"] = losses
                self._attributes["winrate"] = f"{winrate}%"
            else:
                self._state = "Unranked"

            # Icon setzen (Optional: Man könnte hier dynamisch Bilder laden)
            self._attr_entity_picture = f"https://ddragon.leagueoflegends.com/cdn/{self._dd_version}/img/profileicon/{profile_icon_id}.png"
            
            self._available = True

        except Exception as e:
            _LOGGER.error("Error updating League Sensor: %s", e)
            self._available = False
