import xml.etree.ElementTree as ET
from datetime import datetime


def log_as_dictionary(log):
    event_dict = {}
    lines = log.strip().split('\n')
    # print(lines)
    for line in lines:
        elements = line.strip().split(';')
        # print(elements)
        if len(elements) == 4:
            event_type, case_id, user, timestamp = elements
            event = {
                'event_type': event_type,
                'case_id': case_id,
                'user': user,
                'timestamp': timestamp
            }
            if case_id in event_dict:
                event_dict[case_id].append(event)
            else:
                event_dict[case_id] = [event]
    # print(event_dict)
    return event_dict


def dependency_graph_inline(log):
    dependency_graph = {}
    for case_id, events in log.items():
        activities = [event['event_type'] for event in events]
        for i in range(len(activities) - 1):
            source_activity = activities[i]
            target_activity = activities[i + 1]
            if source_activity not in dependency_graph:
                dependency_graph[source_activity] = {}
            if target_activity in dependency_graph[source_activity]:
                dependency_graph[source_activity][target_activity] += 1
            else:
                dependency_graph[source_activity][target_activity] = 1
    return dependency_graph


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


def dependency_graph_file(log):
    dependency_dict = {}
    for case_id, events in log.items():
        for i in range(len(events) - 1):
            source_activity = events[i]["concept:name"]
            target_activity = events[i + 1]["concept:name"]
            if source_activity not in dependency_dict:
                dependency_dict[source_activity] = {}
            if target_activity not in dependency_dict[source_activity]:
                dependency_dict[source_activity][target_activity] = 1
            else:
                dependency_dict[source_activity][target_activity] += 1
    return dependency_dict


f = """
Task_A;case_1;user_1;2019-09-09 17:36:47
Task_B;case_1;user_3;2019-09-11 09:11:13
Task_D;case_1;user_6;2019-09-12 10:00:12
Task_E;case_1;user_7;2019-09-12 18:21:32
Task_F;case_1;user_8;2019-09-13 13:27:41

Task_A;case_2;user_2;2019-09-14 08:56:09
Task_B;case_2;user_3;2019-09-14 09:36:02
Task_D;case_2;user_5;2019-09-15 10:16:40

Task_G;case_1;user_6;2019-09-18 19:14:14
Task_G;case_2;user_6;2019-09-19 15:39:15
Task_H;case_1;user_2;2019-09-19 16:48:16
Task_E;case_2;user_7;2019-09-20 14:39:45
Task_F;case_2;user_8;2019-09-22 09:16:16

Task_A;case_3;user_2;2019-09-25 08:39:24
Task_H;case_2;user_1;2019-09-26 12:19:46
Task_B;case_3;user_4;2019-09-29 10:56:14
Task_C;case_3;user_1;2019-09-30 15:41:22"""
# log_dic = log_as_dictionary(f)
# dg = dependency_graph_inline(log_dic)
# for ai in sorted(dg.keys()):
#     for aj in sorted(dg[ai].keys()):
#         print(ai, '->', aj, ':', dg[ai][aj])

# filename = 'extension-log.xes'
# log = read_from_file(filename)
# for case_id in sorted(log):
#     print((case_id, len(log[case_id])))
#
# case_id = "case_123"
# event_no = 0
# print((log[case_id][event_no]["concept:name"], log[case_id][event_no]["org:resource"],
#        log[case_id][event_no]["time:timestamp"], log[case_id][event_no]["cost"]))
#
# dependency_graph = dependency_graph_file(log)
#
# for source_activity, target_activities in dependency_graph.items():
#     for target_activity, frequency in target_activities.items():
#         print(f"{source_activity} -> {target_activity}: {frequency}")
