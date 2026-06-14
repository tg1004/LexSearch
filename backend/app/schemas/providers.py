from pydantic import BaseModel


class ProviderInfo(BaseModel):
    name: str
    label: str
    model: str | None = None
    available: bool


class ProvidersResponse(BaseModel):
    providers: list[ProviderInfo]
