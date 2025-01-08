import simulation, random, sbs, copy
from NPC_Ships import NPC_AI, fleetOrders

# stances - Attack, Defend, Raid, Disrupt, Search, Retreat"""

commanders = {} #Dictionary of Object ID and Object for each commander

commanderkillList = []
commanderaddList = []

OrdersDatabase = {
    "Attack": NPC_AI.LeaderBehaviours.Attack,
    "Hold Position": NPC_AI.LeaderBehaviours.HoldPosition,
    "Support Allies": NPC_AI.LeaderBehaviours.Support,
    "Patrol": NPC_AI.LeaderBehaviours.Patrol,
    "Defend": NPC_AI.LeaderBehaviours.Defend,
    "Fall Back": NPC_AI.EvasiveBehaviours.FallBack,
    "Reform": NPC_AI.LeaderBehaviours.Reform,
    "Surrender": NPC_AI.EvasiveBehaviours.Surrender
}

CarrierOrdersDatabase = {
    "Carrier Operations": NPC_AI.CarrierBehaviours.CarrierOperations,
}

SupportElementDatabase = {
    "All Stop": NPC_AI.GeneralBehaviours.AllStop,
    "Support Leader": NPC_AI.FollowerBehaviours.SupportLeader,
    "Follow": NPC_AI.FollowerBehaviours.Follow,
    "Carrier Support": NPC_AI.CarrierBehaviours.CarrierSupport
}

NonCombatOrdersDatabase = {
    "Transport": NPC_AI.NonCombatBehaviours.Transport
}

FighterOrdersDatabase = {
    "Strike": NPC_AI.CarrierBehaviours.Strike,
    "RTB": NPC_AI.CarrierBehaviours.RTB
}

EvasiveOrdersDatabase = {
    "Evade": NPC_AI.EvasiveBehaviours.Evade
}

tasksDatabase = OrdersDatabase | NonCombatOrdersDatabase | CarrierOrdersDatabase
ordersDatabase = SupportElementDatabase | OrdersDatabase | NonCombatOrdersDatabase | FighterOrdersDatabase | CarrierOrdersDatabase | EvasiveOrdersDatabase


class AISoloCommander:
    def __init__(self, FleetCommander, FleetMembers, FleetSize, **kwargs):
        self.FleetCommander = FleetCommander  # Single Script Object
        self.FleetCommanderID = FleetCommander.ObjectID
        self.FleetMembers = FleetMembers  # Dictionary of ID and script Objects
        self.FleetSize = FleetSize
        if "Orders" in kwargs.keys():
            self.Orders = kwargs.get("Orders")
        else:
            self.Orders = copy.deepcopy(fleetOrders.standardOrders)
        FleetCommander.ObjectData.set("Fleet Commander", id(self), 0)

    def checkFleetCommander(self):
        if not simulation.simul.space_object_exists(self.FleetCommanderID):
            self.FleetCommander = None
            commanderkillList.append(id(self))

    def AITickMonitors(self):
        self.checkFleetCommander()
        self.ExecuteOrders()

    def ExecuteOrders(self):
        if simulation.simul.space_object_exists(self.FleetCommanderID):
            NPC_AI.EvasiveBehaviours.CheckEvasion(self.FleetCommander)
            task = self.Orders.get("Fleet Task")
            order = ordersDatabase.get(task)
            order(self.FleetCommander, self.Orders)


