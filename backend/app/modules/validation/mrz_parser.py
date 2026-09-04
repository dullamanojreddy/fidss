from pydantic import BaseModel
from typing import Optional, List
from .mrz_checksum import verify_check_digit, compute_check_digit

class FieldStatus(BaseModel):
    value: str
    status: str  # "VALID", "INVALID", "INCOMPLETE"

class MrzResult(BaseModel):
    mrz_type: str
    document_type: FieldStatus
    issuing_country: FieldStatus
    surname: FieldStatus
    given_names: FieldStatus
    document_number: FieldStatus
    nationality: FieldStatus
    dob: FieldStatus
    sex: FieldStatus
    expiry_date: FieldStatus
    personal_number: FieldStatus
    composite_status: str  # "VALID", "INVALID", "INCOMPLETE"

def parse_names(name_field: str):
    parts = name_field.split("<<", 1)
    surname = parts[0].replace("<", " ").strip()
    given_names = parts[1].replace("<", " ").strip() if len(parts) > 1 else ""
    return surname, given_names

def _build_incomplete_result(mrz_type: str = "UNKNOWN") -> MrzResult:
    fs = FieldStatus(value="", status="INCOMPLETE")
    return MrzResult(
        mrz_type=mrz_type,
        document_type=fs, issuing_country=fs, surname=fs, given_names=fs,
        document_number=fs, nationality=fs, dob=fs, sex=fs,
        expiry_date=fs, personal_number=fs, composite_status="INCOMPLETE"
    )

def parse_mrz(lines: List[str]) -> MrzResult:
    if not lines:
        return _build_incomplete_result()
        
    line_len = len(lines[0])
    if len(lines) == 2 and line_len == 44:
        return parse_td3(lines)
    elif len(lines) == 2 and line_len == 36:
        return parse_td2(lines)
    elif len(lines) == 3 and line_len == 30:
        return parse_td1(lines)
        
    return _build_incomplete_result()

def parse_td3(lines: List[str]) -> MrzResult:
    try:
        line1, line2 = lines
        doc_type = line1[0:2].replace("<", "")
        country = line1[2:5].replace("<", "")
        surname, given_names = parse_names(line1[5:44])
        
        doc_num = line2[0:9]
        doc_num_cd = line2[9]
        nationality = line2[10:13].replace("<", "")
        dob = line2[13:19]
        dob_cd = line2[19]
        sex = line2[20].replace("<", "UNSPECIFIED")
        expiry = line2[21:27]
        expiry_cd = line2[27]
        personal_num = line2[28:42]
        personal_num_cd = line2[42]
        composite_cd = line2[43]
        
        doc_num_status = "VALID" if verify_check_digit(doc_num, doc_num_cd) else "INVALID"
        dob_status = "VALID" if verify_check_digit(dob, dob_cd) else "INVALID"
        expiry_status = "VALID" if verify_check_digit(expiry, expiry_cd) else "INVALID"
        
        # Personal number check digit is optional in some countries (can be '<'). If '<', verify_check_digit handles it (expects 0).
        # Actually ICAO says if no check digit is used, the field should be '<'.
        if personal_num_cd == '<':
            personal_num_status = "VALID" # if it's '<', it means no check digit was computed
            # But the composite check digit includes it as '<' (0).
        else:
            personal_num_status = "VALID" if verify_check_digit(personal_num, personal_num_cd) else "INVALID"
            
        # Composite check digit
        composite_str = doc_num + doc_num_cd + dob + dob_cd + expiry + expiry_cd + personal_num + personal_num_cd
        composite_status = "VALID" if verify_check_digit(composite_str, composite_cd) else "INVALID"
        
        return MrzResult(
            mrz_type="TD3",
            document_type=FieldStatus(value=doc_type, status="VALID"),
            issuing_country=FieldStatus(value=country, status="VALID"),
            surname=FieldStatus(value=surname, status="VALID"),
            given_names=FieldStatus(value=given_names, status="VALID"),
            document_number=FieldStatus(value=doc_num.replace("<", ""), status=doc_num_status),
            nationality=FieldStatus(value=nationality, status="VALID"),
            dob=FieldStatus(value=dob, status=dob_status),
            sex=FieldStatus(value=sex, status="VALID"),
            expiry_date=FieldStatus(value=expiry, status=expiry_status),
            personal_number=FieldStatus(value=personal_num.replace("<", ""), status=personal_num_status),
            composite_status=composite_status
        )
    except Exception:
        return _build_incomplete_result("TD3")

