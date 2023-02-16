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

class WeightClass(ormar.Model):
    class Meta(BaseMeta):
        tablename = "weight_class"

    id = ormar.Integer(primary_key=True)
    min_weight = ormar.SmallInteger()
    max_weight = ormar.SmallInteger()
    archived = ormar.Boolean(default=False, nullable=False)

class AgeBracket(ormar.Model):
    class Meta(BaseMeta):
        tablename = "age_bracket"

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=40)
    min_age = ormar.SmallInteger()
    max_age = ormar.SmallInteger()
    archived = ormar.Boolean(default=True, nullable=False)

class Category(ormar.Model):
    class Meta(BaseMeta):
        tablename = "category"

    id = ormar.Integer(primary_key=True)
    gender = ormar.Enum(enum_class=GenderChoice)
    weight_class = ormar.ForeignKey(WeightClass)
    age_bracket = ormar.ForeignKey(AgeBracket)

class Fee(ormar.Model):
    class Meta(BaseMeta):
        tablename = "fee"

    id = ormar.Integer(primary_key=True)
    year = ormar.SmallInteger()
    invoiced_at = ormar.DateTime()
    paid_at = ormar.DateTime()

class Contact(ormar.Model):
    class Meta(BaseMeta):
        tablename = "contact"

    id = ormar.Integer(primary_key=True)
    role = ormar.String(max_length=50)
    name = ormar.String(max_length=100)
    phone = ormar.String(max_length=50, nullable=True)
    email = ormar.String(max_length=200, nullable=True)

class ContactInformation(ormar.Model):
    class Meta(BaseMeta):
        tablename = "contact_information"

    id = ormar.Integer(primary_key=True)
    address = ormar.String(max_length=200)
    postal_code = ormar.String(max_length=5, nullable=True)
    postal_city = ormar.String(max_length=50, nullable=True)
    phone = ormar.String(max_length=50, nullable=True)
    email = ormar.String(max_length=200, nullable=True)

class District(ormar.Model):
    class Meta(BaseMeta):
        tablename = "district"

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=100)
    rf_number = ormar.SmallInteger()
    org_number = ormar.String(max_length=10)
    contact_information = ormar.ForeignKey(ContactInformation)
    contacts = ormar.ManyToMany(Contact)

class Club(ormar.Model):
    class Meta(BaseMeta):
        tablename = "club"

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=100)
    district = ormar.ForeignKey(District)
    rf_number = ormar.SmallInteger()
    org_number = ormar.String(max_length=10)
    contact_information = ormar.ForeignKey(ContactInformation)
    fees = ormar.ManyToMany(Fee)

class Lifter(ormar.Model):
    class Meta(BaseMeta):
        tablename = "lifter"

    id = ormar.Integer(primary_key=True)
    first_name = ormar.String(max_length=50)
    family_name = ormar.String(max_length=100)
    contact_information = ormar.ForeignKey(ContactInformation)
    gender = ormar.Enum(enum_class=GenderChoice)
    id_number = ormar.String(max_length=12)
    clubs = ormar.ManyToMany(Club)
    created_at = ormar.DateTime(default=datetime.now())

class License(ormar.Model):
    class Meta(BaseMeta):
        tablename = "license"

    id = ormar.Integer(primary_key=True)
    lifter = ormar.ForeignKey(Lifter)
    club = ormar.ForeignKey(Club)
    number = ormar.String(max_length=8)
    year = ormar.SmallInteger()
    requested = ormar.DateTime(default=datetime.now())
    canceled_at = ormar.DateTime(nullable=True)
    status = ormar.Enum(enum_class=LicenseStatus)

class JudgeLicense(ormar.Model):
    class Meta(BaseMeta):
        tablename = "judge_license"

    id = ormar.Integer(primary_key=True)
    lifter = ormar.ForeignKey(Lifter)
    judge_level = ormar.Enum(enum_class=JudgeLevel)
    book_number = ormar.SmallInteger()
    approved = ormar.Boolean(default=True, nullable=False)
    year = ormar.SmallInteger()

