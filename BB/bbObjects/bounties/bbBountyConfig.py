# Typing imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...bbDatabases import bbBountyDB

import random
from datetime import datetime, timedelta

from ...bbConfig import bbData, bbConfig
from ... import bbUtil

class BountyConfig:
    """
    Configurator class describing all attributes needed for a bbBounty object.

    :var faction: The faction owning this bounty
    :vartype faction: str
    :var name: The name of the wanted criminal. If this is a player bounty, name should be the player mention.
    :vartype name: str
    :var isPlayer: Whether or not the target criminal is a player or an npc
    :vartype isPlayer: bool
    :var route: the names of systems in this bounty's route
    :vartype route: list[str]
    :var start: The name of the system at the start of the route
    :vartype start: str
    :var end: The name of the system at the end of the route
    :vartype end: str
    :var answer: The name of the system where the criminal is located
    :vartype answer: str
    :var checked: Dictionary of system names to user IDs, where the id corresponds to the user who checked that system, or -1 if the system is unchecked.
    :vartype checked: dict[str, int]
    :var reward: Prize pool of credits to award to contributing users
    :vartype reward: int
    :var issueTime: A utc timestamp representing the time at which the bounty was issued
    :vartype issueTime: float
    :var endTime: A utc timestamp representing the time at which the bounty should automatically expire
    :vartype endTime: flaot
    :var icon: A URL directly linking to an image to use as the criminal's icon
    :vartype icon: str
    :var aliases: Aliases that can be used to refer to this criminal
    :vartype aliases: list[str]
    :var wiki: The page to link to as the criminal's wiki, in their info embed
    :vartype wiki: str
    :var builtIn: whether or not this is a built in npc criminal
    :vartype builtIn: bool
    :var generated: whether or not this config is ready to be used. The config must verify and generate its attributes before they can be used in a bbBounty.
    :vartype generated: bool
    :var ship: The bbShip this criminal should equip
    :vartype ship: bbShip
    """

    def __init__(self, faction="", name="", isPlayer=None, route=[], start="", end="", answer="", checked={}, reward=-1, issueTime=-1.0, endTime=-1.0, icon="", aliases=[], wiki="", ship=None):
        """All parameters are optional. If a parameter is not given, it will be randomly generated.

        :param faction: The faction owning this bounty
        :type faction: str
        :param name: The name of the wanted criminal. If this is a player bounty, name should be the player mention.
        :type name: str
        :param isPlayer: Whether or not the target criminal is a player or an npc
        :type isPlayer: bool
        :param route: the names of systems in this bounty's route
        :type route: list[str]
        :param start: The name of the system at the start of the route
        :type start: str
        :param end: The name of the system at the end of the route
        :type end: str
        :param answer: The name of the system where the criminal is located
        :type answer: str
        :param checked: Dictionary of system names to user IDs, where the id corresponds to the user who checked that system, or -1 if the system is unchecked.
        :type checked: dict[str, int]
        :param reward: Prize pool of credits to award to contributing users
        :type reward: int
        :param issueTime: A utc timestamp representing the time at which the bounty was issued
        :type issueTime: float
        :param endTime: A utc timestamp representing the time at which the bounty should automatically expire
        :type endTime: flaot
        :param icon: A URL directly linking to an image to use as the criminal's icon
        :type icon: str
        :param aliases: Aliases that can be used to refer to this criminal
        :type aliases: list[str]
        :param wiki: The page to link to as the criminal's wiki, in their info embed
        :type wiki: str
        :param ship: The bbShip this criminal should equip
        :type ship: bbShip
        """
        self.faction = faction.lower()
        self.name = name.title()
        self.isPlayer = False if isPlayer is None else isPlayer
        self.route = []
        for system in route:
            self.route.append(system.title())

        self.start = start.title()
        self.end = end.title()
        self.answer = answer.title()
        self.checked = checked
        self.reward = reward
        if type(reward) == float:
            self.reward = int(reward)
        self.issueTime = issueTime
        self.endTime = endTime
        self.icon = icon
        self.generated = False
        self.builtIn = False

        self.aliases = aliases
        self.wiki = wiki

        self.ship = ship
        
    
    def generate(self, bountyDB : bbBountyDB.bbBountyDB, noCriminal=True, forceKeepChecked=False, forceNoDBCheck=False):
        """Validate all given config data, and randomly generate missing data.

        :param bbBountyDB bountyDB: Database containing all currently active bounties. When forceNoDBCheck is True, this is ignored.
        :param bool noCriminal: If this is True, randomly generate a bbCriminal object. (Default True)
        :param bool forceKeepChecked: If this is False, a blank checked dictionary will be used. This should only be set to be True when using a pre-made checked dictionary; e.g for custom bounties or for bounties loaded from file. (Default False)
        :param bool forceNoDBCheck: If this is False, do not check if the bounty already exists. This should only be used as a performance and compatibility measure when loading in a bounty from file. (Default False)
        :raise ValueError: When requesting an invalid faction, or when requesting an invalid reward amount
        :raise IndexError: When no space is available for a new bounty
        :raise KeyError: When the requested criminal name already exists in a bounty, or when requesting an unknown system name
        """
        doDBCheck = not forceNoDBCheck
        if noCriminal:
            if self.name in bbData.bountyNames:
                self.builtIn = True
            else:
                if self.faction == "":
                    self.faction = random.choice(bbData.bountyFactions)
                    while doDBCheck and not bountyDB.factionCanMakeBounty(self.faction):
                        self.faction = random.choice(bbData.bountyFactions)

                else:
                    if self.faction not in bbData.bountyFactions:
                        raise ValueError("BOUCONF_CONS_INVFAC: Invalid faction requested '" + self.faction + "'")
                    if doDBCheck and not bountyDB.factionCanMakeBounty(self.faction):
                        raise IndexError("BOUCONF_CONS_FACDBFULL: Attempted to generate new bounty config when no slots are available for faction: '" + self.faction + "'")

                if self.name == "":
                    self.builtIn = True
                    self.name = random.choice(bbData.bountyNames[self.faction])
                    while doDBCheck and bountyDB.bountyNameExists(self.name):
                        self.name = random.choice(bbData.bountyNames[self.faction])
                else:
                    if doDBCheck and bountyDB.bountyNameExists(self.name):
                        raise KeyError("BountyConfig: attempted to create config for pre-existing bounty: " + self.name)
                    
                    if self.icon == "":
                        self.icon = bbData.rocketIcon
        
        else:
            if doDBCheck and not bountyDB.factionCanMakeBounty(self.faction):
                raise IndexError("BOUCONF_CONS_FACDBFULL: Attempted to generate new bounty config when no slots are available for faction: '" + self.faction + "'")
        
        if self.route == []:
            if self.start == "":
                self.start = random.choice(list(bbData.builtInSystemObjs.keys()))
                while self.start == self.end or not bbData.builtInSystemObjs[self.start].hasJumpGate():
                    self.start = random.choice(list(bbData.builtInSystemObjs.keys()))
            elif self.start not in bbData.builtInSystemObjs:
                raise KeyError("BountyConfig: Invalid start system requested '" + self.start + "'")
            if self.end == "":
                self.end = random.choice(list(bbData.builtInSystemObjs.keys()))
                while self.start == self.end or not bbData.builtInSystemObjs[self.end].hasJumpGate():
                    self.end = random.choice(list(bbData.builtInSystemObjs.keys()))
            elif self.end not in bbData.builtInSystemObjs:
                raise KeyError("BountyConfig: Invalid end system requested '" + self.end + "'")
            # self.route = makeRoute(self.start, self.end)
            self.route = bbUtil.bbAStar(self.start, self.end, bbData.builtInSystemObjs)
        else:
            for system in self.route:
                if system not in bbData.builtInSystemObjs:
                    raise KeyError("BountyConfig: Invalid system in route '" + system + "'")
        if self.answer == "":
            self.answer = random.choice(self.route)
        elif self.answer not in bbData.builtInSystemObjs:
            raise KeyError("Bounty constructor: Invalid answer requested '" + self.answer + "'")
        
        if self.reward == -1:
            self.reward = int(len(self.route) * bbConfig.bPointsToCreditsRatio)
        elif self.reward < 0:
            raise ValueError("Bounty constructor: Invalid reward requested '" + str(self.reward) + "'")
        if self.issueTime == -1.0:
            self.issueTime = datetime.utcnow().replace(second=0).timestamp()
        if self.endTime == -1.0:
            self.endTime = (datetime.utcfromtimestamp(self.issueTime) + timedelta(days=len(self.route))).timestamp()

        if not forceKeepChecked:
            self.checked = {}
        for station in self.route:
            if (not forceKeepChecked) or station not in self.checked or self.checked == {}:
                self.checked[station] = -1

        self.generated = True
        
