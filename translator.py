import re
import hgtk

from googleapiclient import discovery

class Translator:
    
    def __init__(self, key, sheet_id):
        self.use_google_trans = True
        self.sheet_range = {}
        self.nouns_dict={}
        self.sheet_id = sheet_id
        self.service = discovery.build('sheets', 'v4', developerKey=key)
        
        request = self.service.spreadsheets().get(spreadsheetId=sheet_id)
        response = request.execute()

        for sheet in response['sheets']:
            title = sheet['properties']['title']
            rows = sheet['properties']['gridProperties']['rowCount']

            self.sheet_range[title] = rows

    def get_sheet_values(self, sheet_name, from_col, to_col, skip=0):
        range_ = "'%s'!%s1:%s%s" % (sheet_name, from_col, to_col, self.sheet_range[sheet_name]+1)

        value_render_option = 'FORMATTED_VALUE'  
        date_time_render_option = 'FORMATTED_STRING' 

        request = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range=range_, 
            valueRenderOption=value_render_option, 
            dateTimeRenderOption=date_time_render_option)
        response = request.execute()

        return response['values'][skip:]

    def get_best_trans(self, trans, id_col=0, default_col=1):
        if len(trans) > 4:
            key = trans[id_col]
            value = trans[-1].split('//')[0]
        elif self.use_google_trans and len(trans) == 4:
            key = trans[id_col]
            value = "[G] %s" % trans[-1].split('//')[0]
        else:
            key = trans[id_col]
            if len(trans) > default_col:
                value = trans[default_col]
            else:
                value = ''

        return key, value

    def replace_nouns(self, text):
        total_text = ""
        splited=text.split('@')

        for idx in range(1, len(splited), 2):
            word = splited[idx]
            if word in self.nouns_dict:
                word = self.nouns_dict[word]

            if idx+1 > len(splited)-1:
                total_text += word
                continue

            lefts = splited[idx+1]
            josa = re.findall(r"[\w']+", lefts)
            nexts = ""

            if josa:
                josa=josa[0]
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

    #self.replace_nouns('나는 d@Drowning-Pearl@을 @Drowning-Pearl@과 교환하려 @할a@로 @dsad@ 거야.')
    
    def load_noun(self):
        self.nouns_dict={}

        for row in self.get_sheet_values('proper_nouns', 'B', 'G'):
            if not row: continue

            k, v = self.get_best_trans(row, 1)
            self.nouns_dict[k] = v


    def load_translation(self, sheet_name):
        events_trans = {}
        current_table = {}

        for row in self.get_sheet_values(sheet_name, 'A', 'F', 3):
            if row[0].startswith('@DataMappingObjectV1Header'):
                current_table = {}

            elif row[0].startswith('@DataMappingObjectV1Footer'):
                events_trans[current_table['Id']] = current_table

            elif row[0].startswith('@Mapping(5)'):
                pass

            else:
                k, v = self.get_best_trans(row, 0)
                v = v.replace('\\', '')
                current_table[k] = self.replace_nouns(v)

        return events_trans


    def recusive_update(self, node, trans_dict):
        matched = 0
        unmatched = 0

        if type(node) == dict:
            if 'Id' in node:
                node_id = node['Id']
                trans = trans_dict.get(str(node_id), None)
                if trans:
                    matched += 1

                    node['Name'] = trans['Name']
                    node['Teaser'] = trans['Teaser']
                    node['Description'] = trans['Description']

                    if not node['Teaser']:
                        temp_teaset = node['Description'].split('.')[0][:40]
                        node['Teaser'] = temp_teaset
                else:
                    unmatched += 1

            for k, v in node.items():
                m, u = self.recusive_update(v, trans_dict)
                matched += m
                unmatched +=u

        elif type(node) == list:
            for item in node:
                m, u = self.recusive_update(item, trans_dict)
                matched += m
                unmatched +=u

        return matched, unmatched
