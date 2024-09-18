import pytest

from app.services.a_indicators import compA3_2
from app.models.instance import Instance

def test_compA3_2_with_no_web_and_free_os():
    instance = Instance(type='no_web', os=["Linux"])
    result, logs = compA3_2(instance)
    assert result == True

def test_compA3_2_with_no_web_and_non_free_os():
    instance = Instance(type='no_web', os=["Windows"])
    result, logs = compA3_2(instance)
    assert result == False

def test_compA3_2_with_no_web_and_mixed_os():
    instance = Instance(type='no_web', os=["Linux", "Windows"])
    result, logs = compA3_2(instance)
    assert result == True

def test_compA3_2_with_no_web_and_mixed_os_lower():
    instance = Instance(type='no_web', os=["linux", "Windows"])
    result, logs = compA3_2(instance)
    assert result == True


def test_compA3_2_with_no_web_and_empty_os():
    instance = Instance(type='no_web', os=[])
    result, logs = compA3_2(instance)
    assert result == False


def test_compA3_2_with_no_web_and_none_os():
    instance = Instance(type='no_web', os=None)
    result, logs = compA3_2(instance)
    assert result == False


def test_compA3_2_with_web():
    instance = Instance(type='web', os=["Linux"])
    result, logs = compA3_2(instance)
    assert result == False    

def test_compA3_2_with_none_type():
    instance = Instance(type=None, os=["Linux"])
    result, logs = compA3_2(instance)
    assert result == True

if __name__ == "__main__":
    pytest.main()
