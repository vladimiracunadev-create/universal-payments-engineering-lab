from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    @abstractmethod
    def create(self, payload: dict, **kwargs): ...

    @abstractmethod
    def get(self, payment_id: str): ...
