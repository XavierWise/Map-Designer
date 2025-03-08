import random
import sbs


def AddAsteroid(sim, type, position, **kwargs):
    asteroidID = sim.create_space_object("behav_asteroid", type, 1)
    asteroid = sim.get_space_object(asteroidID)
    asteroiddata = asteroid.data_set
    asteroiddata.set("name_tag", "Asteroid", 0)
    sim.reposition_space_object(asteroid, position[0], position[1], position[2])
    if "offset" in kwargs:
        offset = kwargs.get("offset")
        sim.reposition_space_object(asteroid, position[0] + offset[0], position[1], position[2] + offset[2])
    if "data" in kwargs:
        data = kwargs.get("data")
        asteroiddata = asteroid.data_set
        for key, value in data.items():
            asteroiddata.set(key, value, 0)
    return asteroidID


def AddNebula(sim, name, position, **kwargs):
    nebulaID = sim.create_space_object("behav_nebula", name, 1)
    nebula = sim.get_space_object(nebulaID)
    nebuladata = nebula.data_set
    nebuladata.set("name_tag", "Nebula", 0)
    sim.reposition_space_object(nebula, position[0], position[1], position[2])
    if "offset" in kwargs:
        offset = kwargs.get("offset")
        sim.reposition_space_object(nebula, position[0] + offset[0], position[1], position[2] + offset[2])
    return nebulaID


def AddBlackHole(sim, name, position, **kwargs):
    blackholeID = sim.create_space_object("behav_maelstrom", "blackhole", 1)
    blackhole = sim.get_space_object(blackholeID)
    blackhole.steer_roll = 5
    sim.reposition_space_object(blackhole, position[0], position[1], position[2])
    blackhole.exclusion_radius = 100  # event horizon
    blackhole.side = "maelstrom"
    blob = blackhole.data_set
    blob.set("gravity_radius", 100, 0)
    blob.set("gravity_strength", 1, 0)
    blob.set("turbulence_strength", 1, 0)
    blob.set("collision_damage", 10, 0)
    return blackholeID


def AddMine(sim, name, position, **kwargs):
    damage = 10
    if kwargs.get("damage"):
        damage = kwargs.get("damage")
    mineID = sim.create_space_object("behav_mine", "alien_small_1a", 1)
    mine = sim.get_space_object(mineID)
    sim.reposition_space_object(mine, position[0], position[1], position[2])
    blob = mine.data_set
    blob.set("damage_done", damage, 0)
    blob.set("blast_radius", 3000, 0)
    blob.set("local_scale_coeff", 0.5, 0)
    mine.blink_state = 2
    return mineID


class HiddenMinefield:
    def __init__(self, sim, position, height, width, density):
        self.pos = position
        self.sim = sim
        self.dens = density
        self.width = width
        self.height = height
        self.targets = {}
        self.ID = id(self)

    def trackArea(self):
        killlist = []
        #check all the ships in the area
        for ship, time in self.targets.items():
            if ship in sbs.broad_test(self.pos[0]-self.width, self.pos[2]-self.height, self.pos[0]+self.width, self.pos[2] + self.height, 0xfff0):
                #if it is still there, calculate whether it should be hit yet.
                if time < sbs.app_seconds() and ship.cur_speed > 0:
                    probability = random.randint(0, 100)
                    if probability < 30:
                        AddMine(self.sim, "mine", (ship.pos.x, ship.pos.y, ship.pos.z), damage=8)
                        self.targets.update({ship: sbs.app_seconds() + 30})
            else:
                #if it isn't in the area any more, remove it
                killlist.append(ship)

        for ship in killlist:
            self.targets.pop(ship)

        #now check if there are any other ships to add, or whether the target needs updating with a new time
        for ping in sbs.broad_test(self.pos[0]-self.width, self.pos[1]-self.height, self.pos[0]+self.width, self.pos[1] + self.height, 0xfff0):
            if ping.tick_type == "behav_playership":
                if ping in self.targets.keys():
                    time = self.targets.get(ping)
                    if time < sbs.app_seconds():
                        self.targets.update({ping: sbs.app_seconds() + 30})
                else:
                    self.targets.update({ping: sbs.app_seconds() + 30})
