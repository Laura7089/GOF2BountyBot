# Typing imports
from __future__ import annotations
from typing import Union, List, TYPE_CHECKING
if TYPE_CHECKING:
    from .battles import DuelRequest

from .items import bbShip, bbModuleFactory, bbWeapon, bbTurret
from .items.modules import bbModule
from ..bbConfig import bbConfig
from . import bbInventory, bbInventoryListing
from ..userAlerts import UserAlerts
from datetime import datetime
from discord import Guild, Member
from . import bbGuild
from ..logging import bbLogger


# Dictionary-serialized bbShip to give to new players
defaultShipLoadoutDict = {"name": "Betty", "builtIn":True,
                        "weapons":[{"name": "Micro Gun MK I", "builtIn": True}],
                        "modules":[{"name": "Telta Quickscan", "builtIn": True}, {"name": "E2 Exoclad", "builtIn": True}, {"name": "IMT Extract 1.3", "builtIn": True}]}

# Default attributes to give to new players
defaultUserDict = {"credits":0, "bountyCooldownEnd":0, "lifetimeCredits":0, "systemsChecked":0, "bountyWins":0, "activeShip": defaultShipLoadoutDict, "inactiveWeapons":[{"item": {"name": "Nirai Impulse EX 1", "builtIn": True}, "count": 1}]}
# Reference value not pre-calculated from defaultUserDict. This is not used in the game's code, but provides a reference for game design.
defaultUserValue = 28970


