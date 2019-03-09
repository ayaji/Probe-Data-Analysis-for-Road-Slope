from collections import defaultdict
from linkprobe import LinkNode, GeoPoint, Probe
import math

AVG_EARTH_RADIUS_MLT = math.pi / 180 * 6371000
points = defaultdict(list)
links = defaultdict(list)

probeData = "Partition6467ProbePoints.csv"
linkData = "Partition6467LinkData.csv"
matchedData = "results/MatchedDataPoints.csv"

def readLinkData():
    # Read and create a dictionary of links for each node of link data
    print("Begin Link Load ")
    for line in open(linkData).readlines():
        attributes = line.strip().split(",")
        nodes = attributes[14].split("|")
        for i in range(len(nodes)-1):
            linkNode = LinkNode(attributes[0], nodes[i], nodes[i+1])
            links[attributes[0]].append(linkNode)
            points[nodes[i]].append(linkNode)
            points[nodes[i + 1]].append(linkNode)
    print("End Link load")

def matchData():
    target = open(matchedData, "w")
    recentID = None
    candidate = []
    # Iterate through the Probe data to match it against links
    for count, line in enumerate(open(probeData).readlines()):
        probe = Probe(line)
        latlong = GeoPoint(probe.latitude + "/" + probe.longitude)

        # Check if the sample ID was scanned earlier
        if probe.sampleID != recentID:
            recentID = probe.sampleID
            # Iterate through each link to match with current probe data
            for key in links.keys():
                for link in links[key]:
                    distance = link.calculateDistance(latlong)
                    if not probe.distFromRef or distance < probe.distFromRef:
                        probe.distFromRef, probe.linkID = distance, link.id
                        probe.distFromLink = links[probe.linkID][0].calculateDistanceFromLink(latlong)
                        probe.getDirection(float(probe.heading), link.radian)
                        candidate = [link.rpoint, link.nrpoint]
        else:
            for candidate_point in candidate:
                for link in points[candidate_point.ID]:
                    distance = link.calculateDistance(latlong)
                    if not probe.distFromRef or distance < probe.distFromRef:
                        probe.distFromRef, probe.linkID = distance, link.id
                        probe.distFromLink = links[probe.linkID][0].calculateDistanceFromLink(latlong)
                        probe.getDirection(float(probe.heading), link.radian)
        probe.distFromRef = math.sqrt(probe.distFromRef) * AVG_EARTH_RADIUS_MLT
        probe.distFromLink = probe.distFromLink * AVG_EARTH_RADIUS_MLT

        # Writing comma separated string into file and display status
        target.write(probe.toString())
        if count % 500 == 0:
            print(" Matching Record : {}".format(count))

    target.close()

if __name__ == '__main__':
    readLinkData()
    matchData()