def parse_td2(lines: List[str]) -> MrzResult:
    try:
        line1, line2 = lines
        doc_type = line1[0:2].replace("<", "")
        country = line1[2:5].replace("<", "")
        surname, given_names = parse_names(line1[5:36])
        
        doc_num = line2[0:9]
        doc_num_cd = line2[9]
        nationality = line2[10:13].replace("<", "")
        dob = line2[13:19]
        dob_cd = line2[19]
        sex = line2[20].replace("<", "UNSPECIFIED")
        expiry = line2[21:27]
        expiry_cd = line2[27]
        personal_num = line2[28:35]
        
        composite_cd = line2[35]
        
        doc_num_status = "VALID" if verify_check_digit(doc_num, doc_num_cd) else "INVALID"
        dob_status = "VALID" if verify_check_digit(dob, dob_cd) else "INVALID"
        expiry_status = "VALID" if verify_check_digit(expiry, expiry_cd) else "INVALID"
        
        composite_str = doc_num + doc_num_cd + dob + dob_cd + expiry + expiry_cd + personal_num
        composite_status = "VALID" if verify_check_digit(composite_str, composite_cd) else "INVALID"
        
        return MrzResult(
            mrz_type="TD2",
            document_type=FieldStatus(value=doc_type, status="VALID"),
            issuing_country=FieldStatus(value=country, status="VALID"),
            surname=FieldStatus(value=surname, status="VALID"),
            given_names=FieldStatus(value=given_names, status="VALID"),
            document_number=FieldStatus(value=doc_num.replace("<", ""), status=doc_num_status),
            nationality=FieldStatus(value=nationality, status="VALID"),
            dob=FieldStatus(value=dob, status=dob_status),
            sex=FieldStatus(value=sex, status="VALID"),
            expiry_date=FieldStatus(value=expiry, status=expiry_status),
            personal_number=FieldStatus(value=personal_num.replace("<", ""), status="VALID"),
            composite_status=composite_status
        )
    except Exception:
        return _build_incomplete_result("TD2")

def parse_td1(lines: List[str]) -> MrzResult:
    try:
        line1, line2, line3 = lines
        doc_type = line1[0:2].replace("<", "")
        country = line1[2:5].replace("<", "")
        doc_num = line1[5:14]
        doc_num_cd = line1[14]
        opt1 = line1[15:30]
        
        dob = line2[0:6]
        dob_cd = line2[6]
        sex = line2[7].replace("<", "UNSPECIFIED")
        expiry = line2[8:14]
        expiry_cd = line2[14]
        nationality = line2[15:18].replace("<", "")
        opt2 = line2[18:29]
        composite_cd = line2[29]
        
        surname, given_names = parse_names(line3[0:30])
        
        doc_num_status = "VALID" if verify_check_digit(doc_num, doc_num_cd) else "INVALID"
        dob_status = "VALID" if verify_check_digit(dob, dob_cd) else "INVALID"
        expiry_status = "VALID" if verify_check_digit(expiry, expiry_cd) else "INVALID"
        
        composite_str = doc_num + doc_num_cd + opt1 + dob + dob_cd + expiry + expiry_cd + opt2
        composite_status = "VALID" if verify_check_digit(composite_str, composite_cd) else "INVALID"
        
        personal_num = opt1 + opt2
        
        return MrzResult(
            mrz_type="TD1",
            document_type=FieldStatus(value=doc_type, status="VALID"),
            issuing_country=FieldStatus(value=country, status="VALID"),
            surname=FieldStatus(value=surname, status="VALID"),
            given_names=FieldStatus(value=given_names, status="VALID"),
            document_number=FieldStatus(value=doc_num.replace("<", ""), status=doc_num_status),
            nationality=FieldStatus(value=nationality, status="VALID"),
            dob=FieldStatus(value=dob, status=dob_status),
            sex=FieldStatus(value=sex, status="VALID"),
            expiry_date=FieldStatus(value=expiry, status=expiry_status),
            personal_number=FieldStatus(value=personal_num.replace("<", ""), status="VALID"),
            composite_status=composite_status
        )
    except Exception:
        return _build_incomplete_result("TD1")
