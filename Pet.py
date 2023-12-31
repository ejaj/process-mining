import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime


class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = []
        self.tokens = []

    def add_place(self, name):
        self.places[name] = 0
        # print(self.places)

    def add_transition(self, name):
        self.transitions[name] = name

    def add_edge(self, source, target):
        if source < 0:
            self.transitions[source]['post'].append(target)
        elif target < 0:
            self.transitions[target]['pre'].append(source)
        # print("after")
        # print(self.transitions)
        return self

    def get_tokens(self, place):
        return self.places.get(place, 0)

    def is_enabled(self, transition):
        # print(self.transitions)
        if transition in self.transitions:
            transition_obj = self.transitions[transition]
            for pre in transition_obj['pre']:
                if pre not in self.tokens:
                    return False
            return True
        return False

    def add_marking(self, place):
        if place in self.places:
            self.places[place] += 1
            self.tokens.append(place)

    def fire_transition(self, transition):
        if self.is_enabled(transition):
            transition_obj = self.transitions[transition]
            for pre in transition_obj['pre']:
                self.places[pre] -= 1
                self.tokens.remove(pre)
            for post in transition_obj['post']:
                self.places[post] += 1
                self.tokens.append(post)
            return True
        else:
            return False

    def transition_name_to_id(self, name):
        for id, transition in self.transitions.items():
            if transition['name'] == name:
                return id
        raise ValueError(f"Transition '{name}' not found in the Petri net.")


def read_from_file(filename):
    try:
        tree = ET.parse(filename)
        root = tree.getroot()

        namespaces = {
            'xes': 'http://www.xes-standard.org/',
            'org': 'http://www.xes-standard.org/org.xesext',
            'time': 'http://www.xes-standard.org/time.xesext',
            'lifecycle': 'http://www.xes-standard.org/lifecycle.xesext',
            'concept': 'http://www.xes-standard.org/concept.xesext'
        }
        event_dict = {}
        for trace in root.findall('.//xes:trace', namespaces):
            case_id = None
            events = []
            # Extract case_id from trace
            case_id_element = trace.find('./xes:string[@key="concept:name"]', namespaces)
            if case_id_element is not None:
                case_id = case_id_element.get('value')
            for event_elem in trace.findall('.//xes:event', namespaces):
                event_data = {}
                for attr_elem in event_elem.findall('./*'):
                    key = attr_elem.get('key')
                    value = attr_elem.get('value')
                    event_data[key] = value

                if 'time:timestamp' in event_data:
                    timestamp_str = event_data['time:timestamp']
                    timestamp_tz = datetime.fromisoformat(timestamp_str)
                    event_data['time:timestamp'] = timestamp_tz.replace(tzinfo=None)
                if 'cost' in event_data:
                    event_data['cost'] = int(event_data['cost'])
                if "urgency" in event_data:
                    event_data['cost'] = int(event_data['urgency'])

                events.append(event_data)
            if case_id:
                event_dict[case_id] = events
        return event_dict
    except ET.ParseError as e:
        print(f"Error parsing the XES file: {e}")
        return None


def construct_relation(event_log):
    direct_succession = {}
    causality = {}
    parallel = {}
    choice = {}

    unique_values = set()

    for event in event_log:
        for value in event:
            unique_values.add(value)

    # Step 1: Construct Direct Succession relations (x > y)
    for trace in event_log:
        for i in range(len(trace) - 1):
            x, y = trace[i], trace[i + 1]
            if x in direct_succession:
                direct_succession[x].add(y)
            else:
                direct_succession[x] = {y}
    # print("dir", direct_succession)

    # Step 2: Construct Causality relations (x → y)
    for x, y_set in direct_succession.items():
        causality[x] = set()
        for y in y_set:
            if x not in direct_succession.get(y, set()):
                causality[x].add(y)
    # print("c", causality)
    # Step 3: Construct Parallel relations (x || y)
    for x, y_set in direct_succession.items():
        parallel[x] = set()
        for y in y_set:
            if x in direct_succession.get(y, set()) and y in direct_succession[x]:
                parallel[x].add(y)
    # print(parallel)
    # Step 4: Construct Choice relations (x # y)
    activities = set(activity for trace in event_log for activity in trace)
    for x in activities:
        choice[x] = {x}
        for y in activities:
            if x != y and x not in direct_succession.get(y, set()) and y not in direct_succession.get(x, set()):
                choice[x].add(y)
    choice_result = {k: v for k, v in choice.items() if v}
    # print(choice_result)
    return unique_values, direct_succession, causality, parallel, choice_result


def construct_footprint_matrix(unique_values, causality, parallel, choice):
    footprint_matrix = {}
    for x in unique_values:
        footprint_matrix[x] = {}
        for y in unique_values:
            if x == y:
                # No relation with itself
                footprint_matrix[x][y] = "#"
            elif y in causality.get(x, set()):
                # Causality relation (x -> y)
                footprint_matrix[x][y] = "->"
            elif x in parallel.get(y, set()):
                # Parallel relation (x || y)
                footprint_matrix[x][y] = "||"
            elif x in choice.get(y, set()):
                # Choice relation (x # y)
                footprint_matrix[x][y] = "#"
    return footprint_matrix


def check_relation(choice_pars, key, col):
    check = False
    check1 = False
    for choice_key, choice_values in choice_pars.items():
        if choice_key == key:
            for i in choice_values:
                if i == choice_key:
                    check = True

        if choice_key == col:
            for j in choice_values:
                if j == choice_key:
                    check1 = True
    if check and check1:
        return True
    else:
        return False


def discover_places(footprint_matrix, choice_dic):
    places = {}
    count_place = 0
    for col, col_value in footprint_matrix.items():
        # print(col, col_value)
        places[col] = set()
        for key, value in col_value.items():
            # print(key, value)
            if value == "->":
                # print(col, key)
                # fun(key, col)
                if check_relation(choice_dic, col, key):
                    # print("dd")
                    count_place += 1
                    places[col].add(key)
    return places, count_place


def alpha(event_log_dddd):

    activities = []
    for case in event_log_dddd.values():
        sub_activities = []
        for event in case:
            sub_activities.append(event['concept:name'])
        activities.append(sub_activities)

    # transition_log_list = {}
    # petri_net = PetriNet()



mined_model = alpha(read_from_file("extension-log.xes"))
