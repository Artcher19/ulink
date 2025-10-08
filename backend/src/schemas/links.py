from pydantic import BaseModel, Field

class LinkAddSchema(BaseModel):
    full_link: str = Field(description='Оригинальная ссылка')

class LinkSchema(LinkAddSchema):
    link_id: int
    short_link: str
    create_date: str

