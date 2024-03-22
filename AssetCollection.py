from Constraint import Constraint


class AssetCollection:
    def __init__(self, identifier, refinement=None):
        """
        Initializes an AssetCollection instance.

        :param identifier: A string or an object representing the collection. If an object, it should have a 'source' attribute.
        :param refinement: Optional; a list of Constraint objects that refine the conditions of the asset collection.
        """
        self.identifier = identifier
        self.refinement = refinement if refinement is not None else []

    def add_refinement(self, refinement):
        """
        Adds a refinement (constraint) to the asset collection.

        :param refinement: A Constraint object to be added as a refinement.
        """
        self.refinement.append(refinement)

    def __str__(self):
        if isinstance(self.identifier, str):
            identifier_str = self.identifier
        else:  # Assuming the object has a 'source' attribute
            identifier_str = getattr(self.identifier, 'source', 'Unknown source')

        refinements_str = ", ".join(str(refinement) for refinement in self.refinement)
        return f"AssetCollection(Identifier: {identifier_str}, Refinements: [{refinements_str}])"

if __name__ == '__main__':
    # Example usage:
    # Assuming the Constraint class is defined as previously discussed

    # Simple asset collection example
    simple_collection = AssetCollection("SimpleCollection")
    print(simple_collection)

    # Complex asset collection example with a source attribute and refinements
    class ComplexCollectionSource:
        def __init__(self, source):
            self.source = source

    complex_source = ComplexCollectionSource("ComplexCollectionSource")
    constraint1 = Constraint('eq', leftOperand='category', reference="Images")
    complex_collection = AssetCollection(complex_source, refinement=[constraint1])
    print(complex_collection)

    # Adding a new refinement to the complex collection
    constraint2 = Constraint('gteq', leftOperand='size', reference=100)
    complex_collection.add_refinement(constraint2)
    print(complex_collection)
