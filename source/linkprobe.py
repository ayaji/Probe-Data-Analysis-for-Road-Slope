import math

class GeoPoint():
    def __init__(self, latlong):
        self.ID = latlong
        split_attrs = latlong.split("/")
        self.long, self.lat = map(float, (split_attrs[0], split_attrs[1]))

class Probe(object):
    def __init__(self, line):

        self.sampleID, self.dateTime, self.sourceCode, self.latitude, self.longitude, self.altitude, self.speed, self.heading = line.strip().split(',')
        self.direction = ""
        self.linkID = None
        self.distFromRef = None
        self.distFromLink = None
        self.slope = None

    def getDirection(self, X, Y):
        if (math.cos(X) * math.cos(Y) + math.sin(X) * math.sin(Y)) > 0:
            self.direction = "F"
        else:
            self.direction = "T"

    def toString(self):
        return '{}, {}, {}, {}, {}, {}, {}, {}, {}, {} ,{}, {}\n'.format(self.sampleID, self.dateTime, self.sourceCode, self.latitude, self.longitude, self.altitude, self.speed, self.heading, self.linkID, self.direction, self.distFromRef, self.distFromRef)

class MatchedProbe(object):
    def __init__(self, line):
        self.sampleID, self.dateTime, self.sourceCode, self.latitude, self.longitude, \
        self.altitude, self.speed, self.heading, self.linkID, self.direction, \
        self.distFromRef, self.distFromLink = line.split(',')
        self.elevation = None
        self.slope = None

    def toString(self):
        return '{}, {}, {}, {}, {}, {}, {}, {}, {}, {} ,{}, {}, {}\n'.format(self.sampleID, self.dateTime, self.sourceCode, self.latitude, self.longitude, self.altitude, self.speed, self.heading, self.linkID, self.direction, self.distFromRef, self.distFromRef, self.slope)


class Link(object):
    def __init__(self, line):
        self.linkID, self.refNodeID, self.nrefNodeID, self.length, self.functionalClass, self.directionOfTravel, self.speedCategory, self.fromRefSpeedLimit, self.toRefSpeedLimit, self.fromRefNumLanes, self.toRefNumLanes, self.multiDigitized, self.urban, self.timeZone, self.shapeInfo, self.curvatureInfo, self.slopeInfo = line.strip().split(
            ',')
        self.ReferenceNodeLat, self.ReferenceNodeLong, _ = self.shapeInfo.split('|')[0].split('/')
        self.ReferenceNode = map(float, (self.ReferenceNodeLat, self.ReferenceNodeLong))
        self.ProbePoints = []

class LinkNode():
    def __init__(self, ID, spoint, epoint):
        self.id = ID
        self.rpoint, self.nrpoint = GeoPoint(spoint), GeoPoint(epoint)
        self.vlong, self.vlat = self.nrpoint.long - self.rpoint.long, self.nrpoint.lat - self.rpoint.lat
        self.length = math.sqrt(self.vlong ** 2 + self.vlat ** 2)
        if self.vlat != 0:
            self.radian = math.atan(self.vlong / self.vlat)
        elif self.vlong > 0:
            self.radian = math.pi / 2
        else:
            self.radian = math.pi * 3 / 2

    def calculateDistance(self, point):
        tlong, tlat = point.long - self.rpoint.long, point.lat - self.rpoint.lat
        dist_point_refnode = (tlong ** 2) + (tlat ** 2)
        proj = (tlong * self.vlong + tlat * self.vlat) / self.length

        if proj < 0:
           return dist_point_refnode

        proj_square = proj ** 2

        if proj_square > self.length ** 2:
            return (point.long - self.nrpoint.long) ** 2 + (point.lat - self.nrpoint.lat) ** 2

        return (tlong**2 + tlat**2) - proj**2

    def calculateDistanceFromLink(self, point):
        tlong, tlat = point.long - self.rpoint.long, point.lat - self.rpoint.lat
        return math.sqrt(tlong**2 + tlat**2)