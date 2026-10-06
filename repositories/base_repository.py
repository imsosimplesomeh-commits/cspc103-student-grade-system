# base_repository.py - base repository interface for CRUD operations

from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def find_by_id(self, entity_id):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def save(self, entity):
        pass

    @abstractmethod
    def delete_by_id(self, entity_id):
        pass
