import xml.etree.ElementTree as ET
from datetime import datetime


class PetriNet:
    def __init__(self):
        self.place_list = []
        self.edge_list = []
        self.transition_list = []
        self.fire_transition_list = []
        self.marking_list = []
        self.marked_list = []
        self.transition_name_list = []
        self.latest_marked = -1
        self.transition_dict = {}
        self.edge_dict = {}
        self.fire_transitions = 0
        self.latest_transition = -1
        self.latest_transition_name = ''
        self.marking = 0
        self.edge_count = 0

    def add_place(self, name):
        self.place_list.append(name)

    def add_transition(self, name):
        self.transition_name_list.append(name)
        self.transition_dict[name] = len(self.transition_name_list) - 1
        self.transition_list.append(len(self.transition_name_list) - 1)

    def add_edge(self, source, target):
        source_list = list(self.edge_dict.get(source, []))
        source_list.append(target)
        self.edge_dict[source] = tuple(source_list)

    def get_tokens(self, place):
        token_list = []
        if place in self.marked_list:
            return len(self.marked_list[:self.marked_list.index(place)])
        else:
            for i in self.marked_list:
                if i < place:
                    token_list.append(i)
            return len(token_list)

    def is_enabled(self, transition):
        self.edge_count += 1
        if self.marking == 0 and self.fire_transitions == 0:
            return transition == 0
        if self.marking == 1:
            return transition in self.edge_dict.get(self.latest_marked, [])
        if self.fire_transitions == 1:
            return transition in self.fire_transition_list

    def add_marking(self, place):
        self.marking = 1
        self.fire_transitions = 0
        self.marked_list.append(place)
        self.latest_marked = place

    def fire_transition(self, transition):
        self.fire_transition_list = []
        self.fire_transitions = 1
        self.marking = 0
        self.latest_transition = transition
        if self.edge_dict.get(transition) is not None:
            fire_source_list = list(self.edge_dict[transition])
            for i in fire_source_list:
                if i in self.transition_list:
                    self.fire_transition_list.append(i)
                elif self.edge_dict.get(i) is not None:
                    fire_source_list1 = list(self.edge_dict[i])
                    for j in fire_source_list1:
                        if j in self.transition_list:
                            self.fire_transition_list.append(j)

    def transition_name_to_id(self, transition_name):
        self.latest_transition_name = transition_name
        return self.transition_dict.get(transition_name, -1)


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


petri_net = PetriNet()


def alpha(log):
    # Initialize the Petri Net and transition log dictionary
    petri_net = PetriNet()
    transition_log_dict = {}
    tasks_dict = {}

    # Extract the activity logs and build the transition log dictionary
    for activity, log_list in log.items():
        for entry in log_list:
            activity_name = entry['concept:name']
            if activity_name not in transition_log_dict:
                transition_log_dict[activity_name] = 0
                petri_net.add_transition(activity_name)

    # Prepare a list of cases for building the causal matrix
    case_list = [list(entry['concept:name'] for entry in log[key]) for key in log]

    # Build the causal matrix and add edges to the Petri Net
    for case in case_list:
        for i in range(len(case) - 1):
            current_task = case[i]
            next_task = case[i + 1]

            if current_task in tasks_dict:
                sub_task_dict = tasks_dict[current_task]
                if next_task in sub_task_dict:
                    sub_task_dict[next_task] += 1
                else:
                    sub_task_dict[next_task] = 1
            else:
                sub_task_dict = {next_task: 1}

            tasks_dict[current_task] = sub_task_dict
            petri_net.add_edge(petri_net.transition_name_list.index(current_task),
                               petri_net.transition_name_list.index(next_task))

    return petri_net


# mined_model = alpha(read_from_file("extension-log.xes"))
#
#
# def check_enabled(pn):
#     ts = ["record issue", "inspection", "intervention authorization", "action not required", "work mandate",
#           "no concession", "work completion", "issue completion"]
#     for t in ts:
#         print(pn.is_enabled(pn.transition_name_to_id(t)))
#     print("")
#
#
# trace = ["record issue", "inspection", "intervention authorization", "work mandate", "work completion",
#          "issue completion"]
# for a in trace:
#     check_enabled(mined_model)
#     mined_model.fire_transition(mined_model.transition_name_to_id(a))
