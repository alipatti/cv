import pydantic


class About(pydantic.BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    website: str = ""


class Item(pydantic.BaseModel):
    title: str = ""
    subtitle: str = ""
    dates: str | int = ""
    bullets: list[str] = []
    citation: str = ""
    with_: str = pydantic.Field(alias="with", default="")
    details: str = ""


class Section(pydantic.BaseModel):
    title: str
    summary: str = ""
    items: list[Item] = []


class CVContent(pydantic.BaseModel):
    about: About
    sections: list[Section]
