from __future__ import unicode_literals, print_function
import spacy
import re
import plac
import json
from spacy import displacy
from spacy.tokens import Span
Span.set_extension("span_type", default="value")
Span.set_extension("inTable", default=[])

CondList = {

    "<": ["<","less than","smaller than"],
    ">": [">","greater than","larger than"],
    "<=": ["<=",r"less than (or)? equal to",r"smaller than (or)? equal to"],
    ">=": [">=",r"greater than (or)? equal to",r"larger than (or)? equal to"]
    
}

AgrList = {

    "Min": ["minimum","min","lowest","smallest"],
    "Max": ["maximum","max","highest","largest"],
    "Count": ["how many","count"],
    "Sum": ["total","sum"],
    "Avg": ["avg","average"]
    
}
#Helper function
def spanIsOverlapping(start,end,spanList):
    is_overlapping = False
    is_exact_overlapping = False
    a = set(range(start,end))
    for current_span in spanList:
        b = range(current_span.start,current_span.end)
        c = a.intersection(b)
        if not len(c) == 0:
            is_overlapping = True
            if (current_span.start == start and current_span.end == end):
                is_exact_overlapping = True
            return (is_overlapping, is_exact_overlapping,current_span)
    return (False,False,None)

def tag_expr_keywords(doc,matches,label,expr):
    for match in re.finditer(expr, doc.text, re.IGNORECASE):
        start, end = match.span()
        span = doc.char_span(start, end, label = match.group(0))
        if span is not None:
            span._.span_type = label
            matches.append(span)

def tag_columns(doc,matches,tableList = None):
    for table, columns in tableList.items():
        for key, phraseList in columns.items():
            for  phrase in phraseList:
                for match in re.finditer(phrase, doc.text, re.IGNORECASE):
                    start, end = match.span()
                    span = doc.char_span(start, end, label = key)
                    if span is not None:
                        is_overlapping, is_exact_overlapping, current_span = spanIsOverlapping(span.start,span.end,matches)
                        if is_overlapping:
                            if is_exact_overlapping:
                                current_span._.inTable.append(table)
                            continue
                        span._.span_type = "column"
                        span._.inTable.append(table)
                        matches.append(span)

def tag_list_keywords(doc,matches,label,tableList = None):
    for key, phraseList in tableList.items():
        for  phrase in phraseList:
            for match in re.finditer(phrase, doc.text, re.IGNORECASE):
                start, end = match.span()
                span = doc.char_span(start, end, label = key)
                if span is not None:
                    is_overlapping, _, _ = spanIsOverlapping(span.start,span.end,matches)
                    if is_overlapping:
                        continue
                    span._.span_type = label
                    matches.append(span)

#Helper function
def find_table(table_list):
    unique_tables = set(table_list)
    count = 0
    maxCount = 0
    tables = []
    for current_table in unique_tables:
        count = 0
        for table in table_list:
            if current_table == table:
                count += 1
        if count > maxCount:
            maxCount = count
            tables = [current_table]

    return tables
        


def get_tables(keywords_list):
    tables = []
    for keyword in keywords_list:
        if keyword._.inTable:  
            tables = tables + keyword._.inTable
        elif keyword._.span_type == "table":
            tables.append(keyword.label_)
    chosen_table = find_table(tables)
    if tables:
       return chosen_table[0]
    else:
        return ""  
             
        # MIGHT USE LATER
        # for t in chosen_table:
        #     if len(table) != 0:
        #         table = table+", "+t
        #     else:
        #         table = table+t
        # return table  


def get_columns(keywords_list):
    columns_list = []
    agr = ""
    has_agr = False
    for keyword in keywords_list:
        if keyword._.span_type == "agr":
            agr = keyword.label_
            has_agr = True

        elif keyword._.span_type == "column":
            column = keyword.label_
            print(column)
            if has_agr:
                column = agr +'(DISTINCT '+column+')'
                has_agr = False
            columns_list.append(column)
    if not columns_list:
        if has_agr == True:
            return (agr +'(*)')
        else:
            print("I'm going to print all the columns")
            print(columns_list)
            print("printing get tables below")

            print(get_tables(keywords_list))
            whatTable = get_tables(keywords_list)
            # I should edit this... for when it's * it gathers all columns lol. (Could read from json file)
            if (whatTable == 'top_students'):
                #return '*'
                return 'student_id, first_name, last_name, email, gender, major, university'
            elif (whatTable == 'university_rankings'):
                return 'university, location, rank, description, tuition_fees, in_state, undergrad_enrollment'
            elif (whatTable == 'university_majors'):
                return 'major_code, major, major_category'
            else:
                return '*'
            
    else:
        print("what's this?")
        return ",".join(list(set(columns_list)))

    
