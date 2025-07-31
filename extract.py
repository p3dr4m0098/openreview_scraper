class Extractor:
    def __init__(self, fields, subfields, include_subfield=False):
        self.fields = fields
        self.subfields = subfields
        self.include_subfield = include_subfield

    def __call__(self, paper):
        return self.extract(paper)

    def _unwrap_value(self, value):
        # Unwrap {"value": ...} dicts recursively
        if isinstance(value, dict) and set(value.keys()) == {"value"}:
            return self._unwrap_value(value["value"])
        return value

    def extract(self, paper):
        trimmed_paper = {}
        for field in self.fields:
            raw_value = getattr(paper, field, None)
            trimmed_paper[field] = self._unwrap_value(raw_value)
        for subfield, fields in self.subfields.items():
            subdict = getattr(paper, subfield, {})
            if self.include_subfield:
                trimmed_paper[subfield] = {}
            for field in fields:
                field_value = subdict.get(field, None)
                unwrapped_value = self._unwrap_value(field_value)
                if self.include_subfield:
                    trimmed_paper[subfield][field] = unwrapped_value
                else:
                    trimmed_paper[field] = unwrapped_value
        return trimmed_paper
