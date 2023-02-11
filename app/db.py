from datetime import datetime
from enum import Enum
import databases
import ormar
import sqlalchemy

from .config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()

class LifterClass(Enum):
    U = "Ungdom"
    J = "Junior"
    S = "Senior"
    M1 = "Veteran (40-49 år)"
    M2 = "Veteran (50-59 år)"
    M3 = "Veteran (60-69 år)"
    M4 = "Veteran (70-79 år)"

class GenderChoice(Enum):
    M = "Man"
    F = "Kvinna"

class LicenseStatus(Enum):
    LI = "Licensierad"
    EL = "Ej licensierad"

class JudgeLevel(Enum):
    DD = "Distriktsdomare"
    FD = "Förbundsdomare"

class Discipline(Enum):
    SQ = "Knäböj"
    BP = "Bänkpress"
    DL = "Marklyft"
    PB = "Paralympisk Bänkpress"

class CompetitionType(Enum):
    EBP = "Utrustad Bänkpress"
    CPL = "Klassiskt Styrkelyft"
    EPL = "Utrustat Styrkelyft"
    CBP = "Klassisk Bänkpress"
    PBP = "Paralympisk Bänkpress"

class PointSystem(Enum):
    IPF = "IPF-poäng"
    WLK = "Wilks-poäng"

class RoleType(Enum):
    CLA = "ClubAdmin"
    DIA = "DistrictAdmin"
    NAA = "NationalAdmin"
    COA = "CompetitionAdmin"
    COO = "CompetitionOrganizer"
    SUA = "SuperAdmin"

class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database

class BaseModel(ormar.Model):
    class Meta(BaseMeta):
        pass

class WeightClass(BaseModel):
    id: int = ormar.Integer(primary_key=True)
    min_weight = ormar.SmallInteger()
    max_weight = ormar.SmallInteger()
    archived = ormar.Boolean(default=False, nullable=False)

class AgeBracket(BaseModel):
    id: int = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=40)
    min_age = ormar.SmallInteger()
    max_age = ormar.SmallInteger()
    archived = ormar.Boolean(default=True, nullable=False)

class Category(BaseModel):
    gender = ormar.Enum(GenderChoice)
    weight_class = ormar.ForeignKey(WeightClass)
    age_bracket = ormar.ForeignKey(AgeBracket)

class Fee(BaseModel):
    year = ormar.SmallInteger()
    invoiced_at = ormar.DateTime()
    paid_at = ormar.DateTime()

class Contact(BaseModel):
    role = ormar.String(max_length=50)
    name = ormar.String(max_lenght=100)
    phone = ormar.String(max_length=50, nullable=True)
    email = ormar.String(max_length=200, nullable=True)

class ContactInformation(BaseModel):
    address = ormar.String(max_length=200)
    postal_code = ormar.String(max_length=5, nullable=True)
    postal_city = ormar.String(max_length=50, nullable=True)
    phone = ormar.String(max_length=50, nullable=True)
    email = ormar.String(nullable=True)

class District(BaseModel):
    name = ormar.String(max_length=100)
    rf_number = ormar.SmallInteger()
    org_number = ormar.String(max_length=10)
    contact_information = ormar.ForeignKey(ContactInformation)
    contacts = ormar.ManyToMany(Contact)

class Club(BaseModel):
    name = ormar.String(max_length=100)
    district = ormar.ForeignKey(District)
    rf_number = ormar.SmallInteger()
    org_number = ormar.String(max_length=10)
    contact_information = ormar.ForeignKey(ContactInformation)
    fees = ormar.ManyToMany(Fee)

class Lifter(BaseModel):
    first_name = ormar.String(max_length=50)
    family_name = ormar.String(max_length=100)
    contact_information = ormar.ForeignKey(ContactInformation)
    gender = ormar.Enum(GenderChoice)
    id_number = ormar.String(max_length=12)
    clubs = ormar.ManyToMany(Club)
    created_at = ormar.DateTime(default=datetime.now())

class License(BaseModel):
    lifter = ormar.ForeignKey(Lifter)
    club = ormar.ForeignKey(Club)
    number = ormar.String(max_length=8)
    year = ormar.SmallInteger()
    requested = ormar.DateTime(default=datetime.now())
    canceled_at = ormar.DateTime(nullable=True)
    status = ormar.Enum(LicenseStatus)

class JudgeLicense(BaseModel):
    lifter = ormar.ForeignKey(Lifter)
    judge_level = ormar.Enum(JudgeLevel)
    book_number = ormar.SmallInteger()
    approved = ormar.Boolean(default=True, nullable=False)
    year = ormar.SmallInteger()

class Roles(BaseModel):
    lifter = ormar.ForeignKey(Lifter)
    role = ormar.Enum(RoleType)

class CollectedResult(BaseModel):
    lifter = ormar.ForeignKey(Lifter)
    weighin_weight = ormar.Decimal(max_digits=5, decimal_places=2)
    weight_class = ormar.ForeignKey(WeightClass)
    category = ormar.ForeignKey(Category)

class Result(BaseModel):
    removed = ormar.Boolean(default=False, nullable=False)
    order_number = ormar.SmallInteger(nullable=True)
    result = ormar.Decimal(max_digits=4, decimal_places=1)
    discipline = ormar.ForeignKey(Discipline)
    competition_type = ormar.ForeignKey(CompetitionType)
    collected_result = ormar.ForeignKey(CollectedResult)

class Division(BaseModel):
    name = ormar.String(max_length=100)
    start = ormar.Date()
    stop = ormar.Date()
    max_lifters = ormar.SmallInteger()
    competition_type = ormar.Enum(CompetitionType)
    point_system = ormar.Enum(PointSystem)

class Team(BaseModel):
    club = ormar.ForeignKey(Club)
    current_division = ormar.ForeignKey(Division)

class Round(BaseModel):
    number = ormar.SmallInteger()
    division = ormar.ForeignKey(Division)

class SeriesTeamResult(BaseModel):
    team = ormar.ForeignKey(Team)
    round = ormar.ForeignKey(Round)
    results = ormar.ManyToMany(Result)

class Document(BaseModel):
    file = ormar.LargBinary(max_length=10000000)

class QualificationLevel(BaseModel):
    category = ormar.ForeignKey(Category)
    qualification_limit = ormar.SmallInteger()

class Invitation(BaseModel):
    name = ormar.String(max_length=50)
    description = ormar.Text()
    organizer = ormar.ForeignKey(Club)
    start_date = ormar.Date()
    finish_date = ormar.Date()
    last_signup = ormar.Date()
    contact = ormar.ForeignKey(Contact)
    competition_types = ormar.ManyToMany(CompetitionType)
    categories = ormar.ManyToMany(Category)
    documents = ormar.ManyToMany(Document)
    qualification_level = ormar.ManyToMany(QualificationLevel)
    affects_ranking = ormar.Boolean(default=True, nullable=False)

class Competition(BaseModel):
    invitation = ormar.ForeignKey(Invitation)
    results = ormar.ManyToMany(Result)

class User(BaseModel):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True)
    email: str = ormar.String(max_length=128, unique=True, nullable=False)
    active: bool = ormar.Boolean(default=True, nullable=False)


engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)