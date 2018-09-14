from pyjexl.analysis import ValidatingAnalyzer


class ExtractTransformSubjectAnalyzer(ValidatingAnalyzer):
    """
    Extract all subject values of given transforms.

    If no transforms are given all subjects of all transforms will be extracted.
    """

    def __init__(self, config, transforms=[]):
        self.transforms = transforms
        super().__init__(config)

    def visit_Transform(self, transform):
        if not self.transforms or transform.name in self.transforms:
            yield transform.subject.value
        yield from self.generic_visit(transform)
