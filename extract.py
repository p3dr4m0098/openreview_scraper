class Extractor:
    def __init__(self, fields, subfields, include_subfield=False):
        self.fields = fields
        self.subfields = subfields
        self.include_subfield = include_subfield

    def __call__(self, paper):
        return self.extract(paper)

    def extract(self, paper):
        trimmed_paper = {}
        for field in self.fields:
            trimmed_paper[field] = getattr(paper, field, None)
        for subfield, fields in self.subfields.items():
            subdict = getattr(paper, subfield, {})
            if self.include_subfield:
                trimmed_paper[subfield] = {}
            for field in fields:
                field_value = subdict.get(field, None)
                if self.include_subfield:
                    trimmed_paper[subfield][field] = field_value
                else:
                    trimmed_paper[field] = field_value
        return trimmed_paper
