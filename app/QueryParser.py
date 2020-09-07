from spacy.lang.en import English
from spacy.pipeline import EntityRuler
# docker requrements
# pip install


def get_tags(str):

    nlp = English()
    ruler = EntityRuler(nlp)
    patterns = [{"label": "ID", "pattern": [{'TEXT': {'REGEX': "\d+"}}]},

                {"label": "EMAIL", "pattern": [
                    {'TEXT': {'REGEX': "[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}"}}]},
                {"label": "ORG", "pattern": [
                    {'TEXT': "University"},
                    {'TEXT': "of"},
                    {'TEXT': {'REGEX': "([A-Z]\w+ ?)"}},
                    {'TEXT': {'REGEX': "([A-Z]\w+ ?)"}},
                ]},
                {"label": "ORG", "pattern": [
                    {'TEXT': "University"},
                    {'TEXT': "of"},
                    {'TEXT': {'REGEX': "([A-Z]\w+ ?)"}},
                ]},
                {"label": "ORG", "pattern": [
                    {'TEXT': {'REGEX': "([A-Z]\w+ ?)"}},
                    {'TEXT': "University"},

                ]},
                {"label": "ORG", "pattern": [
                    {'TEXT': {'REGEX': "([A-Z]\w+ ?)"}},
                    {'TEXT': {'REGEX': "([A-Z]\w+ ?)"}},
                    {'TEXT': "University"},

                ]},

                {"label": "EMAIL_COL", "pattern": [
                    {'TEXT': "email"}]},
                {"label": "EMAIL_COL", "pattern": [
                    {'TEXT': "mail"}]},

                {"label": "FIRST_NAME_COL", "pattern": [
                    {'TEXT': "first"}, {'TEXT': "name"}]},
                {"label": "LAST_NAME_COL", "pattern": [
                    {'TEXT': "last"}, {'TEXT': "name"}]},

                {"label": "ID_COL", "pattern": [
                    {'TEXT': "ID"}]},
                {"label": "ID_COL", "pattern": [
                    {'TEXT': "Student"}, {'TEXT': "ID"}]},

                {"label": "ORG_COL", "pattern": [
                    {'TEXT': "university"}]},


                ]

    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    doc = nlp(str)
    return([(ent.text, ent.label_) for ent in doc.ents])


def create_query(str):
    keywords = get_tags(str)

    col_connections = {'ORG_COL': 'university', 'EMAIL_COL': 'email', 'ID_COL': 'student_id',
                       'FIRST_NAME_COL': 'first_name', 'LAST_NAME_COL': 'last_name'
                       ''}
    value_collections = {'ORG': 'university=',
                         'EMAIL': 'email=', 'ID': 'student_id='}

    column = ''
    condition = ''

    for (value, tag) in keywords:
        if(tag in col_connections.keys() and not column):
            column = col_connections[tag]
        elif(tag in value_collections.keys() and not condition):
            condition = value_collections[tag]+"'"+value+"'"

    return (stitch_query(column, condition),column.split(','))


def stitch_query(column, condition):
    column2 = ' Student_id,first_name '
    SELECT = 'SELECT '
    FROM = ' FROM Students '
    WHERE = 'WHERE '
    
    return  SELECT + column + FROM + WHERE + condition

