import discord
from datetime import datetime, timedelta
import asyncio
import random
# from bbdata import System, factions, bountyNames, securityLevels, systems
import bbdata
import bbutil
import bbPRIVATE

maxBountiesPerFaction = 5
sendChannel = 699744305715085334
botLoggedIn = False


def makeRoute(start, end):
    open = [start]
    closed = []
    route = [start]
    while open:
        q = open.pop(0)


class Bounty:
    issueTime = -1
    name = ""
    route = []
    reward = 0.0
    endTime = -1
    faction = ""
    visited = {}

    def __init__(self, faction="", issueTime=-1.0, name="", route=[], reward=-1.0, endTime=-1.0):
        self.issueTime = issueTime
        self.name = name
        self.route = route
        self.reward = reward
        self.endTime = endTime
        self.faction = faction

        if self.faction == "":
            self.faction = random.choice(bbdata.factions)
        if self.faction not in bbdata.factions:
            raise RuntimeError("makeBounty: Invalid faction requested '" + faction + "'")
    
        if self.route == []:
            self.route = random.choice(bountyRoutes)
            if random.choice([True, False]):
                self.route = self.route[::-1]
        if self.name == "":
            self.name = random.choice(bbdata.bountyNames[faction])
        if self.reward == -1.0:
            self.reward = len(self.route) * 10
        if self.issueTime == -1.0:
            self.issueTime = datetime.utcnow().timestamp()
        if self.endTime == -1.0:
            self.endTime = (self.issueTime + timedelta(days=len(self.route))).timestamp()
        for station in self.route:
            self.visited[station] = 


def makeBounty(faction="", bountyName=""):
    if faction == "":
        faction = random.choice(bbdata.factions)
    if faction not in bbdata.factions:
        raise RuntimeError("makeBounty: Invalid faction requested '" + faction + "'")
    
    route = random.choice(bountyRoutes)
    if random.choice([True, False]):
        route = route[::-1]
    if bountyName == "":
        bountyName = random.choice(bbdata.bountyNames[faction])
    reward = len(route) * 10
    issue = datetime.utcnow()
    due = issue + timedelta(days=len(route))
    return faction, {"issueTime": issue.timestamp(), "name": bountyName, "route": route, "reward": reward, "endTime": due.timestamp()}


def bountyNameExists(bountiesList, nameToFind):
    for bounty in bountiesList:
        if bounty["name"] == nameToFind:
            return True
    return False


BBDB = bbutil.readJDB("BBDB.json")
client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    botLoggedIn = True
    while botLoggedIn:
        await asyncio.sleep(5)
        # Make new bounties
        newFaction = random.choice(bbdata.factions)
        while len(BBDB["bounties"][newFaction]) >= maxBountiesPerFaction:
            newFaction = random.choice(bbdata.factions)
        newName = random.choice(bbdata.bountyNames[newFaction])
        while bountyNameExists(BBDB["bounties"][newFaction], newName): 
            newName = random.choice(bbdata.bountyNames[newFaction])
        newBounty = makeBounty(faction=newFaction, bountyName=newName)[1]
        BBDB["bounties"][newFaction].append(newBounty)
        if sendChannel != 0:
            await client.get_channel(sendChannel).send("New " + newFaction + " bounty: " + newName)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!bb'):
        if message.content == '!bb hello':
            await message.channel.send('Hello!')
        elif message.content == "!bb setchannel":
            sendChannel = message.channel.id
        elif message.author.id == 188618589102669826 and message.content == "!bb s":
            botLoggedIn = False
            await client.logout()
            bbutil.writeJDB("BBDB.json", BBDB)
        elif message.content == "!bb win":
            if str(message.author.id) not in BBDB["users"]:
                BBDB["users"][str(message.author.id)] = {"credits":0}
            BBDB["users"][str(message.author.id)]["credits"] += 10
            await message.channel.send("<@" + str(message.author.id) + ">, you now have " + str(BBDB["users"][str(message.author.id)]["credits"]) + " credits!")
        elif len(message.content.split(" ")) == 2 and message.content.split(" ")[1].lower() in bbdata.factions:
            requestedFaction = message.content.split(" ")[1].lower()
            if len(BBDB["bounties"][requestedFaction]) == 0:
                await message.channel.send("There are no " + requestedFaction + " bounties active currently!")
            else:
                outmessage = "active " + requestedFaction + " bounties:"
                for bounty in BBDB["bounties"][requestedFaction]:
                    outmessage += "\n - " + bounty["name"] + ": " + str(bounty["reward"]) + " credits, issued: " + datetime.utcfromtimestamp(bounty["issueTime"]).strftime("%B-%d %H:%M:%S") + ", ending: " + datetime.utcfromtimestamp(bounty["endTime"]).strftime("%B-%d %H:%M:%S")
                await message.channel.send(outmessage)
        elif len(message.content.split(" ")) > 3 and message.content.split(" ")[1].lower() in bbdata.factions and message.content.split(" ")[2].lower() == "route":
            requestedBountyName = ""
            for section in message.content.split(" ")[3:]:
                requestedBountyName += " " + section
            if len(requestedBountyName) > 0:
                requestedBountyName = requestedBountyName[1:]
            requestedFaction = message.content.split(" ")[1].lower()
            bountyFound = False
            for bounty in BBDB["bounties"][requestedFaction]:
                if bounty["name"] == requestedBountyName:
                    bountyFound = True
                    outmessage = requestedBountyName + "'s current route:"
                    for system in bounty["route"]:
                        outmessage += " " + system + ","
                    outmessage = outmessage[:-1] + "."
                    await message.channel.send(outmessage)
            if (not bountyFound):
                await message.channel.send("That pilot is not on the " + requestedFaction + " bounty board!")
        else:
            await message.channel.send("""Can't do that, pilot. Type "!bb help" for a list of commands o7""")
        
client.run(bbPRIVATE.botToken)
