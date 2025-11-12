from pydantic import BaseModel

from typing import List, Optional, Dict, Any


class Option(BaseModel):
    id: str
    parameters: Optional[Dict[str, Any]] = None


class Group(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[int] = None
    level: Optional[int] = None
    actions: Optional[List[str]] = None


class Order(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    actions: Optional[List[str]] = None
    resources: Optional[List[str]] = None


class DeviceType(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    actions: Optional[List[str]] = None
    resources: Optional[List[str]] = None


class ContractDetail(BaseModel):
    name: str
    activationEndTime: int
    communicationEndTime: int
    bidir: bool
    highPriorityDownlink: bool
    maxUplinkFrames: int
    maxDownlinkFrames: int
    maxTokens: int
    automaticRenewal: bool
    renewalDuration: int
    options: Optional[List[Option]] = None
    id: str
    contractId: str
    userId: str
    group: Optional[Group] = None
    order: Optional[Order] = None
    pricingModel: Optional[int] = None
    createdBy: str
    lastEditionTime: int
    creationTime: int
    lastEditedBy: str
    startTime: int
    timezone: str
    subscriptionPlan: Optional[int] = None
    tokenDuration: int
    blacklistedTerritories: Optional[List[Group]] = None
    tokensInUse: int
    tokensUsed: int
    deviceType: Optional[DeviceType] = None


class Paging(BaseModel):
    next: Optional[str] = None


class ContractsResponse(BaseModel):
    data: List[ContractDetail]
    paging: Paging


class ContractBrief(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    actions: Optional[List[str]] = None
    resources: Optional[List[str]] = None


class ModemCertificate(BaseModel):
    id: Optional[str] = None
    key: Optional[str] = None


class ProductCertificate(BaseModel):
    id: Optional[str] = None
    key: Optional[str] = None


class Location(BaseModel):
    lat: float
    lng: float


class LastComputedLocation(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius: Optional[int] = None
    sourceCode: Optional[int] = None
    placeIds: Optional[List[str]] = None


class Token(BaseModel):
    state: Optional[int] = None
    detailMessage: Optional[str] = None
    end: Optional[int] = None
    unsubscriptionTime: Optional[int] = None
    freeMessages: Optional[int] = None
    freeMessagesSent: Optional[int] = None


class Device(BaseModel):
    id: str
    name: str
    satelliteCapable: bool
    repeater: bool
    messageModulo: int
    deviceType: Optional[DeviceType] = None
    contract: Optional[ContractBrief] = None
    group: Group
    modemCertificate: Optional[ModemCertificate] = None
    prototype: bool
    productCertificate: Optional[ProductCertificate] = None
    location: Location
    lastComputedLocation: Optional[LastComputedLocation] = None
    pac: str
    sequenceNumber: Optional[int] = None
    trashSequenceNumber: Optional[int] = None
    lastCom: Optional[int] = None
    lqi: int
    activationTime: Optional[int] = None
    creationTime: int
    state: int
    comState: int
    token: Optional[Token] = None
    unsubscriptionTime: Optional[int] = None
    createdBy: str
    lastEditionTime: int
    lastEditedBy: str
    automaticRenewal: bool
    automaticRenewalStatus: int
    activable: bool
    actions: Optional[List[str]] = None
    resources: Optional[List[str]] = None


class DevicesResponse(BaseModel):
    data: List[Device]
    paging: Paging


class DeviceTypesResponse(BaseModel):
    data: List[DeviceType]
    paging: Paging


class BaseDevice(BaseModel):
    id: str


class SimpleDevice(BaseDevice):
    name: Optional[str] = None


class ComputedLocation(BaseModel):
    lat: float
    lng: float
    radius: int
    source: int


class BaseStation(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    resourceType: Optional[int] = None


class Repetition(BaseModel):
    nseq: int
    rssi: str
    freq: float
    repeated: bool


class CBStatus(BaseModel):
    status: int
    cbDef: str
    time: int
    attempts: int


class Rinfo(BaseModel):
    baseStation: BaseStation
    rssi: str
    rssiRepeaters: str
    lat: str
    lng: str
    freq: float
    freqRepeaters: str
    rep: int
    repetitions: List[Repetition]
    cbStatus: CBStatus


class DownlinkAckInfo(BaseModel):
    emissionTimestamp: Optional[int] = None
    retryNumber: Optional[int] = None
    lastCst: Optional[int] = None


class DownlinkPowerMatrixTrain(BaseModel):
    timeSlot: Optional[int] = None
    device: Optional[str] = None
    actualPower: Optional[float] = None
    plannedPower: Optional[float] = None


class DownlinkPowerMatrixTransmission(BaseModel):
    index: Optional[int] = None
    train: Optional[List[DownlinkPowerMatrixTrain]] = None


class DownlinkPowerMatrix(BaseModel):
    id: Optional[str] = None
    numberOfSlots: Optional[int] = None
    transmissions: Optional[List[DownlinkPowerMatrixTransmission]] = None


class DownlinkAnswerStatus(BaseModel):
    baseStation: Optional[BaseStation] = None
    plannedPower: Optional[float] = None
    data: Optional[str] = None
    operator: Optional[str] = None
    country: Optional[str] = None


class DownlinkAnswerStatusDetail(BaseModel):
    statusCode: Optional[int] = None
    message: Optional[str] = None
    status: Optional[int] = None
    transmissionTime: Optional[int] = None
    baseStation: Optional[BaseStation] = None
    freq: Optional[float] = None
    slot: Optional[int] = None
    downlinkMethod: Optional[int] = None
    plannedPower: Optional[float] = None
    data: Optional[str] = None
    downlinkAckInfo: Optional[DownlinkAckInfo] = None
    downlinkPowerMatrix: Optional[DownlinkPowerMatrix] = None
    operator: Optional[str] = None
    country: Optional[str] = None


class DeviceMessage(BaseModel):
    device: Optional[SimpleDevice] = None
    time: int
    data: str
    ackRequired: Optional[bool] = None
    lqi: int
    seqNumber: int
    nbFrames: int
    computedLocation: List[ComputedLocation]
    rinfos: List[Rinfo]
    downlinkAnswerStatus: Optional[DownlinkAnswerStatus] = None
    downlinkAnswerStatuses: Optional[List[DownlinkAnswerStatusDetail]] = None


class DeviceMessagesResponse(BaseModel):
    data: List[DeviceMessage]
    paging: Paging


class DeviceMessageStats(BaseModel):
    lastDay: int
    lastWeek: int
    lastMonth: int


class RequestErrorDescription(BaseModel):
    type: str
    field: str
    message: str


class ErrorResponse(BaseModel):
    message: str
    errors: list[RequestErrorDescription]
