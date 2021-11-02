class Warehouse():
    
    def __init__(self) -> None:
        self.entities = []

    def AddEntity(self, entityInstance) -> None:
        self.entities.append(entityInstance)

