class CustomEmbed:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title", "")
        self.description = kwargs.get("description", "")
        self.color = kwargs.get("color", 0xFFFFFF)  # Default color is white
        self.fields = kwargs.get("fields", [])
        self.footer = kwargs.get("footer", {})

    @property
    def _json(self):
        data = {
            "title": self.title,
            "description": self.description,
            "color": self.color
        }
        if self.fields:
            data["fields"] = self.fields
        if self.footer:
            data["footer"] = self.footer
        return data
