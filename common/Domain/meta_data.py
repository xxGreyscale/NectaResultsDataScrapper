from datetime import datetime


class Metadata:
    # I want the meta-data to be a dictionary
    def __init__(self, key: str = None, value: str = None, created_at: datetime = None, updated_at: datetime = None):
        self.key = key
        self.value = value
        self.created_at = datetime.now() if created_at is None else created_at
        self.updated_at = datetime.now() if updated_at is None else updated_at

    def __str__(self):
        return f"Metadata: {self.key}, Value: {self.value}, Created At: {self.created_at}, Updated At: {self.updated_at}"

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_dict(data) -> 'Metadata':
        if not isinstance(data, dict): # Because somehow we get an Object sometimes ://
            return Metadata()
        return Metadata(
            key=data.get("key"),
            value=data.get("value"),
            created_at=datetime.fromisoformat(data["createdAt"]) if data.get("createdAt") else None,
            updated_at=datetime.fromisoformat(data["updatedAt"]) if data.get("updatedAt") else None,
        )