class AIGroupCommander:
    def __init__(self, FleetCommander, FleetMembers, FleetSize, **kwargs):
        self.FleetCommander = FleetCommander  # Single Script Object (not game Object)
        self.FleetCommanderID = FleetCommander.ObjectID
        self.FleetMembers = FleetMembers  # Dictionary of ID and Objects (not game Object)
        self.FleetSize = FleetSize
        if "Orders" in kwargs.keys():
            self.Orders = kwargs.get("Orders")
        else:
            self.Orders = copy.deepcopy(fleetOrders.standardOrders)

        for member in FleetMembers.values():
            member.ObjectData.set("Fleet Commander", id(self), 0)

    def checkFleetCommander(self):
        if not simulation.simul.space_object_exists(self.FleetCommanderID):
            self.FleetCommander = None
            if len(self.FleetMembers.keys()) > 0:
                self.FleetCommander = list(self.FleetMembers.values())[0]
                self.FleetCommanderID = self.FleetCommander.ObjectID

        if simulation.simul.space_object_exists(self.FleetCommanderID):
            if self.FleetCommanderID not in self.FleetMembers.keys():
                self.FleetCommander = None
                if len(self.FleetMembers.keys()) > 0:
                    self.FleetCommander = list(self.FleetMembers.values())[0]
                    self.FleetCommanderID = self.FleetCommander.ObjectID

    def checkFleetMembers(self):
        if len(self.FleetMembers.keys()) == 0:
            commanderkillList.append(id(self))
        removeList = []
        for memberID in self.FleetMembers.keys():
            if not simulation.simul.space_object_exists(memberID):
                removeList.append(memberID)
        for memberID in removeList:
            self.FleetMembers.pop(memberID)

    def AITickMonitors(self):
        self.checkFleetMembers()
        self.checkFleetCommander()
        self.ExecuteOrders()

    def ExecuteOrders(self):
        task = self.Orders.get("Fleet Task")
        order = ordersDatabase.get(task)
        position = 0
        removeList = []
        for memberID, memberObj in self.FleetMembers.items():
            if simulation.simul.space_object_exists(memberID):
                NPC_AI.EvasiveBehaviours.CheckEvasion(memberObj)
                if memberObj.ObjectData.get("evasion", 0):
                    removeList.append(memberID)
                elif memberID == self.FleetCommanderID:
                    order(memberObj, self.Orders)
                else:
                    params = self.Orders.get("Parameters")
                    task = params.get("Support Elements")
                    order = ordersDatabase.get(task)
                    position += 1
                    order(memberObj, self.Orders, position=position, formation="LeftE", commander=self.FleetCommander, members=self.FleetMembers)
            else:
                removeList.append(memberID)
        for memberID in removeList:
            self.FleetMembers.pop(memberID)


class AIFighterCommander(AIGroupCommander):
    def __init__(self, FleetCommander, FleetMembers, FleetSize):
        super().__init__(FleetCommander, FleetMembers, FleetSize)
        self.Orders = copy.deepcopy(fleetOrders.fighterOrders)
        self.FighterState = "Docked"
        self.RTBTimer = sbs.app_minutes()
        self.RefitTimer = sbs.app_minutes()

    def AITickMonitors(self):
        if self.FighterState == "Deployed":
            self.checkFleetCommander()
            self.checkFleetMembers()
            if self.RTBTimer > sbs.app_minutes():
                self.ExecuteOrders()
            else:
                self.Orders.update({"Fleet Task": "RTB"})
                params = self.Orders.get("Parameters")
                params.update({"Support Elements": "RTB"})
                self.FighterState = "Returning"
        elif self.FighterState == "Returning":
            self.checkFleetCommander()
            self.checkFleetMembers()
            self.ExecuteOrders()

    def ExecuteOrders(self):
        task = self.Orders.get("Fleet Task")
        order = ordersDatabase.get(task)
        position = 0
        removeList = []
        for memberID, memberObj in self.FleetMembers.items():
            if simulation.simul.space_object_exists(memberID):
                NPC_AI.CarrierBehaviours.CheckFighterEvasion(memberObj)
                if memberObj.ObjectData.get("evasion", 0):
                    NPC_AI.CarrierBehaviours.RTB(memberObj, self.Orders)
                elif memberID == self.FleetCommanderID:
                    order(memberObj, self.Orders)
                else:
                    params = self.Orders.get("Parameters")
                    task = params.get("Support Elements")
                    order = ordersDatabase.get(task)
                    position += 1
                    order(memberObj, self.Orders, position=position, formation="v", commander=self.FleetCommander, members=self.FleetMembers)
            elif not sbs.in_standby_list_id(memberID):
                removeList.append(memberID)
        for memberID in removeList:
            print(memberID)
            self.FleetMembers.pop(memberID)

    def checkFleetMembers(self):
        if len(self.FleetMembers.keys()) == 0:
            commanderkillList.append(id(self))
        removeList = []
        for memberID in self.FleetMembers.keys():
            if not simulation.simul.space_object_exists(memberID):
                if not sbs.in_standby_list_id(memberID):
                    removeList.append(memberID)

        for memberID in removeList:
            self.FleetMembers.pop(memberID)

        if all(sbs.in_standby_list_id(member) for member in self.FleetMembers.keys()) and self.FighterState != "Docked":
            self.FighterState = "Docked"
            self.RefitTimer = sbs.app_minutes() + 1
            print("Docked")
