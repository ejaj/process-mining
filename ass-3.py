from collections import defaultdict
import xml.etree.ElementTree as ET
from datetime import datetime


class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.tokens = []

    def add_place(self, name):
        self.places[name] = 0

    def add_transition(self, name, id):
        self.transitions[id] = {
            'name': name,
            'pre': [],
            'post': [],
        }

    def add_edge(self, source, target):
        if source in self.transitions and target in self.transitions:
            self.transitions[target]['pre'].append(source)
            self.transitions[source]['post'].append(target)
        else:
            raise ValueError("Source or target transition not found in the Petri net.")

    def get_tokens(self, place):
        return self.places.get(place, 0)

    def is_enabled(self, transition):
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
                if pre in self.tokens:
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


def alpha(log):
    print(log)
    petri_net = PetriNet()

    # Step 1: Extract all unique activities from the log
    unique_activities = set()
    for case in log.values():
        for event in case:
            unique_activities.add(event['concept:name'])

    # Step 2: Create transitions for each unique activity
    for activity in unique_activities:
        petri_net.add_transition(activity, activity)

    # Step 3: Add places and edges based on log data
    for case in log.values():
        for i in range(len(case) - 1):
            source = case[i]['concept:name']
            target = case[i + 1]['concept:name']
            petri_net.add_place(source)
            petri_net.add_place(target)
            petri_net.add_edge(source, target)

    return petri_net


mined_model = alpha(read_from_file("extension-log.xes"))


def check_enabled(pn):
    ts = ["record issue", "inspection", "intervention authorization", "action not required", "work mandate",
          "no concession", "work completion", "issue completion"]
    for t in ts:
        print(pn.is_enabled(pn.transition_name_to_id(t)))
    print("")


trace = ["record issue", "inspection", "intervention authorization", "work mandate", "work completion",
         "issue completion"]
for a in trace:
    check_enabled(mined_model)
    mined_model.fire_transition(mined_model.transition_name_to_id(a))
