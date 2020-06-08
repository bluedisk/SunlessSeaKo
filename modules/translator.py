import json
import re

import hgtk
from googleapiclient import discovery


class Translator:

    def __init__(self, key, sheet_id):
        self.use_google_trans = True
        self.sheet_range = {}
        self.nouns_dict = {}
        self.nouns_list = []
        self.sheet_id = sheet_id
        self.service = discovery.build('sheets', 'v4', developerKey=key)

        request = self.service.spreadsheets().get(spreadsheetId=sheet_id)
        response = request.execute()

        for sheet in response['sheets']:
            title = sheet['properties']['title']
            rows = sheet['properties']['gridProperties']['rowCount']

            self.sheet_range[title] = rows

    def get_sheet_values(self, sheet_name, from_col, to_col, skip=0):
        range_ = "'%s'!%s1:%s%s" % (sheet_name, from_col, to_col, self.sheet_range[sheet_name] + 1)

        value_render_option = 'FORMATTED_VALUE'
        date_time_render_option = 'FORMATTED_STRING'

        request = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range=range_,
            valueRenderOption=value_render_option,
            dateTimeRenderOption=date_time_render_option)
        response = request.execute()

        return response['values'][skip:]

    def get_best_trans(self, trans, id_col=0, default_col=1):
        while trans and not trans[-1].strip():
            trans = trans[:-1]

        if len(trans) > 4:
            key = trans[id_col]
            value = trans[-1].split('//')[0]
        elif self.use_google_trans and len(trans) == 4:
            key = trans[id_col]
            value = "G: %s" % trans[-1].split('//')[0]
        else:
            key = trans[id_col]
            if len(trans) > default_col:
                value = trans[default_col]
            else:
                value = ''

        return key, value

    def replace_nouns(self, text):
        total_text = ""
        splited = text.split('@')

        for idx in range(1, len(splited), 2):
            word = splited[idx]
            if word in self.nouns_dict:
                word = self.nouns_dict[word]

            if idx + 1 > len(splited) - 1:
                total_text += word
                continue

            lefts = splited[idx + 1]
            josa = re.findall(r"[\w']+", lefts)
            nexts = ""

            if josa:
                josa = josa[0]
                nexts = lefts[len(josa):]
                josa_type = hgtk.josa.get_josa_type(josa)

                if josa_type:
                    word = hgtk.josa.attach(word, josa_type)
                    total_text += word + nexts
                else:
                    total_text += word + lefts
            else:
                total_text += word + lefts

        return splited[0] + total_text

    # self.replace_nouns('나는 d@Drowning-Pearl@을 @Drowning-Pearl@과 교환하려 @할a@로 @dsad@ 거야.')

    def load_noun(self, filename=None):

        if filename:
            with open(filename) as f:
                self.nouns_dict = json.load(f)
                self.nouns_list = self.nouns_dict.keys()
            return

        # load from google
        self.nouns_dict = {}
        self.nouns_list = []

        for row in self.get_sheet_values('proper_nouns', 'A', 'G'):
            if not row:
                continue

            row = row + [''] * (7 - len(row))
            cate, _, key, reference, google, translate, final = row

            self.nouns_dict[key] = {
                "cate": cate,
                "origin": key,
                "reference": reference,
                "google": google,
                "translate": translate,
                "final": final
            }

        self.nouns_list = tuple(self.nouns_dict.keys())

    def nouns(self):
        return self.nouns_dict

    def save_noun(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.nouns_dict, f)

    def encode_nouns(self, text):
        for idx, key in enumerate(self.nouns_list):
            text = re.sub(r'\b%s\b' % key, 'n_%04d' % idx, text, flags=re.IGNORECASE)

        return text

    def decode_nouns(self, text):
        noun_ids = [int(idx) for idx in re.findall(r'n_([0-9]{4})', text)]

        for idx in noun_ids:
            key = self.nouns_list[idx]
            val = (self.nouns_dict[key]['final'] or
                   self.nouns_dict[key]['translate'] or
                   self.nouns_dict[key]['google'] or key)

            text = re.sub('n_%04d' % idx, "@%s@" % val, text)

        text = self.replace_nouns(text)
        return text

    def load_translation(self, sheet_name):
        events_trans = {}
        current_table = {}

        for row in self.get_sheet_values(sheet_name, 'A', 'F', 3):
            if row[0].startswith('@DataMappingObjectV1Header'):
                current_table = {}

            elif row[0].startswith('@DataMappingObjectV1Footer'):
                if current_table['Id'] in events_trans:
                    events_trans[current_table['Id']].append(current_table)
                else:
                    events_trans[current_table['Id']] = [current_table]

            elif row[0].startswith('@Mapping(5)'):
                pass

            else:
                k, v = self.get_best_trans(row, 0)
                v = v.replace('\\"', '"')
                v = v.replace('\\r\\n', '\r\n')
                v = v.replace('"\\', '"')
                current_table[k] = self.replace_nouns(v)

                if k == 'Name':
                    if len(row) > 1 and row[1]:
                        ov = row[1]
                        ov = ov.replace('\\"', '"')
                        ov = ov.replace('\\r\\n', '\r\n')
                        ov = ov.replace('"\\', '"')

                        current_table["Name_origin"] = ov
                    else:
                        current_table["Name_origin"] = ''

        return events_trans

    def _clean_data(self, text):
        text = text.replace('\\"', '"')
        text = text.replace('\\r\\n', '\r\n')
        text = text.replace('"\\', '"')

        return text

    def load_all(self, sheet_name):
        events_trans = {}
        current_table = {}

        for row in self.get_sheet_values(sheet_name, 'A', 'F', 3):
            if row[0].startswith('@DataMappingObjectV1Header'):
                current_table = {
                    "origin": {}, "reference": {},
                    "google": {}, "translate": {},
                    "final": {}
                }

            elif row[0].startswith('@DataMappingObjectV1Footer'):
                if current_table['origin']['Id'] in events_trans:
                    events_trans[current_table['origin']['Id']].append(current_table)
                else:
                    events_trans[current_table['origin']['Id']] = [current_table]

            elif row[0].startswith('@Mapping(5)'):
                pass

            else:
                key, origin, reference, google, translate, final = row + [''] * (6 - len(row))
                key = key.strip()

                for target in current_table.keys():
                    current_table[target][key] = self._clean_data(locals()[target])

        return events_trans
