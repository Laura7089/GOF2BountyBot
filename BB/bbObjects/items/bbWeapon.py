from .bbItem import bbItem
from ...bbConfig import bbData
from ... import bbUtil
from typing import List

class bbWeapon(bbItem):
    """A primary weapon that can be equipped onto a bbShip for use in duels.

    :var dps: The weapon's damage per second to a target ship.
    :vartype dps: float
    """

    def __init__(self, name : str, aliases : List[str], dps=0.0, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        """
        :param str name: The name of the weapon. Must be unique. (a model number is a good starting point)
        :param list[str] aliases: A list of alternative names this weapon may be referred to by.
        :param int valie: The amount of credits that this turret can be bought/sold for at a shop. (Default 0)
        :param float dps:The weapon's damage per second to a target ship. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this weapon. (Default "")
        :param str manufacturer: The name of the manufacturer of this weapon (Default "")
        :param str icon: A URL pointing to an image to use for this weapon's icon (Default "")
        :param bbUtil.dumbEmoji emoji: The emoji to use for this weapon's small icon (Default bbUtil.EMPTY_DUMBEMOJI)
        :param int techLevel: A rating from 1 to 10 of this weapon's technical advancement. Used as a measure for its effectiveness compared to other weapons of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard weapon (loaded in from bbData) or a custom spawned weapon (Default False)
        """
        super(bbWeapon, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.dps = dps

    
    def statsStringShort(self) -> str:
        """Get a short string summary of the weapon. This currently only includes the DPS.

        :return: a short string summary of the weapon's statistics
        :rtype: str
        """
        return "*Dps: " + str(self.dps) + "*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbWeapon class
        :rtype: type
        """
        return bbWeapon


    def toDict(self) -> dict:
        """Serialize this item into dictionary format, for saving to file.

        :return: A dictionary containing all information needed to reconstruct this weapon. If the weapon is builtIn, this is only its name.
        :rtype: dict
        """
        itemDict = super(bbWeapon, self).toDict()
        if not self.builtIn:
            itemDict["dps"] = self.dps
        return itemDict


def fromDict(weaponDict):
    """Factory function constructing a new bbWeapon object from a dictionary serialised representation - the opposite of bbWeapon.toDict.
    
    :param dict weaponDict: A dictionary containing all information needed to construct the desired bbWeapon
    :return: A new bbWeapon object as described in weaponDict
    :rtype: bbWeapon
    """
    if weaponDict["builtIn"]:
        return bbData.builtInWeaponObjs[weaponDict["name"]]
    else:
        return bbWeapon(weaponDict["name"], weaponDict["aliases"], dps=weaponDict["dps"], value=weaponDict["value"],
        wiki=weaponDict["wiki"] if "wiki" in weaponDict else "", manufacturer=weaponDict["manufacturer"] if "manufacturer" in weaponDict else "",
        icon=weaponDict["icon"] if "icon" in weaponDict else bbData.rocketIcon, emoji=bbUtil.dumbEmojiFromStr(weaponDict["emoji"]) if "emoji" in weaponDict else bbUtil.EMPTY_DUMBEMOJI,
        techLevel=weaponDict["techLevel"] if "techLevel" in weaponDict else -1, builtIn=False)
