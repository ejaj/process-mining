class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.tokens = []

    def add_place(self, name):
        self.places[name] = 0
        # print(self.places)

    def add_transition(self, name, id):
        self.transitions[id] = {
            'name': name,
            'pre': [],
            'post': [],
        }
        # print(self.transitions)

    def add_edge(self, source, target):
        if source in self.transitions and target in self.transitions:
            self.transitions[target]['pre'].append(source)
            self.transitions[source]['post'].append(target)
        # print(source, target)
        # if source < 0:
        #     self.transitions[source]['post'].append(target)
        # elif target < 0:
        #     self.transitions[target]['pre'].append(source)
        # print("AD", self.transitions)
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
                self.tokens.remove(pre)
            for post in transition_obj['post']:
                self.tokens.append(post)
            return True
        else:
            return False

    def transition_name_to_id(self, name):
        for id, transition in self.transitions.items():
            if transition['name'] == name:
                return id