class bbUser:
    """A user of the bot. There is currently no guarantee that user still shares any guilds with the bot, though this is planned to change in the future.

    :var id: The user's unique ID. The same as their unique discord ID.
    :vartype id: int
    :var credits: The amount of credits (currency) this user has
    :vartype credits: int
    :var lifetimeCredits: The total amount of credits this user has earned through hunting bounties (TODO: rename)
    :vartype lifetimeCredits: int
    :var bountyCooldownEnd: A utc timestamp representing when the user's cmd_check cooldown is due to expire
    :vartype bountyCooldownEnd: float
    :var systemsChecked: The total number of space systems this user has checked
    :vartype systemsChecked: int
    :var bountyWins: The total number of bounties this user has won
    :vartype bountyWins: int
    :var activeShip: The user's currently equipped bbShip
    :vartype activeShip: bbShip
    :var inactiveShips: The bbShips currently in this user's inventory (unequipped)
    :vartype inactiveShips: bbInventory
    :var inactiveModules: The bbModules currently in this user's inventory (unequipped)
    :vartype inactiveModules: bbInventory
    :var inactiveWeapons: The bbWeapons currently in this user's inventory (unequipped)
    :vartype inactiveWeapons: bbInventory
    :var inactiveTurrets: The bbTurrets currently in this user's inventory (unequipped)
    :vartype inactiveTurrets: bbInventory
    :var lastSeenGuildId: The ID of the guild where this user was last active. Not guaranteed to be present.
    :vartype lastSeenGuildId: int
    :var hasLastSeenGuildId: Whether or not the user currently has a lastSeenGuildId
    :vartype hasLastSeenGuildId: bool
    :var duelRequests: A dictionary mapping target bbUser objects to DuelRequest objects. Only contains duel requests issued by this user.
    :vartype duelRequests: dict[bbUser, DuelRequest]
    :var duelWins: The total number of duels the user has won
    :vartype duelWins: int
    :var duelLosses: The total number of duels the user has lost
    :vartype duelLosses: int
    :var duelCreditsWins: The total amount of credits the user has won through fighting duels
    :vartype duelCreditsWins: int
    :var duelCreditsLosses: The total amount of credits the user has lost through fighting duels
    :vartype duelCreditsLosses: int
    :var userAlerts: A dictionary mapping UserAlerts.UABase subtypes to instances of that subtype
    :vartype userAlerts: dict[type, UserAlerts.UABase]
    :var bountyWinsToday: The number of bounties the user has won today
    :vartype bountyWinsToday: int
    :var dailyBountyWinsReset: A datetime.datetime representing the time at which the user's bountyWinsToday should be reset to zero
    :vartype dailyBountyWinsReset: datetime.datetime
    :var pollOwned: Whether or not this user has a running ReactionPollMenu
    :vartype pollOwned: bool
    """

    def __init__(self, id : int, credits=0, lifetimeCredits=0, 
                    bountyCooldownEnd=-1, systemsChecked=0, bountyWins=0, activeShip=None,
                    inactiveShips=bbInventory.bbInventory(), inactiveModules=bbInventory.bbInventory(), inactiveWeapons=bbInventory.bbInventory(), inactiveTurrets=bbInventory.bbInventory(),
                    lastSeenGuildId=-1, duelWins=0, duelLosses=0, duelCreditsWins=0, duelCreditsLosses=0,
                    alerts={}, bountyWinsToday=0, dailyBountyWinsReset=datetime.utcnow(), pollOwned=False):
        """
        :param int id: The user's unique ID. The same as their unique discord ID.
        :param int credits: The amount of credits (currency) this user has (Default 0)
        :param int lifetimeCredits: The total amount of credits this user has earned through hunting bounties (TODO: rename) (Default 0)
        :param float bountyCooldownEnd: A utc timestamp representing when the user's cmd_check cooldown is due to expire (Default -1)
        :param int systemsChecked: The total number of space systems this user has checked (Default 0)
        :param int bountyWins: The total number of bounties this user has won (Default 0)
        :param bbShip activeShip: The user's currently equipped bbShip (Default None)
        :param bbInventory inactiveShips: The bbShips currently in this user's inventory (unequipped) (Default empty bbInventory)
        :param bbInventory inactiveModules: The bbModules currently in this user's inventory (unequipped) (Default empty bbInventory)
        :param bbInventory inactiveWeapons: The bbWeapons currently in this user's inventory (unequipped) (Default empty bbInventory)
        :param bbInventory inactiveTurrets: The bbTurrets currently in this user's inventory (unequipped) (Default empty bbInventory)
        :param int lastSeenGuildId: The ID of the guild where this user was last active. Not guaranteed to be present. (Default -1)
        :param int duelWins: The total number of duels the user has won (Default 0)
        :param int duelLosses: The total number of duels the user has lost (Default 0)
        :param int duelCreditsWins: The total amount of credits the user has won through fighting duels (Default 0)
        :param int duelCreditsLosses: The total amount of credits the user has lost through fighting duels (Default 0)
        :param userAlerts: A dictionary mapping either (UserAlerts.UABase subtypes or string UA ids from UserAlerts.userAlertsIDsTypes) to either (instances of that subtype or booleans representing the alert state) (Default {})
        :type userAlerts: dict[type or str, UserAlerts.UABase or bool]
        :param int bountyWinsToday: The number of bounties the user has won today (Default 0)
        :param datetime.datetime dailyBountyWinsReset: A datetime.datetime representing the time at which the user's bountyWinsToday should be reset to zero (Default datetime.utcnow())
        :param bool pollOwned: Whether or not this user has a running ReactionPollMenu (Default False)
        :raise TypeError: When given an argument of incorrect type
        """
        if type(id) == float:
            id = int(id)
        elif type(id) != int:
            raise TypeError("id must be int, given " + str(type(id)))

        if type(credits) == float:
            credits = int(credits)
        elif type(credits) != int:
            raise TypeError("credits must be int, given " + str(type(credits)))

        if type(lifetimeCredits) == float:
            lifetimeCredits = int(lifetimeCredits)
        elif type(lifetimeCredits) != int:
            raise TypeError("lifetimeCredits must be int, given " + str(type(lifetimeCredits)))

        if type(bountyCooldownEnd) == int:
            bountyCooldownEnd = float(bountyCooldownEnd)
        if type(bountyCooldownEnd) != float:
            raise TypeError("bountyCooldownEnd must be float, given " + str(type(bountyCooldownEnd)))

        if type(systemsChecked) == float:
            systemsChecked = int(systemsChecked)
        elif type(systemsChecked) != int:
            raise TypeError("systemsChecked must be int, given " + str(type(systemsChecked)))

        if type(bountyWins) == float:
            bountyWins = int(bountyWins)
        elif type(bountyWins) != int:
            raise TypeError("bountyWins must be int, given " + str(type(bountyWins)))

        self.id = id
        self.credits = credits
        self.lifetimeCredits = lifetimeCredits
        self.bountyCooldownEnd = bountyCooldownEnd
        self.systemsChecked = systemsChecked
        self.bountyWins = bountyWins

        self.activeShip = activeShip
        self.inactiveShips = inactiveShips
        self.inactiveModules = inactiveModules
        self.inactiveWeapons = inactiveWeapons
        self.inactiveTurrets = inactiveTurrets

        self.lastSeenGuildId = lastSeenGuildId
        self.hasLastSeenGuildId = lastSeenGuildId != -1

        self.duelRequests = {}
        self.duelWins = duelWins
        self.duelLosses = duelLosses

        self.duelCreditsWins = duelCreditsWins
        self.duelCreditsLosses = duelCreditsLosses

        self.userAlerts = {}
        # Convert the given user alerts to types and instances. The given alerts may be IDs instead of types, or booleans instead of instances.
        for alertID in UserAlerts.userAlertsIDsTypes:
            alertType = UserAlerts.userAlertsIDsTypes[alertID]
            if alertType in alerts:
                if isinstance(alerts[alertType], UserAlerts.UABase):
                    self.userAlerts[alertType] = alerts[alertType]
                elif isinstance(alerts[alertType], bool):
                    self.userAlerts[alertType] = alertType(alerts[alertType])
                else:
                    bbLogger.log("bbUsr", "init", "Given unknown alert state type for UA " + alertID + ". Must be either UABase or bool, given " + alerts[alertType].__class__.__name__ + ". Alert reset to default (" + str(alertType(bbConfig.userAlertsIDsDefaults[alertID])) + ")", category="usersDB", eventType="LOAD-UA_STATE_TYPE")
                    self.userAlerts[alertType] = alertType(bbConfig.userAlertsIDsDefaults[alertID])
            elif alertID in alerts:
                if isinstance(alerts[alertID], UserAlerts.UABase):
                    self.userAlerts[alertType] = alerts[alertID]
                elif isinstance(alerts[alertID], bool):
                    self.userAlerts[alertType] = alertType(alerts[alertID])
                else:
                    bbLogger.log("bbUsr", "init", "Given unknown alert state type for UA " + alertID + ". Must be either UABase or bool, given " + alerts[alertID].__class__.__name__ + ". Alert reset to default (" + str(alertType(bbConfig.userAlertsIDsDefaults[alertID])) + ")", category="usersDB", eventType="LOAD-UA_STATE_TYPE")
                    self.userAlerts[alertType] = alertType(bbConfig.userAlertsIDsDefaults[alertID])
            else:
                self.userAlerts[alertType] = alertType(bbConfig.userAlertsIDsDefaults[alertID])

        self.bountyWinsToday = bountyWinsToday
        self.dailyBountyWinsReset = dailyBountyWinsReset

        self.pollOwned = pollOwned

    
    def resetUser(self):
        """Reset the user's attributes back to their default values.
        """
        self.credits = 0
        self.lifetimeCredits = 0
        self.bountyCooldownEnd = -1
        self.systemsChecked = 0
        self.bountyWins = 0
        self.activeShip = bbShip.fromDict(defaultShipLoadoutDict)
        self.inactiveModules.clear()
        self.inactiveShips.clear()
        self.inactiveWeapons.clear()
        self.inactiveTurrets.clear()
        self.duelWins = 0
        self.duelLosses = 0
        self.duelCreditsWins = 0
        self.duelCreditsLosses = 0
        self.pollOwned = False


    def numInventoryPages(self, item : str, maxPerPage : int) -> int:
        """Get the number of pages required to display all of the user's unequipped items of the named type, displaying the given number of items per page
        
        :param str item: The name of the item type whose inventory pages to calculate
        :param int maxPerPage: The maximum number of items that may be present on a single page of items (TODO: Add a default)
        :return: The number of pages of size maxPerPage needed to display all of the user's inactive items of the named type
        :rtype: int
        :raise ValueError: When requesting an invalid item type
        :raise NotImplementedError: When requesting a valid item type, but one that is not yet implemented (e.g commodity)
        """
        if item not in bbConfig.validItemNames:
            raise ValueError("Requested an invalid item name: " + item)

        numWeapons = self.inactiveWeapons.numKeys
        numModules = self.inactiveModules.numKeys
        numTurrets = self.inactiveTurrets.numKeys
        numShips = self.inactiveShips.numKeys

        itemsNum = 0

        if item == "all":
            itemsNum = max(numWeapons, numModules, numTurrets, numShips)
        elif item == "module":
            itemsNum = numModules
        elif item == "weapon":
            itemsNum = numWeapons
        elif item == "turret":
            itemsNum = numTurrets
        elif item == "ship":
            itemsNum = numShips
        else:
            raise NotImplementedError("Valid but unsupported item name: " + item)
        
        return int(itemsNum/maxPerPage) + (0 if itemsNum % maxPerPage == 0 else 1)

    
    def lastItemNumberOnPage(self, item : str, pageNum : int, maxPerPage : int) -> int:
        """Get index of the last item on the given page number, where page numbers are of size maxPerPage.
        This is an absolute index from the start of the inventory, not a relative index from the start of the page.
        
        :param str item: The name of the item type whose last index to calculate
        :param int maxPerPage: The maximum number of items that may be present on a single page of items (TODO: Add a default)
        :return: The index of the last item on page pageNum, where page numbers are of size maxPerPage
        :rtype: int
        :raise ValueError: When requesting an invalid item type
        :raise NotImplementedError: When requesting a valid item type, but one that is not yet implemented (e.g commodity)
        """
        if item not in bbConfig.validItemNames:
            raise ValueError("Requested an invalid item name: " + item)
        if pageNum < self.numInventoryPages(item, maxPerPage):
            return pageNum * maxPerPage
            
        elif item == "ship":
            return self.inactiveShips.numKeys
        elif item == "weapon":
            return self.inactiveWeapons.numKeys
        elif item == "module":
            return self.inactiveModules.numKeys
        elif item == "turret":
            return self.inactiveTurrets.numKeys
        else:
            raise NotImplementedError("Valid but unsupported item name: " + item)


    def unequipAll(self, ship : bbShip.bbShip):
        """Unequip all items from the given bbShip, and move them into the user's inactive items ('hangar')
        The user must own ship.

        :param bbShip ship: the ship whose items to transfer to storage
        :raise TypeError: When given any other type than bbShip
        :raise RuntimeError: when given a bbShip that is not owned by this user
        """
        if not type(ship) == bbShip.bbShip:
            raise TypeError("Can only unequipAll from a bbShip. Given " + str(type(ship)))

        if not (self.activeShip == ship or ship in self.inactiveShips):
            raise RuntimeError("Attempted to unequipAll on a ship that isnt owned by this bbUser")

        for weapon in ship.weapons:
            self.inactiveWeapons.addItem(weapon)
        ship.clearWeapons()

        for module in ship.modules:
            self.inactiveModules.addItem(module)
        ship.clearModules()

        for turret in ship.turrets:
            self.inactiveTurrets.addItem(turret)
        ship.clearTurrets()


    def validateLoadout(self):
        """Ensure that the user's active loadout complies with bbModuleFactory.maxModuleTypeEquips
        This method was written as a transferal measure when maxModuleTypeEquips was first released, and should seldom be used
        """
        incompatibleModules = []
        allModulesChecked = False

        for currentModule in self.activeShip.modules:
            if not self.activeShip.canEquipModuleType(currentModule.getType()):
                incompatibleModules.append(currentModule)
                self.activeShip.unequipModuleObj(currentModule)

        finalModules = []
        for currentModule in incompatibleModules:
            if self.activeShip.canEquipModuleType(currentModule.getType()):
                self.activeShip.equipModule(currentModule)
            else:
                finalModules.append(currentModule)
        
        for currentModule in finalModules:
            self.inactiveModules.addItem(currentModule)


    def equipShipObj(self, ship : bbShip.bbShip, noSaveActive=False):
        """Equip the given ship, replacing the active ship.
        Give noSaveActive=True to delete the currently equipped ship.

        :param bbShip ship: The ship to equip. Must be owned by this user
        :param bool noSaveActive: Give True to delete the currently equipped ship. Give False to move the active ship to the hangar. (Default False)
        :raise RuntimeError: When given a bbShip that is not owned by this user
        """
        if not (self.activeShip == ship or ship in self.inactiveShips):
            raise RuntimeError("Attempted to equip a ship that isnt owned by this bbUser")
        if not noSaveActive and self.activeShip is not None:
            self.inactiveShips.addItem(self.activeShip)
        if ship in self.inactiveShips:
            self.inactiveShips.removeItem(ship)
        self.activeShip = ship

    
    def equipShipIndex(self, index : int):
        """Equip the ship at the given index in the user's inactive ships

        :param int index: The index from the user's inactive ships of the requested ship
        :raise IndexError: When given an index that is out of range of the user's inactive ships
        """
        if not (0 <= index <= self.inactiveShips.numKeys - 1):
            raise IndexError("Index out of range")
        if self.activeShip is not None:
            self.inactiveShips.addItem(self.activeShip)
        self.activeShip = self.inactiveShips[index]
        self.inactiveShips.removeItem(self.activeShip)


    def toDictNoId(self) -> dict:
        """Serialize this bbUser to a dictionary representation for saving to file.

        :return: A dictionary containing all information needed to recreate this user
        :rtype: dict
        """
        inactiveShipsDict = []
        for ship in self.inactiveShips.keys:
            inactiveShipsDict.append(self.inactiveShips.items[ship].toDict())

        inactiveModulesDict = []
        for module in self.inactiveModules.keys:
            inactiveModulesDict.append(self.inactiveModules.items[module].toDict())

        inactiveWeaponsDict = []
        for weapon in self.inactiveWeapons.keys:
            inactiveWeaponsDict.append(self.inactiveWeapons.items[weapon].toDict())

        inactiveTurretsDict = []
        for turret in self.inactiveTurrets.keys:
            inactiveTurretsDict.append(self.inactiveTurrets.items[turret].toDict())

        alerts = {}
        for alertID in self.userAlerts.keys():
            if isinstance(self.userAlerts[alertID], UserAlerts.StateUserAlert):
                alerts[alertID] = self.userAlerts[alertID].state

        return {"credits":self.credits, "lifetimeCredits":self.lifetimeCredits,
                "bountyCooldownEnd":self.bountyCooldownEnd, "systemsChecked":self.systemsChecked,
                "bountyWins":self.bountyWins, "activeShip": self.activeShip.toDict(), "inactiveShips":inactiveShipsDict,
                "inactiveModules":inactiveModulesDict, "inactiveWeapons":inactiveWeaponsDict, "inactiveTurrets": inactiveTurretsDict, "lastSeenGuildId":self.lastSeenGuildId,
                "duelWins": self.duelWins, "duelLosses": self.duelLosses, "duelCreditsWins": self.duelCreditsWins, "duelCreditsLosses": self.duelCreditsLosses,
                "bountyWinsToday": self.bountyWinsToday, "dailyBountyWinsReset": self.dailyBountyWinsReset.timestamp(), "pollOwned": self.pollOwned}


    def userDump(self) -> str:
        """Get a string containing key information about the user.

        :return: A string containing the user ID, credits, lifetimeCredits, bountyCooldownEnd, systemsChecked and bountyWins
        :rtype: str
        """
        data = "bbUser #" + str(self.id) + ": "
        for att in [self.credits, self.lifetimeCredits, self.bountyCooldownEnd, self.systemsChecked, self.bountyWins]:
            data += str(att) + "/"
        return data[:-1]


    def getStatByName(self, stat : str) -> Union[int, float]:
        """Get a user attribute by its string name. This method is primarily used in leaderboard generation.

        :param str stat: One of id, credits, lifetimeCredits, bountyCooldownEnd, systemsChecked, bountyWins or value
        :return: The requested user attribute
        :rtype: int or float
        :raise ValueError: When given an invalid stat name
        """
        if stat == "id":
            return self.id
        elif stat == "credits":
            return self.credits
        elif stat == "lifetimeCredits":
            return self.lifetimeCredits
        elif stat == "bountyCooldownEnd":
            return self.bountyCooldownEnd
        elif stat == "systemsChecked":
            return self.systemsChecked
        elif stat == "bountyWins":
            return self.bountyWins
        elif stat == "value":
            modulesValue = 0
            for module in self.inactiveModules.keys:
                modulesValue += self.inactiveModules.items[module].count * module.getValue()
            turretsValue = 0
            for turret in self.inactiveTurrets.keys:
                turretsValue += self.inactiveTurrets.items[turret].count * turret.getValue()
            weaponsValue = 0
            for weapon in self.inactiveWeapons.keys:
                weaponsValue += self.inactiveWeapons.items[weapon].count * weapon.getValue()
            shipsValue = 0
            for ship in self.inactiveShips.keys:
                shipsValue += self.inactiveShips.items[ship].count * ship.getValue()

            return modulesValue + turretsValue + weaponsValue + shipsValue + self.activeShip.getValue() + self.credits
        else:
            raise ValueError("Unknown stat name: " + str(stat))


    def getInactivesByName(self, item : str) -> bbInventory:
        """Get the all of the user's inactive (hangar) items of the named type.
        The given bbInventory is mutable, and can alter the contents of the user's inventory.

        :param str item: One of ship, weapon, module or turret
        :return: A bbInventory containing all of the user's inactive items of the named type.
        :rtype: bbInventory
        :raise ValueError: When requesting an invalid item type name
        :raise NotImplementedError: When requesting a valid item type name, but one that is not yet implemented (e.g commodity)
        """
        if item == "all" or item not in bbConfig.validItemNames:
            raise ValueError("Invalid item type: " + item)
        if item == "ship":
            return self.inactiveShips
        if item == "weapon":
            return self.inactiveWeapons
        if item == "module":
            return self.inactiveModules
        if item == "turret":
            return self.inactiveTurrets
        else:
            raise NotImplementedError("Valid, but unrecognised item type: " + item)


    def hasDuelChallengeFor(self, targetBBUser : bbUser) -> bool:
        """Decide whether or not this user has an active duel request targetted at the given bbUser

        :param bbUser targetBBUser: The user to check for duel request existence
        :return: True if this user has sent a duel request to the given user, and it is still active. False otherwise
        :rtype: bool
        """
        return targetBBUser in self.duelRequests


    def addDuelChallenge(self, duelReq : DuelRequest.DuelRequest):
        """Store a new duel request from this user to another.
        The duel request must still be active (TODO: Add validation), the source user must be this user,
        the target user must not be this user, and this user must not already have a duel challenge for the target user.

        :param DuelRequest duelReq: The duel request to store
        :raise ValueError: When given a duel request where either: This is not the source user, this is the target user, or a duel request is already stored for the target user (TODO: Move to separate exception types)
        """
        if duelReq.sourceBBUser is not self:
            raise ValueError("Attempted to add a DuelRequest for a different source user: " + str(duelReq.sourceBBUser.id))
        if self.hasDuelChallengeFor(duelReq.targetBBUser):
            raise ValueError("Attempted to add a DuelRequest for an already challenged user: " + str(duelReq.sourceBBUser.id))
        if duelReq.targetBBUser is self:
            raise ValueError("Attempted to add a DuelRequest for self: " + str(duelReq.sourceBBUser.id))
        self.duelRequests[duelReq.targetBBUser] = duelReq


    def removeDuelChallengeObj(self, duelReq : DuelRequest.DuelRequest):
        """Remove the given duel request object from this user's storage.

        :param DuelRequest duelReq: The DuelRequest to remove
        :raise ValueError: When given a duel request that this user object is unaware of
        """
        if not duelReq.targetBBUser in self.duelRequests or self.duelRequests[duelReq.targetBBUser] is not duelReq:
            raise ValueError("Duel request not found: " + str(duelReq.sourceBBUser.id) + " -> " + str(duelReq.sourceBBUser.id))
        del self.duelRequests[duelReq.targetBBUser]
    
    
    def removeDuelChallengeTarget(self, duelTarget : bbUser.bbUser):
        """Remove this user's duel request that is targetted at the given user.

        :param bbUser duelTarget: The target user whose duel request to remove
        """
        self.removeDuelChallengeObj(self.duelRequests[duelTarget])


    # TODO: Consider moving these alert functions to UserAlerts.py
    async def setAlertByType(self, alertType : type, dcGuild : Guild, bbGuild : bbGuild.bbGuild, dcMember : Member, newState : bool) -> bool:
        """Set the state of one of this users's UserAlerts, identifying the alert by its class.

        :param type alertType: The class of the alert whose state to set. Must be a subclass of UserAlerts.UABase
        :param discord.Guild dcGuild: The discord guild in which to set the alert state (currently only relevent for role-based alerts)
        :param bbGuild bbGuild: The bbGuild in which to set the alert state (currently only relevent for role-based alerts, as the role must be looked up) 
        :param discord.Member dcMember: This user's member object in dcGuild (TODO: Just grab dcMember from dcGuild in here)
        :param bool newState: The new desired of the alert
        """
        await self.userAlerts[alertType].setState(dcGuild, bbGuild, dcMember, newState)
        return newState


    async def setAlertByID(self, alertID : str, dcGuild : Guild, bbGuild : bbGuild.bbGuild, dcMember : Member, newState) -> bool:
        """Set the state of one of this users's UserAlerts, identifying the alert by its ID as given by UserAlerts.userAlertsIDsTypes.

        :param str alertID: The ID of the user alert type, as given by UserAlerts.userAlertsIDsTypes
        :param discord.Guild dcGuild: The discord guild in which to set the alert state (currently only relevent for role-based alerts)
        :param bbGuild bbGuild: The bbGuild in which to set the alert state (currently only relevent for role-based alerts, as the role must be looked up) 
        :param discord.Member dcMember: This user's member object in dcGuild (TODO: Just grab dcMember from dcGuild in here)
        :param bool newState: The new desired of the alert
        """
        return await self.setAlertType(UserAlerts.userAlertsIDsTypes[alertID], dcGuild, bbGuild, dcMember, newState)


    async def toggleAlertType(self, alertType : type, dcGuild : Guild, bbGuild : bbGuild.bbGuild, dcMember : Member) -> bool:
        """Toggle the state of one of this users's UserAlerts, identifying the alert by its class.

        :param type alertType: The class of the alert whose state to toggle. Must be a subclass of UserAlerts.UABase
        :param discord.Guild dcGuild: The discord guild in which to toggle the alert state (currently only relevent for role-based alerts)
        :param bbGuild bbGuild: The bbGuild in which to toggle the alert state (currently only relevent for role-based alerts, as the role must be looked up) 
        :param discord.Member dcMember: This user's member object in dcGuild (TODO: Just grab dcMember from dcGuild in here)
        """
        return await self.userAlerts[alertType].toggle(dcGuild, bbGuild, dcMember)

    
    async def toggleAlertID(self, alertID : str, dcGuild : Guild, bbGuild : bbGuild.bbGuild, dcMember : Member) -> bool:
        """Toggle the state of one of this users's UserAlerts, identifying the alert by its ID as given by UserAlerts.userAlertsIDsTypes.

        :param str alertID: The ID of the user alert type, as given by UserAlerts.userAlertsIDsTypes
        :param discord.Guild dcGuild: The discord guild in which to toggle the alert state (currently only relevent for role-based alerts)
        :param bbGuild bbGuild: The bbGuild in which to toggle the alert state (currently only relevent for role-based alerts, as the role must be looked up) 
        :param discord.Member dcMember: This user's member object in dcGuild (TODO: Just grab dcMember from dcGuild in here)
        """
        return await self.toggleAlertType(UserAlerts.userAlertsIDsTypes[alertID], dcGuild, bbGuild, dcMember)


    def isAlertedForType(self, alertType : type, dcGuild : Guild, bbGuild : bbGuild.bbGuild, dcMember : Member) -> bool:
        """Get the state of one of this users's UserAlerts, identifying the alert by its class.

        :param type alertType: The class of the alert whose state to get. Must be a subclass of UserAlerts.UABase
        :param discord.Guild dcGuild: The discord guild in which to get the alert state (currently only relevent for role-based alerts)
        :param bbGuild bbGuild: The bbGuild in which to get the alert state (currently only relevent for role-based alerts, as the role must be looked up) 
        :param discord.Member dcMember: This user's member object in dcGuild (TODO: Just grab dcMember from dcGuild in here)
        """
        return self.userAlerts[alertType].getState(dcGuild, bbGuild, dcMember)

    
    def isAlertedForID(self, alertID : str, dcGuild : Guild, bbGuild : bbGuild.bbGuild, dcMember : Member) -> bool:
        """Get the state of one of this user's UserAlerts, identifying the alert by its ID as given by UserAlerts.userAlertsIDsTypes.

        :param str alertID: The ID of the user alert type, as given by UserAlerts.userAlertsIDsTypes
        :param discord.Guild dcGuild: The discord guild in which to get the alert state (currently only relevent for role-based alerts)
        :param bbGuild bbGuild: The bbGuild in which to get the alert state (currently only relevent for role-based alerts, as the role must be looked up) 
        :param discord.Member dcMember: This user's member object in dcGuild (TODO: Just grab dcMember from dcGuild in here)
        """
        return self.isAlertedForType(UserAlerts.userAlertsIDsTypes[alertID], dcGuild, bbGuild, dcMember)


    def __str__(self) -> str:
        """Get a short string summary of this bbUser. Currently only contains the user ID.

        :return: A string summar of the user, containing the user ID
        :rtype: str
        """
        return "<bbUser #" + str(self.id) + ">"


