import factory
import factory.fuzzy

from books_collection.account.enums import State
from books_collection.account.models import Account
from books_collection.account.schemas import AccountRequest


class AccountFactory(factory.Factory):
    class Meta:
        model = Account

    username = factory.Sequence(lambda n: f'username-{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}#pass')
    state = factory.fuzzy.FuzzyChoice(State)


class AccountRequestFactory(factory.Factory):
    class Meta:
        model = AccountRequest

    username = factory.Sequence(lambda n: f'username-{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}#pass')
