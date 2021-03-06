from . import bbModule
from ....bbConfig import bbData
from .... import bbUtil
from typing import List

class bbScannerModule(bbModule.bbModule):
    """A module providing a ship with the ability to scan in-range objects, such as asteroids and ships

    :var timeToLock: The number of seconds this scanner takes to lock onto an object and obtain information
    :vartype timeToLock: float
    :var showClassAAsteroids: Whether or not this scanner will display nearby A-class asteroids on the ship's heads up display
    :vartype showClassAAsteroids: bool
    :var showCargo: Whether or not this scanner will display the contents of scanned ships' cargo holds
    :vartype showCargo: bool
    """

    def __init__(self, name : str, aliases : List[str], timeToLock=0, showClassAAsteroids=False, showCargo=False, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        """
        :param str name: The name of the module. Must be unique.
        :param list[str] aliases: Alternative names by which this module may be referred to
        :param float timeToLock: The number of seconds this scanner takes to lock onto an object and obtain information (Default 0)
        :param bool showClassAAsteroids: Whether or not this scanner will display nearby A-class asteroids on the ship's heads up display (Default False)
        :param bool showCargo: Whether or not this scanner will display the contents of scanned ships' cargo holds (Default False)
        :param int value: The number of credits this module may be sold or bought or at a shop (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this module. (Default "")
        :param str manufacturer: The name of the manufacturer of this module (Default "")
        :param str icon: A URL pointing to an image to use for this module's icon (Default "")
        :param bbUtil.dumbEmoji emoji: The emoji to use for this module's small icon (Default bbUtil.EMPTY_DUMBEMOJI)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other modules of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard module (loaded in from bbData) or a custom spawned module (Default False)
        """
        super(bbScannerModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.timeToLock = timeToLock
        self.showClassAAsteroids = showClassAAsteroids
        self.showCargo = showCargo


    def statsStringShort(self):
        return "*Time To Lock: " + str(self.timeToLock) + "s, Show Class A Asteroids: " + ("Yes" if self.showClassAAsteroids else "No") + ", Show Cargo: " + ("Yes" if self.showCargo else "No") + "*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the object's __class__ attribute.

        :return: A reference to this class
        :rtype: type
        """
        return bbScannerModule

    
    def toDict(self) -> dict:
        """Serialize this module into dictionary format, to be saved to file.
        Uses the base bbModule toDict method as a starting point, and adds extra attributes implemented by this specific module.

        :return: A dictionary containing all information needed to reconstruct this module
        :rtype: dict
        """
        itemDict = super(bbScannerModule, self).toDict()
        if not self.builtIn:
            itemDict["timeToLock"] = self.timeToLock
            itemDict["showClassAAsteroids"] = self.showClassAAsteroids
            itemDict["showCargo"] = self.showCargo
        return itemDict


def fromDict(moduleDict : dict) -> bbScannerModule:
    """Factory function building a new module object from the information in the provided dictionary. The opposite of this class's toDict function.

    :param moduleDict: A dictionary containing all information needed to construct the requested module
    :return: The new module object as described in moduleDict
    :rtype: dict
    """
    return bbScannerModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], timeToLock=moduleDict["timeToLock"] if "timeToLock" in moduleDict else 0,
                            showClassAAsteroids=moduleDict["showClassAAsteroids"] if "showClassAAsteroids" in moduleDict else False, showCargo=moduleDict["showCargo"] if "showCargo" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=bbUtil.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else bbUtil.EMPTY_DUMBEMOJI, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