class Roles(ormar.Model):
    class Meta(BaseMeta):
        tablename = "roles"

    id = ormar.Integer(primary_key=True)
    lifter = ormar.ForeignKey(Lifter)
    role = ormar.Enum(enum_class=RoleType)

class CollectedResult(ormar.Model):
    class Meta(BaseMeta):
        tablename = "collected_result"

    id = ormar.Integer(primary_key=True)
    lifter = ormar.ForeignKey(Lifter)
    weighin_weight = ormar.Decimal(max_digits=5, decimal_places=2)
    weight_class = ormar.ForeignKey(WeightClass)
    category = ormar.ForeignKey(Category)

class Result(ormar.Model):
    class Meta(BaseMeta):
        tablename = "result"

    id = ormar.Integer(primary_key=True)
    removed = ormar.Boolean(default=False, nullable=False)
    order_number = ormar.SmallInteger(nullable=True)
    result = ormar.Decimal(max_digits=4, decimal_places=1)
    discipline = ormar.Enum(enum_class=Discipline)
    competition_type = ormar.Enum(enum_class=CompetitionType)
    collected_result = ormar.ForeignKey(CollectedResult)

class Division(ormar.Model):
    class Meta(BaseMeta):
        tablename = "division"

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=100)
    start = ormar.Date()
    stop = ormar.Date()
    max_lifters = ormar.SmallInteger()
    competition_type = ormar.Enum(enum_class=CompetitionType)
    point_system = ormar.Enum(enum_class=PointSystem)

class Team(ormar.Model):
    class Meta(BaseMeta):
        tablename = "team"

    id = ormar.Integer(primary_key=True)
    club = ormar.ForeignKey(Club)
    current_division = ormar.ForeignKey(Division)

class Round(ormar.Model):
    class Meta(BaseMeta):
        tablename = "round"

    id = ormar.Integer(primary_key=True)
    number = ormar.SmallInteger()
    division = ormar.ForeignKey(Division)

class SeriesTeamResultResult(ormar.Model):
    class Meta(BaseMeta):
        tablename = "str_x_r"
    id = ormar.Integer(primary_key=True)

class SeriesTeamResult(ormar.Model):
    class Meta(BaseMeta):
        tablename = "series_team_result"

    id = ormar.Integer(primary_key=True)
    team = ormar.ForeignKey(Team)
    round = ormar.ForeignKey(Round)
    results = ormar.ManyToMany(Result, through=SeriesTeamResultResult)

class Document(ormar.Model):
    class Meta(BaseMeta):
        tablename = "document"

    id = ormar.Integer(primary_key=True)
    file = ormar.LargeBinary(max_length=10000000)

class QualificationLevel(ormar.Model):
    class Meta(BaseMeta):
        tablename = "q_level"

    id = ormar.Integer(primary_key=True)
    category = ormar.ForeignKey(Category)
    qualification_limit = ormar.SmallInteger()

class InvQLevel(ormar.Model):
    class Meta(BaseMeta):
        tablename = "i_x_ql"
    id = ormar.Integer(primary_key=True)

class Invitation(ormar.Model):
    class Meta(BaseMeta):
        tablename = "invitation"

    id = ormar.Integer(primary_key=True)
    name = ormar.String(max_length=50)
    description = ormar.Text()
    organizer = ormar.ForeignKey(Club)
    start_date = ormar.Date()
    finish_date = ormar.Date()
    last_signup = ormar.Date()
    contact = ormar.ForeignKey(Contact)
    competition_types = ormar.String(max_length=200)
    categories = ormar.ManyToMany(Category)
    documents = ormar.ManyToMany(Document)
    q_levels = ormar.ManyToMany(QualificationLevel, through=InvQLevel)
    affects_ranking = ormar.Boolean(default=True, nullable=False)

class Competition(ormar.Model):
    class Meta(BaseMeta):
        tablename = "competition"

    id = ormar.Integer(primary_key=True)
    invitation = ormar.ForeignKey(Invitation)
    results = ormar.ManyToMany(Result)

engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)