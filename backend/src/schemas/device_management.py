from pydantic import BaseModel, FutureDatetime


class GetOTP(BaseModel):
    otp: str
    exp: FutureDatetime


class AuthenticateOTP(BaseModel):
    otp: str
    mac_adress: str
    name: str


class AuthenticatedDevice(BaseModel):
    device_secret: str
    exp: FutureDatetime