def fromDict(id : int, userDict : dict) -> bbUser:
    """Construct a new bbUser object from the given ID and the information in the given dictionary - The opposite of bbUser.toDict

    :param int id: The discord ID of the user
    :param dict userDict: A dictionary containing all information necessary to construct the bbUser object, other than their ID.
    :return: A bbUser object as described in userDict
    :rtype: bbUser 
    """
    activeShip = bbShip.fromDict(userDict["activeShip"])

    inactiveShips = bbInventory.bbInventory()
    if "inactiveShips" in userDict:
        for shipListingDict in userDict["inactiveShips"]:
            inactiveShips.addItem(bbShip.fromDict(shipListingDict["item"]), quantity=shipListingDict["count"])

    inactiveWeapons = bbInventory.bbInventory()
    if "inactiveWeapons" in userDict:
        for weaponListingDict in userDict["inactiveWeapons"]:
            inactiveWeapons.addItem(bbWeapon.fromDict(weaponListingDict["item"]), quantity=weaponListingDict["count"])

    inactiveModules = bbInventory.bbInventory()
    if "inactiveModules" in userDict:
        for moduleListingDict in userDict["inactiveModules"]:
            inactiveModules.addItem(bbModuleFactory.fromDict(moduleListingDict["item"]), quantity=moduleListingDict["count"])

    inactiveTurrets = bbInventory.bbInventory()
    if "inactiveTurrets" in userDict:
        for turretListingDict in userDict["inactiveTurrets"]:
            inactiveTurrets.addItem(bbTurret.fromDict(turretListingDict["item"]), quantity=turretListingDict["count"])

    return bbUser(id, credits=userDict["credits"], lifetimeCredits=userDict["lifetimeCredits"],
                    bountyCooldownEnd=userDict["bountyCooldownEnd"], systemsChecked=userDict["systemsChecked"],
                    bountyWins=userDict["bountyWins"], activeShip=activeShip, inactiveShips=inactiveShips,
                    inactiveModules=inactiveModules, inactiveWeapons=inactiveWeapons, inactiveTurrets=inactiveTurrets, lastSeenGuildId=userDict["lastSeenGuildId"] if "lastSeenGuildId" in userDict else -1,
                    duelWins=userDict["duelWins"] if "duelWins" in userDict else 0, duelLosses=userDict["duelLosses"] if "duelLosses" in userDict else 0, duelCreditsWins=userDict["duelCreditsWins"] if "duelCreditsWins" in userDict else 0, duelCreditsLosses=userDict["duelCreditsLosses"] if "duelCreditsLosses" in userDict else 0,
                    alerts=userDict["alerts"] if "alerts" in userDict else {}, bountyWinsToday=userDict["bountyWinsToday"] if "bountyWinsToday" in userDict else 0, dailyBountyWinsReset=datetime.utcfromtimestamp(userDict["dailyBountyWinsReset"]) if "dailyBountyWinsReset" in userDict else datetime.utcnow(), pollOwned=userDict["pollOwned"] if "pollOwned" in userDict else False)
