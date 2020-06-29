import random

from BB.bbConfig import bbData
from BB.bountybot import usersDB, bbCommands

# TODO: add delay between mining attempts

ORE_TYPES = ["Iron", "Doxtrite", "Perrius", "Cesogen", "Hypanium", "Golden", "Sodil", "Pyresium", "Orichalzine", "Titanium"]
asteroid_tiers = ["D", "C", "B", "A"]
risky_aliases = ["risk", "risky", "danger", "dangerous"]
risky_mining_failure_chance = 5
max_ore_per_asteroid_tier = [62, 47, 34, 23]


def pickOre(oreList=ORE_TYPES):
    numAsteroids = len(oreList)
    choice = random.random() % numAsteroids
    return oreList[int(choice)]


def pickTier():
    return random.randint(1,4)


def tierToLetter(tier):
    return asteroid_tiers[tier-1]


def boolRiskArg(arg):
    return arg.lower() in risky_aliases


"""
gets result of mining attempt

@param drill -- type of drill being used
@param isRisky -- Choice of taking risk or not
@return -- returns ore type, amount, and if a core was obtained
"""
def mineResult(drill, isRisky, tier):
    # TODO: move max_ore_per_asteroid_tier to bbConfig
    # fails if exceeds drill handling or doesn't meet minimum requirement
    if isRisky and risky_mining_failure_chance > random.randint(1,100) > drill.handling:
        return 0, 0

    minedOre = max_ore_per_asteroid_tier[tier-1] * drill.oreYield

    if isRisky:
        if tier == 4:
            return minedOre, True
        return minedOre, False

    minedOre = minedOre * drill.handling
    variance = random.randint(-5, 5)
    return minedOre + variance, False


def mineAsteroid(user, tier, oreType, isRisky):
    if user.getDrill() is None:
        return "No drill equipped"
    else:
        returnMessage = ""
        results = mineResult(user.getDrill(), isRisky, tier)
        oreQuantity = results[0]
        gotCore = results[1]
        user.addCommodity(oreType, oreQuantity)
        remainingSpace = user.activeShip.cargo - user.commoditiesCollected
        if oreQuantity > remainingSpace:
            oreQuantity = remainingSpace
            if gotCore:
                oreQuantity -= 1
        if oreQuantity > 0:
            returnMessage += ("You mined a class " + tierToLetter(tier) + " " + str(oreType) + " asteroid yielding " + str(oreQuantity) + " ore")
            if gotCore:
                user.commodity(str(oreType) + " Core", 1)
                returnMessage += " and 1 core"
        else:
            returnMessage = "Asteroid mining failed"
        return returnMessage


def setRisky(message, isRisky):
    usersDB.getUser(message.author.id).defaultMineIsRisky = isRisky
    return


async def cmd_setRisk(message, args):
    user = usersDB.getUser(message.author.id)
    argsSplit = args.split(" ")
    arg = argsSplit[0]
    if arg.lower() is not "risky" or "dangerous" or "safe" or "cautious":
        message.channel.send("Please enter valid option")
        message.channel.send("valid options are \"risky\" \"dangerous\" \"safe\" or \"cautious\"")
    elif arg.lower() == "risky" or "dangerous":
        user.defaultMineIsRisky = True
    else:
        user.defaultMineIsRisky = False

bbCommands.register("setMineRisk", cmd_setRisk)
bbCommands.register("setRisk", cmd_setRisk)


async def cmd_mining(message, args):
    argsSplit = args.split(" ")
    user = usersDB.getUser(message.author.id)
    if user.commoditiesCollected >= user.activeShip.cargo:
        message.channel.send("You have exceeded your ship's cargo capacity")
    tier = pickTier()
    oreType = pickOre()
    if argsSplit[0] is not None:
        risk = argsSplit[0]
        if risk.lower() == "risk" or "risky":
            isRisky = True
        else:
            isRisky = False
    else:
        isRisky = user.defaultMineIsRisky
    sendMessage = mineAsteroid(user, tier, oreType, isRisky)
    message.channel.send(sendMessage)

bbCommands.register("mine", cmd_mining)
