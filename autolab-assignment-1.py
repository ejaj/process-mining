class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.tokens = []

    def add_place(self, name):
        self.places[name] = 0
        print('place', self.places)

    def add_transition(self, name, id):
        self.transitions[id] = {
            'name': name,
            'pre': [],
            'post': [],
        }
        print('Tr', self.transitions)

    def add_edge(self, source, target):
        if source < 0:
            self.transitions[source]['post'].append(target)
        elif target < 0:
            self.transitions[target]['pre'].append(source)
        print('Edge', self.transitions)
        return self

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
                self.places[pre] -= 1
                self.tokens.remove(pre)
            for post in transition_obj['post']:
                self.places[post] += 1
                self.tokens.append(post)
            return True
        else:
            return False


p = PetriNet()

p.add_place(1)  # add place with id 1
p.add_place(2)
p.add_place(3)
p.add_place(4)
p.add_transition("A", -1)
p.add_transition("B", -2)
p.add_transition("C", -3)
p.add_transition("D", -4)

p.add_edge(1, -1)
p.add_edge(-1, 2)
p.add_edge(2, -2).add_edge(-2, 3)
p.add_edge(2, -3).add_edge(-3, 3)
p.add_edge(3, -4)
p.add_edge(-4, 4)

print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.add_marking(1)  # add one token to place id 1
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-1)  # fire transition A
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-3)  # fire transition C
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-4)  # fire transition D
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.add_marking(2)  # add one token to place id 2
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-2)  # fire transition B
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

p.fire_transition(-4)  # fire transition D
print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

# by the end of the execution there should be 2 tokens on the final place
print(p.get_tokens(4))
