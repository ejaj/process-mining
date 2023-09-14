class PetriNet:

    def __init__(self):
        """
        Initializes an empty Petri Net.

        The Petri Net consists of places, transitions, and edges between them.
        """
        self.places = {}
        self.transitions = {}
        self.edges = {}

    def add_place(self, name):
        """
        Add a place to the Petri Net.

        Args:
            name (str or int): The name of the place to add.
        """
        self.places[name] = 0

    def add_transition(self, name, id):
        """
        Add a transition to the Petri Net.

        Args:
            name (str or int): The name of the transition to add.
            id (str or int): The unique identifier for the transition.
        """
        self.transitions[id] = name

    def add_edge(self, source, target):
        """
        Add an edge between a source place and a target place in the Petri Net.

        Args:
            source (str or int): The name of the source place.
            target (str or int): The name of the target place.
        """
        if source in self.edges:
            self.edges[source].append(target)
        else:
            self.edges[source] = [target]
        return self

    def get_tokens(self, place):
        """
        Get the number of tokens in a specified place.

        Args:
            place (str or int): The name of the place to query.

        Returns:
            int: The number of tokens in the specified place.
        """
        return self.places.get(place, 0)

    def is_enabled(self, transition):
        """
        Check if a transition is enabled for firing.

        A transition is enabled if all its input places have at least one token.

        Args:
            transition (str or ing): The name of the transition to check.

        Returns:
            bool: True if the transition is enabled, False otherwise.
        """
        if transition in self.transitions:
            transition_places = []
            for source, targets in self.edges.items():
                if transition in targets:
                    transition_places.append(source)
            for place in transition_places:
                if self.places.get(place, 0) >= 1:
                    return True
        return False

    def add_marking(self, place):
        """
        Add a token to a specified place.

        Args:
            place (str or int): The name of the place to add a token to.
        """
        if place in self.places:
            self.places[place] += 1

    def fire_transition(self, transition):
        """
        Fire a specified transition by moving tokens from input places to output places.

        Args:
            transition (str or int): The name of the transition to fire.
        """
        if self.is_enabled(transition):
            transition_places = [source for source, targets in self.edges.items() if transition in targets]

            # Remove tokens from source places
            for place in transition_places:
                if self.places.get(place, 0) >= 1:
                    self.places[place] -= 1

            # Add tokens to target places
            targets = self.edges[transition]
            for target in targets:
                self.places[target] += 1

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