def check_int_or_float(str):
    try:
        val = int(str)
        return True
    except ValueError:
        try:
            val = float(str)
            return True
        except ValueError:
            return False
     
def getWhereClause(keywords_list):
    
    used_keywords = []
    where_clauses = []
    has_conds = False
    condition = ""
    prev_keyword = None
    
    for keyword in keywords_list:
        
        if keyword._.span_type == "concat" and prev_keyword is not None:
            
            if prev_keyword._.span_type == "value":  
                where_clauses.append(keyword.label_)
                used_keywords.append(keyword)
        
        if keyword._.span_type == "value":
            rev_keywords = keywords_list[::-1]
            idx = rev_keywords.index(keyword)
            
            for word in range(idx,len(rev_keywords)):

                if rev_keywords[word]._.span_type == "cond" and not has_conds:
                    has_conds = True
                    condition = rev_keywords[word].label_
                    used_keywords.append(rev_keywords[word])
                
                if rev_keywords[word]._.span_type == "column":
                    label = keyword.label_.replace("\"","'")
                    temp_label = label.replace("'","")
                    
                    if(check_int_or_float(temp_label)):
                        label = "cast("+temp_label+" as int)"
                   
                    if(has_conds):
                        where_clauses.append(rev_keywords[word].label_+condition+" "+ label)
                        has_conds = False
                   
                    else: 
                        where_clauses.append(rev_keywords[word].label_+"= "+ label)
                    
                    used_keywords.append(rev_keywords[word])
                    used_keywords.append(keyword)
                    break
       
        prev_keyword = keyword
    
    return (where_clauses,used_keywords)



def getQuery(ls):
    
    has_conds = False
    has_cols = False
    is_agr = False
    
    for l in ls:
        if l._.span_type == "agr":
            is_agr = True
    where, usedColumns = getWhereClause(ls)
    print(usedColumns)
    tables = get_tables(ls)
    print("tables is ", tables)
    temp = []
    for l in ls:
            if l not in usedColumns:
                temp.append(l)
                print("added ", l)
    if is_agr or re.search("\*", get_columns(temp)):
   # if is_agr or re.search("\*", get_columns(temp)):
        for u in usedColumns:
            if u in ls:
                ls.remove(u)
                print("removed ", u)
            
    columns = get_columns(ls)
    if len(where) != 0:
        has_conds = True
    if len(columns) != 0:
        has_cols = True
    finalQuery = ""
 
    finalQuery += "SELECT " + columns + " "
        
    finalQuery += "FROM " + tables + " "
    
    if(has_conds):
        finalQuery += "WHERE "
        for cond in where:
            finalQuery += cond + " "

    final = [("cast("+ w +" as int)")  if re.match(r"[0-9]+", w) else w for w in list(finalQuery.split(" "))]
    finalfinal = " ".join(final)
    print("printing columns from getquery")
    print(columns)
    return (finalfinal, columns.split(','), tables.split(','))

def parse(str):
    nlp = spacy.load("en_core_web_sm")
    columnList = {}
    TableList = {}
    with open("columns.json", "r") as read_file:
        columnList = json.load(read_file)
        
    with open("tables.json", "r") as read_file:
        TableList = json.load(read_file)
    doc = nlp(str)
    doc.ents = ()
    matches = []
    keywords = []
    tag_expr_keywords(doc,matches,"value",r'("[^"]*")|([0-9]+)')
    tag_list_keywords(doc,matches,"table",TableList)
    tag_list_keywords(doc,matches,"agr",AgrList)
    tag_columns(doc,matches,columnList)
    tag_expr_keywords(doc,matches,"concat",r'\b(and|or)')
    tag_list_keywords(doc,matches,"cond",CondList)
    doc.ents = tuple(matches)
    
    for ent in doc.ents:
        keywords.append(ent)
   
    query = getQuery(keywords)
    print(query)

    return query

