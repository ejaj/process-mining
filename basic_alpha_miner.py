def alpha_miner(event_log):
    direct_succession = {}
    causality = {}
    parallel = {}
    choice = {}

    # Step 1: Construct Direct Succession relations (x > y)
    for trace in event_log:
        for i in range(len(trace) - 1):
            x, y = trace[i], trace[i + 1]
            if x in direct_succession:
                direct_succession[x].add(y)
            else:
                direct_succession[x] = {y}

    # Step 2: Construct Causality relations (x → y)
    for x, y_set in direct_succession.items():
        causality[x] = set()
        for y in y_set:
            if x not in direct_succession.get(y, set()):
                causality[x].add(y)

    # Step 3: Construct Parallel relations (x || y)
    for x, y_set in direct_succession.items():
        parallel[x] = set()
        for y in y_set:
            if x in direct_succession.get(y, set()) and y in direct_succession[x]:
                parallel[x].add(y)

    # Step 4: Construct Choice relations (x # y)
    activities = set(activity for trace in event_log for activity in trace)
    for x in activities:
        for y in activities:
            if x != y and x not in direct_succession.get(y, set()) and y not in direct_succession.get(x, set()):
                choice[x] = choice.get(x, set())
                choice[x].add(y)

    return direct_succession, causality, parallel, choice


def construct_footprint_matrix(direct_succession, causality, parallel, choice):
    activities = set(direct_succession.keys())

    # Initialize an empty footprint matrix
    footprint_matrix = {}

    for x in activities:
        footprint_matrix[x] = {}
        for y in activities:
            if x == y:
                # No relation with itself
                footprint_matrix[x][y] = None
            elif y in causality.get(x, set()):
                # Causality relation (x -> y)
                footprint_matrix[x][y] = "->"
            elif x in direct_succession.get(y, set()) and y not in direct_succession.get(x, set()):
                # Direct succession relation (x > y)
                footprint_matrix[x][y] = ">"
            elif x in parallel.get(y, set()):
                # Parallel relation (x || y)
                footprint_matrix[x][y] = "||"
            elif x in choice.get(y, set()):
                # Choice relation (x # y)
                footprint_matrix[x][y] = "#"

    return footprint_matrix


def discover_places(footprint_matrix):
    places = {}
    activities = list(footprint_matrix.keys())

    for x in activities:
        for y in activities:
            if x != y and footprint_matrix[x][y] == "#":
                places[(x, y)] = {
                    'input': {x},
                    'output': {y}
                }

    # Include activities that are not directly involved in choice relations
    for x in activities:
        if all(footprint_matrix[x][y] is None or footprint_matrix[x][y] != "#" for y in activities):
            places[(x, x)] = {
                'input': {x},
                'output': {x}
            }

    return places


event_log = [
    ["A", "B", "C", "D"],
    ["A", "C", "B", "D"],
    ["A", "E", "D"],
]

direct_succession, causality, parallel, choice = alpha_miner(event_log)
footprint_matrix = construct_footprint_matrix(direct_succession, causality, parallel, choice)
# print("Footprint Matrix:")
# for x in footprint_matrix:
#     print(x, footprint_matrix[x])
places = discover_places(footprint_matrix)
for place, tasks in places.items():
    print(f"Place: {place}, Input Tasks: {tasks['input']}, Output Tasks: {tasks['output']}")

# print("Direct Succession Relations:")
# for x, y_set in direct_succession.items():
#     for y in y_set:
#         print(f"{x} > {y}")
#
# print("\nCausality Relations:")
# for x, y_set in causality.items():
#     for y in y_set:
#         print(f"{x} -> {y}")
#
# print("\nParallel Relations:")
# for x, y_set in parallel.items():
#     for y in y_set:
#         print(f"{x} || {y}")
#
# print("\nChoice Relations:")
# for x, y_set in choice.items():
#     for y in y_set:
#         print(f"{x} # {y}")
