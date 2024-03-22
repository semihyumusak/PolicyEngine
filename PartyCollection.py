from Constraint import Constraint


class PartyCollection:
    def __init__(self, identifier, refinement=None):
        """
        Initializes a PartyCollection instance.

        :param identifier: A string or an object representing the collection of parties. If an object, it should have a 'source' attribute.
        :param refinement: Optional; a list of Constraint objects that refine the conditions of the party collection.
        """
        self.identifier = identifier
        self.refinement = refinement if refinement is not None else []

    def add_refinement(self, refinement):
        """
        Adds a refinement (constraint) to the party collection.

        :param refinement: A Constraint object to be added as a refinement.
        """
        self.refinement.append(refinement)

    def __str__(self):
        if isinstance(self.identifier, str):
            identifier_str = self.identifier
        else:  # Assuming the object has a 'source' attribute
            identifier_str = getattr(self.identifier, 'source', 'Unknown source')

        refinements_str = ", ".join(str(refinement) for refinement in self.refinement)
        return f"PartyCollection(Identifier: {identifier_str}, Refinements: [{refinements_str}])"


if __name__ == '__main__':
    # Example usage:
    # Assuming the Constraint class is defined as previously discussed

    # Simple party collection example
    simple_party_collection = PartyCollection("SimplePartyCollection")
    print(simple_party_collection)

    # Complex party collection example with a source attribute and refinements
    class ComplexPartySource:
        def __init__(self, source):
            self.source = source

    complex_source = ComplexPartySource("ComplexPartySource")
    constraint1 = Constraint('eq', leftOperand='role', reference="Contributor")
    complex_party_collection = PartyCollection(complex_source, refinement=[constraint1])
    print(complex_party_collection)

    # Adding a new refinement to the complex party collection
    constraint2 = Constraint('neq', leftOperand='status', reference="Inactive")
    complex_party_collection.add_refinement(constraint2)
    print(complex_party_collection)
