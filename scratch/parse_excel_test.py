import openpyxl
import re
import os

os.makedirs("scratch", exist_ok=True)

def test_excel_parse():
    wb = openpyxl.load_workbook('ROK Question.xlsx')
    sheet = wb['Sheet2']
    rows = [r[0] for r in list(sheet.iter_rows(values_only=True)) if r[0] and r[1] is None]

    def clean_leading_num(s):
        s = s.strip()
        s = re.sub(r'^\d+[\.\s\-]+', '', s)
        return s.strip()

    parsed_count = 0
    for i, raw in enumerate(rows):
        cleaned = clean_leading_num(raw)
        
        # Try splitting by various separators
        parts = []
        if '?' in cleaned:
            # If there is a question mark, split by it but keep the question mark with the first part
            idx = cleaned.find('?')
            p1 = cleaned[:idx+1].strip()
            p2 = cleaned[idx+1:].strip()
            # Clean leading separator in p2
            p2 = re.sub(r'^[\s\:\/\-\.\,\"]+', '', p2)
            if p1 and p2:
                parts = [p1, p2]
        
        if not parts:
            for sep in ['/.', '/', ':', ' - ', ' – ']:
                if sep in cleaned:
                    parts = [p.strip() for p in cleaned.split(sep, 1)]
                    break
                    
        if len(parts) == 2:
            p1, p2 = parts[0], parts[1]
            # Heuristic: longer is question, shorter is answer
            # Unless one already contains a question mark
            if '?' in p1:
                q, a = p1, p2
            elif '?' in p2:
                q, a = p2, p1
            else:
                if len(p1) > len(p2):
                    q, a = p1, p2
                else:
                    q, a = p2, p1
                    
            # Clean up question and answer
            q = re.sub(r'^[\s\:\/\-\.\,\"]+', '', q).strip()
            a = re.sub(r'^[\s\:\/\-\.\,\"]+', '', a).strip()
            # Strip trailing quotes or dots from answer
            a = re.sub(r'[\.\"]+$', '', a).strip()
            
            # Verify length and that answer is not empty
            if len(q) > 8 and len(a) > 0:
                print(f'{i+1}. Q: "{q}" | A: "{a}"')
                parsed_count += 1
            else:
                print(f'{i+1}. [SKIP SHORT] Q: "{q}" | A: "{a}" (Raw: "{raw}")')
        else:
            print(f'{i+1}. [FAILED SPLIT] Raw: "{raw}"')

    print(f'\nTotal parsed successfully: {parsed_count} / {len(rows)}')

if __name__ == "__main__":
    test_excel_parse()
