import pytest
from app.calculation import *

@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(50)

@pytest.mark.parametrize("num1, num2, expected",[
    (3,2,5),
    (7,1,8),
    (12,4,16)
])
def test_add(num1,num2,expected):
    print('testin add fucntion')
    assert add(num1,num2) == expected

def test_bank_set_initial_amount(zero_bank_account):
    assert zero_bank_account.balance == 0

def test_withdrow(bank_account):
    bank_account.withdraw(20)
    assert bank_account.balance == 30

def test_deposite(bank_account):
    bank_account.deposit(30)
    assert bank_account.balance == 80

def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance,3) == 55

@pytest.mark.parametrize("deposite, withdraw, expected",[
    (200,100,100),
    (7,1,6),
    (12,4,8)
])
def test_bank_transaction(zero_bank_account,deposite, withdraw, expected):
    zero_bank_account.deposit(deposite)
    zero_bank_account.withdraw(withdraw)
    assert zero_bank_account.balance == expected

def test_insufficinet_funds(bank_account):
    with pytest.raises(InsufficientClassFunds):
        bank_account.withdraw(100)



    