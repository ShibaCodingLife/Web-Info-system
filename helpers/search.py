import re
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from pydantic import BaseModel

__ALL__ = ("SearchParam", "parse_params", "search_t_s_info")


class SearchParam(BaseModel):
    class SearchType(Enum):
        fuzzy = 'fuzzy'
        regex = 'regex'
        exact = 'exact'

    field: str
    value: str
    search_type: SearchType = SearchType.fuzzy


param_re = re.compile(R"(?:(\w+):)?(?:([rRfFeE]):)?('\w*'|\w+)")


def parse_params(params: str) -> list[SearchParam]:
    matches: list[tuple[str, str, str]] = param_re.findall(params)
    ret = []
    if not matches:
        return ret

    for field, search_type, value in matches:
        match search_type.lower():
            case 'r':
                search_type = SearchParam.SearchType.regex
            case 'f':
                search_type = SearchParam.SearchType.fuzzy
            case 'e':
                search_type = SearchParam.SearchType.exact
            case '':
                search_type = SearchParam.SearchType.fuzzy
            case _:
                raise ValueError(f"Invalid search type: {search_type}")

        value = value.strip("'")

        ret.append(SearchParam(
            field=field, value=value, search_type=search_type))

    return ret


def search_t_s_info(params: str, teacher_name: str, db: SQLAlchemy, TeacherStudentInfo: type):
    search_params = parse_params(params)
    query = db.session.query(TeacherStudentInfo)
    query = query.filter_by(teachername=teacher_name)
    for param in search_params:

        # remap field names
        match param.field.lower():
            case "name":
                param.field = "studentname"
            case "id":
                param.field = "studentnumber"
            case "age":
                param.field = "studentage"
            case "sex":
                param.field = "studentsex"
            case "addr" | "address":
                param.field = "studentorigin"
            case "dept" | "department":
                param.field = "studentsdept"
            case '':
                param.field = "studentname"
            case _:
                raise ValueError(f"Invalid field name: {param.field}")

        if param.search_type == SearchParam.SearchType.fuzzy:
            query = query.filter(
                getattr(TeacherStudentInfo, param.field).ilike(f"%{param.value}%"))
        elif param.search_type == SearchParam.SearchType.regex:
            query = query.filter(
                getattr(TeacherStudentInfo, param.field).match(param.value))
        elif param.search_type == SearchParam.SearchType.exact:
            query = query.filter(
                getattr(TeacherStudentInfo, param.field) == param.value)
    return query.all()


if __name__ == "__main__":
    pstr = "abc name:'张三' id:'123456'"
    print(param_re.findall(pstr))
