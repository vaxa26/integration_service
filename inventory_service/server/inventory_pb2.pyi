from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InventoryRequest(_message.Message):
    __slots__ = ("items",)
    class ItemsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.ScalarMap[str, int]
    def __init__(self, items: _Optional[_Mapping[str, int]] = ...) -> None: ...

class InventoryResponse(_message.Message):
    __slots__ = ("availability",)
    class AvailabilityEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    availability: _containers.ScalarMap[str, bool]
    def __init__(self, availability: _Optional[_Mapping[str, bool]] = ...) -> None: ...

class ReserveRequest(_message.Message):
    __slots__ = ("items",)
    class ItemsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.ScalarMap[str, int]
    def __init__(self, items: _Optional[_Mapping[str, int]] = ...) -> None: ...

class ReserveResponse(_message.Message):
    __slots__ = ("overallSuccess", "results")
    class ResultsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ReserveStatus
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ReserveStatus, _Mapping]] = ...) -> None: ...
    OVERALLSUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    overallSuccess: bool
    results: _containers.MessageMap[str, ReserveStatus]
    def __init__(self, overallSuccess: bool = ..., results: _Optional[_Mapping[str, ReserveStatus]] = ...) -> None: ...

class ReserveStatus(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ReleaseRequest(_message.Message):
    __slots__ = ("items",)
    class ItemsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.ScalarMap[str, int]
    def __init__(self, items: _Optional[_Mapping[str, int]] = ...) -> None: ...

class ReleaseResponse(_message.Message):
    __slots__ = ("overallSuccess", "messages")
    class MessagesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    OVERALLSUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    overallSuccess: bool
    messages: _containers.ScalarMap[str, str]
    def __init__(self, overallSuccess: bool = ..., messages: _Optional[_Mapping[str, str]] = ...) -> None: ...
