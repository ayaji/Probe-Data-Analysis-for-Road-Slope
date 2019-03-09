from linkprobe import Link, MatchedProbe
import math

linkData = "Partition6467LinkData.csv"
matchedData = "results/MatchedDataPoints.csv"
slopeData = "results/SlopesCalculation.csv"
evaluationData = "results/EvaluatedRoadSlope.csv"

AVG_EARTH_RADIUS = 6367

def findSlope():
    link_data = []
    file_line_count = 0

    # Reading link file
    with open(linkData) as street_data:
        for line in street_data:
            link_data.append(Link(line))

    # Reading matched probe data
    with open(matchedData) as matched_data:
        result_data = open(slopeData, 'w')

        prev_probe = None
        print("Calculating slope for each mapped probe point")

        for line in matched_data:
            matched_probe = MatchedProbe(line)

            if not prev_probe or matched_probe.linkID != prev_probe.linkID:
                matched_probe.slope = ''
            else:
                try:
                    # Calculating slope
                    start, end = list(map(float, [matched_probe.longitude, matched_probe.latitude])), list(map(float, [prev_probe.longitude, prev_probe.latitude]))

                    long1, latt1, long2, latt2 = list(map(math.radians, [start[0], start[1], end[0], end[1]]))
                    distance_long, distance_lat = long2 - long1, latt2 - latt1
                    a = math.sin(distance_lat / 2) ** 2 + math.cos(latt1) * math.cos(latt2) * math.sin(
                        distance_long / 2) ** 2
                    hyp = AVG_EARTH_RADIUS * 2 * math.asin(math.sqrt(a))

                    opp = float(matched_probe.altitude) - float(prev_probe.altitude)
                    matched_probe.slope = (2 * math.pi * math.atan(opp / hyp)) / 360

                except ZeroDivisionError:
                    matched_probe.slope = 0.0

                # check for matching linkID
                for link in link_data:
                    if matched_probe.linkID == link.linkID and link.slopeInfo != '':
                        link.ProbePoints.append(matched_probe)
                        break

            # Increment line number
            file_line_count += 1
            result_data.write(matched_probe.toString())

            if file_line_count % 500 == 0:
                print(" Calculated slope : {}".format(file_line_count))
                break

            prev_probe = matched_probe
        result_data.close()

    return link_data

def slope_evaluation(link_data):
    print("Evaluating Slope: ")
    evaluation_data = open(evaluationData, 'a')
    evaluation_data.write('linkID,  Given Slope, Calculated Slope' + "\n")

    for link in link_data:
        # check for link has matched point
        if len(link.ProbePoints) > 0:
            sum_given_slope = 0.0

            # Calculating the mean of given slope info for the link
            givenSlope = link.slopeInfo.strip().split('|')
            for gslope in givenSlope:
                sum_given_slope += float(gslope.strip().split('/')[1])

            given_slope = sum_given_slope / len(givenSlope)
            sum_calculated_slope, non_zero_probe_count = 0.0, 0

            # Calculating the mean of calculated slope info for the link
            for probe in link.ProbePoints:
                if probe.direction == "T":
                    probe.slope = -probe.slope

                if probe.slope != '' and probe.slope != 0:
                    sum_calculated_slope += probe.slope
                    non_zero_probe_count += 1

            calculated_slope = sum_calculated_slope / non_zero_probe_count if non_zero_probe_count != 0 else 0
            evaluation_data.write('{}, {}, {}\n'.format(link.linkID, given_slope, calculated_slope))

    evaluation_data.close()
    print("End Evaluating Slope: ")

if __name__ == '__main__':
    link_data = findSlope()
    slope_evaluation(link_data)