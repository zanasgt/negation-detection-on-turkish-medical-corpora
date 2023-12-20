# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 22:22:38 2023

@author: cardcentric
"""

from cassis import *
from dkpro_cassis_tools import load_cas_from_zip_file
import pandas as pd
import os

class AnnotationData:
  def __init__(self):
    self.documents = []
    self.document_number = 1
    self.dictionery_dataset = []
    self.sentence_dataset = pd.DataFrame(columns=['sentence_id', 'sentence_text', 'cue', 'scope', 'focus', 'event'])
    self.labeled_dataset = pd.DataFrame(columns=['sentence_id', 'sentence_set_id', 
                                           'token_id', 'token', 'token_index', 
                                           'cue', 'cue_type', 'cue_index', 'cue_label',
                                           'scope', 'scope_index', 'scope_label',
                                           'focus', 'focus_index', 'focus_label',
                                           'event', 'event_index', 'event_label',
                                           'cp', 'cp_index', 'cp_label'])
    # this part will be done with data visualization on DataFrame
    # self.negation_count = {
    #     "morphological": 0,
    #     "lexical": 0,
    #     "syntactical": 0,
    #     "_me": 0,
    #     "_sız": 0
    #     }
    # self.multi_negation_count = 0

  def add_document(self, document):
    document.sentence_dataset['document_number'] = self.document_number
    document.labeled_dataset['document_number'] = self.document_number
    self.sentence_dataset = pd.concat([self.sentence_dataset, document.sentence_dataset], axis=0, join='outer')
    self.labeled_dataset = pd.concat([self.labeled_dataset, document.labeled_dataset], axis=0, join='outer')
    
    self.documents.append(document)
    self.document_number += 1
    print("Document negations added to dataset..")
    
  def process_all_documents(self, resetIndexes = True):
    doc_number = 0
    for document in self.documents:
      # self.sentence_dataset = pd.concat([self.sentence_dataset, document.sentence_dataset], axis=0, join='outer')
      # self.labeled_dataset = pd.concat([self.labeled_dataset, document.labeled_dataset], axis=0, join='outer')
      self.sentence_dataset.insert(0, 'doc_number', doc_number)
      self.labeled_dataset.insert(0, 'doc_number', doc_number)
      doc_number += 1
      print("Document negations added to dataset..")
      # self.labeled_dataset = labeled_dataset
      # print("Labeled results added to dataset..")
      # self.indexed_dataset = indexed_dataset
      # print("İndexed results added to dataset..")
      # self.detail_dataset = detailed_dataset
      # print("Detailed results added to dataset..")
  
class Document():
  def __init__(self, xmi_path, dataset: AnnotationData):
    self.xmi_path = xmi_path
    # self.typesystem_path = typesystem_path
    self.cas = None
    self.load()
    self.sentence_dataset = pd.DataFrame()
    self.labeled_dataset = pd.DataFrame()
    self.process()
  def load(self):
    with open(xmi_path, 'rb') as f:
      self.cas = load_cas_from_zip_file(f)
    # with open(self.typesystem_path, 'rb') as f:
    #   typesystem = load_typesystem(f)

    # with open(self.xmi_path, 'rb') as f:
    #   self.cas = load_cas_from_xmi(f, typesystem=typesystem)

  def load_negation_features(self, feature_list):
    if feature_list:
      result = []
      for item in feature_list:
        item = {'begin': item.target.begin, 
                'end': item.target.end,
                'text': item.target.get_covered_text()}
        # begin = item.target.begin
        # end = item.target.end
        # tar_text = item.target.get_covered_text()
        result.append(item)
        # incase if needed as we will recor those feature by neme later
        #tar_type = item.target.type.name.split('.')[-1]
        #feature = {
        #  "type":   tar_type,
        #  "begin":  begin,
        #  "end":    end,
        #  "text":   tar_text}
      return result
    else:
      return None
  
  def extract_elements_of_marker(self):
    neg_in_doc = []
    for neg_marker in self.cas.select('webanno.custom.NegationMarker'):
      neg_cue = {"type" : neg_marker.markerType,
                 "begin" : neg_marker.begin,
                 "end" : neg_marker.end,
                 "text" : neg_marker.get_covered_text()}
      neg_coordination_particle_ = neg_marker.coordinationparticle.elements
      neg_coordination_particle = self.load_negation_features(neg_coordination_particle_)
      neg_event_ = neg_marker.event.elements
      neg_event = self.load_negation_features(neg_event_)
      neg_focus_ = neg_marker.focus.elements
      neg_focus = self.load_negation_features(neg_focus_)
      neg_scope_ = neg_marker.scope.elements
      neg_scope = self.load_negation_features(neg_scope_)
      '''
      print(neg_type)
      print(neg_marker.get_covered_text())
      print('coordination particle:\n', (f'{x[0]},{x[1]}' for x in neg_coordination_particle) 
            if neg_coordination_particle is not None else 'No coordination partical')
      print('event:\n', (f'{x[0]},{x[1]}' for x in neg_event if neg_event) 
            if neg_event is not None else 'No event')
      print('focus:\n', (f'{x[0]},{x[1]}' for x in neg_focus)
            if neg_focus is not None else 'No focus')
      print('scope:\n', (f'{x[0]},{x[1]}' for x in neg_scope) 
            if neg_scope is not None else 'No scope')
      '''
      neg = {
        "cue": neg_cue,
        "scope": neg_scope,
        "focus": neg_focus,
        "event": neg_event,
        "coor_part": neg_coordination_particle
      }
      neg_in_doc.append(neg)
    #print(neg_in_doc[2])
    return neg_in_doc
  
  # This part will be done with data visualization part
  # def count_negation(self, neg_marker: dict):
  #   if neg_marker["neg_marker_type"] == 'NegMorMarker':
  #     self.dataset.negation_count["morphological"] += 1
  #   elif neg_marker["neg_marker_type"] == 'NegLexMarker':
  #     self.dataset.negation_count["lexical"] += 1
  #   elif neg_marker["neg_marker_type"] == 'NegSynMarker':
  #     self.dataset.negation_count["syntactical"] += 1
  #   else:
  #     print(f'Type error with {neg_marker["neg_marker"]}...\n')
    
  #   if neg_marker["neg_marker"] == 'ma' or neg_marker["neg_marker"] == 'me' or neg_marker["neg_marker"] == 'mı' or neg_marker["neg_marker"] == 'mi':
  #     self.dataset.negation_count["_me"] += 1
  #   elif neg_marker["neg_marker"] == 'sız' or neg_marker["neg_marker"] == 'siz' or neg_marker["neg_marker"] == 'suz' or neg_marker["neg_marker"] == 'süz':
  #     self.dataset.negation_count["_sız"] += 1
  
  # def find_token_features(self,sentence, reset_indexes = True):
  #   token_id = 0
  #   result = []
  #   token_dict ={}
  #   for token in self.cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'):
  #     if token.begin >= sentence.begin and token.end <= sentence.end:
  #       token_dict = {
  #         "token_id": token_id,
  #         "token": token.get_covered_text(),
  #         "begin": token.begin - sentence.begin,
  #         "end": token.end - sentence.begin
  #       }

  #       #sentence_dict["tokens"].append(token_dict)
  #       token_id += 1
  #       result.append(token_dict)
  #   return result

  def process(self, reset_indexes=True):
    if self.cas is None:
      raise ValueError("Document not loaded.")
    else:
      def find_token_feature(token_text, token_index, feature_index):
        index = (0, 0)
        if token_index[0] < feature_index[0]:
          if token_index[1] < feature_index[1]:
            index = (feature_index[0], token_index[1])
            token_feature_text = token_text[feature_index[0]-token_index[0]:token_index[1]-token_index[0]]
          else:
            index = (feature_index[0], feature_index[1])
            token_feature_text = token_text[feature_index[0]-token_index[0]:feature_index[1]-token_index[0]]
        else:
          if token_index[1] > feature_index[1]:
            index = (token_index[0], feature_index[1])
            token_feature_text = token_text[token_index[0]-token_index[0]:feature_index[1]-token_index[0]]
          else:
            index = (token_index[0], token_index[1])
            token_feature_text = token_text[0:token_index[1]-token_index[0]]
        return token_feature_text, index
      
      def is_include(token_index, feature_index):
        return not (feature_index[1] <= token_index[0] or feature_index[0] >= token_index[1])
      #(token_index[1] > feature_index[0] >= token_index[0]) or (feature_index[0] <= token_index[0] < feature_index[1])
      
      def split_features(feature_dict: dict, feature_name):
        if type(feature_dict[feature_name]) is type(None):
          return []
        elif type(feature_dict[feature_name]) is list:
          return feature_dict[feature_name]
        else:
          return [feature_dict[feature_name]]
      
      sentence_dataset = pd.DataFrame(columns=['sentence_id', 'sentence_set_id', 'sentence_text', 
                                               'cue', 'scope', 'focus', 'event', 'coor_part'])
      
      labeled_dataset = pd.DataFrame(columns=['sentence_id', 'sentence_set_id', 
                                             'token_id', 'token', 'token_index', 
                                             'cue', 'cue_type', 'cue_index', 'cue_label',
                                             'scope', 'scope_index', 'scope_label',
                                             'focus', 'focus_index', 'focus_label',
                                             'event', 'event_index', 'event_label',
                                             'cp', 'cp_index', 'cp_label'])
      
      # extract negation markers and its features
      negations_in_doc = self.extract_elements_of_marker()
      
      dataset_dict = []
      sentence_id = 0
      sentence_set_id = 0
      processed_token_index = 0
      
      # Sort tokens based on their 'begin' values it is already sorted in xmi
      # tokens.sort(key=lambda x: x.begin)
      
      tokens = self.cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token')
      for sentence in self.cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        if sentence.get_covered_text() == "GİRİŞ" or sentence.get_covered_text() =="İÇERİK" or sentence.get_covered_text() =="ÖZET":
          processed_token_index += 1
          pass
        else:
          sentence_tokens = []
          for token in tokens:
            print(token.begin, sentence.begin, sentence.end)
            if token.begin >= sentence.end or token.end < sentence.begin:
              processed_token_index =+ 1
              pass
            if sentence.begin <= token.begin < sentence.end:
              sentence_tokens.append(token)
              processed_token_index += 1
              print(token.get_covered_text())
            if token.begin > sentence.end:
              break
          
          tokens = tokens[processed_token_index:]
          
          sentence_neg_markers = [item for item in negations_in_doc 
                              if sentence.begin <= item["cue"]["begin"] <= sentence.end]
          
          if len(sentence_neg_markers):
            for neg_marker in sentence_neg_markers:
              cues = split_features(neg_marker, "cue") # neg_marker["cue"] if type(neg_marker["cue"]) is list else [neg_marker["cue"]]
              scopes = split_features(neg_marker, "scope") # neg_marker["scope"] if type(neg_marker["scope"]) is list else [neg_marker["scope"]]
              focuses = split_features(neg_marker, "focus") # neg_marker["focus"] if type(neg_marker["focus"]) is list else [neg_marker["focus"]]
              events = split_features(neg_marker, "event") # neg_marker["event"] if type(neg_marker["event"]) is list else [neg_marker["event"]]
              coor_parts = split_features(neg_marker, "coor_part") #neg_marker["coor_part"] if type(neg_marker["coor_part"]) is dict else [neg_marker["coor_part"]]
              
              sentence_dataset_dict = {"sentence_id" : sentence_id, 
                                       "sentence_set_id" : sentence_set_id,
                                       "sentence_text" : sentence.get_covered_text(), 
                                       "cue" : cues,
                                       "scope" : scopes,
                                       "focus" : focuses,
                                       "event" : events,
                                       "coor_part" : coor_parts}
              sentence_dataset.loc[len(sentence_dataset)] = sentence_dataset_dict
              
              is_first_token_scope = True
              is_first_token_focus = True
              is_first_token_event = True
              is_first_token_cp = True
              token_id = 0
              for token in sentence_tokens:
                print(token.begin, token.end, token.get_covered_text(), token.order, token.parent)
                token_index = (token.begin, token.end)
                token_text = token.get_covered_text()
                token_cue_index = None 
                token_cue_text = None 
                token_cue_type = None
                token_scope_index = None
                token_scope_text = None
                token_focus_index = None
                token_focus_text = None
                token_event_index = None
                token_event_text = None
                token_cp_index = None
                token_cp_text = None
                token_cue_label = 'O'
                token_scope_label = 'O'
                token_focus_label = 'O'
                token_event_label = 'O'
                token_cp_label = 'O'
                
                token_scope_texts = []
                token_focus_texts = []
                token_event_texts = []
                token_cp_texts = []
                token_scope_indexes = []
                token_focus_indexes = []
                token_event_indexes = []
                token_cp_indexes = []
                
                
                for cue in cues:
                  cue_index = (cue["begin"], cue["end"])
                  cue_text = cue["text"]
                  cue_type = cue["type"]
                  if is_include(token_index, cue_index):
                    token_cue_text, token_cue_index = find_token_feature(token_text, token_index, cue_index)
                    token_cue_type = cue["type"]
                    token_cue_label = f'B_{token_cue_type}'
                    
                    
                for scope in scopes:
                  scope_index = (scope["begin"], scope["end"])
                  scope_text = scope["text"]
                  if is_include(token_index, scope_index):
                    token_scope_text, token_scope_index = find_token_feature(token_text, token_index, scope_index)
                    token_scope_texts.append(token_scope_text)
                    token_scope_indexes.append(token_scope_index)
                    if is_first_token_scope:
                      token_scope_label = 'B_scope'
                      is_first_token_scope = False
                    else:
                      token_scope_label = 'I_scope'
                                
                for focus in focuses:
                  focus_index = (focus["begin"], focus["end"])
                  focus_text = focus["text"]
                  if is_include(token_index, focus_index):
                    token_focus_text, token_focus_index = find_token_feature(token_text, token_index, focus_index)
                    token_focus_texts.append(token_focus_text)
                    token_focus_indexes.append(token_focus_index)
                    if is_first_token_focus:
                      token_focus_label = 'B_focus'
                      is_first_token_focus = False
                    else:
                      token_focus_label = 'I_focus'
                    
                for event in events:
                  event_index = (event["begin"], event["end"])
                  event_text = event["text"]
                  if is_include(token_index, event_index):
                    token_event_text, token_event_index = find_token_feature(token_text, token_index, event_index)
                    token_event_texts.append(token_event_text)
                    token_event_indexes.append(token_event_index)
                    if is_first_token_event:
                      token_event_label = 'B_event'
                      is_first_token_event = False
                    else:
                      token_event_label = 'I_event'
                                      
                for coor_part in coor_parts:
                  cp_index = (coor_part["begin"], coor_part["end"])
                  cp_text = coor_part["text"]
                  if is_include(token_index, cp_index):
                    token_cp_text, token_cp_index = find_token_feature(token_text, token_index, cp_index)
                    token_cp_texts.append(token_cp_text)
                    token_cp_indexes.append(token_cp_index)
                    if is_first_token_cp:
                      token_cp_label = 'B_cp'
                      is_first_token_cp = False
                    else:
                      token_cp_label = 'I_cp'
                    
                labeled_dataset_dict = {"sentence_id" : sentence_id, "sentence_set_id" : sentence_set_id,
                                          "token_id" : token_id, "token" : token.get_covered_text(), 
                                          "token_index" : (token.begin, token.end), 
                                          "cue" : token_cue_text, "cue_type" : token_cue_type, "cue_index" : token_cue_index,
                                          "cue_label" : token_cue_label,
                                          "scope" : ('|').join(text for text in token_scope_texts) if len(token_scope_texts) > 0 else token_scope_text, 
                                          "scope_index" : token_scope_indexes if len(token_scope_indexes) > 0 else token_scope_index,
                                          "scope_label" : token_scope_label,
                                          "focus" : ('|').join(text for text in token_focus_texts) if len(token_focus_texts) > 0 else token_focus_text, 
                                          "focus_index" : token_focus_indexes if len(token_focus_indexes) > 0 else token_focus_index,
                                          "focus_label" : token_focus_label,
                                          "event" : ('|').join(text for text in token_event_texts) if len(token_event_texts) > 0 else token_event_text, 
                                          "event_index" : token_event_indexes if len(token_event_indexes) > 0 else token_event_index,
                                          "event_label" : token_event_label,
                                          "cp" : ('|').join(text for text in token_cp_texts) if len(token_cp_texts) > 0 else token_cp_text, 
                                          "cp_index" : token_cp_indexes if len(token_cp_indexes) > 0 else token_cp_index,
                                          "cp_label" : token_cp_label}
                  
                labeled_dataset.loc[len(labeled_dataset)] = labeled_dataset_dict
                token_id = token_id + 1
              
              sentence_id = sentence_id + 1
            sentence_tokens = []
            sentence_set_id = sentence_set_id + 1
          else:
            sentence_dataset_dict = {"sentence_id" : sentence_id,
                                     "sentence_set_id" : sentence_set_id,
                                     "sentence_text" : sentence.get_covered_text(), 
                                     "cue" : None,
                                     "scope" : None,
                                     "focus" : None,
                                     "event" : None,
                                     "coor_part" : None}
            sentence_dataset.loc[len(sentence_dataset)] = sentence_dataset_dict
            
            token_id = 0
            for token in sentence_tokens:
              print(token.begin, token.end, token.get_covered_text(), token.order, token.parent)
              token_index = (token.begin, token.end)
              token_text = token.get_covered_text()
              token_cue_index = None
              token_cue_text = None
              token_cue_type = None
              token_scope_index = None
              token_scope_text = None
              token_focus_index = None
              token_focus_text = None
              token_event_index = None
              token_event_text = None
              token_cp_index = None
              token_cp_text = None
              token_cue_label = 'O'
              token_scope_label = 'O'
              token_focus_label = 'O'
              token_event_label = 'O'
              token_cp_label = 'O'
              labeled_dataset_dict = {"sentence_id" : sentence_id, "sentence_set_id" : sentence_set_id,
                                        "token_id" : token_id, "token" : token.get_covered_text(), 
                                        "token_index" : (token.begin, token.end), 
                                        "cue" : token_cue_text, "cue_type" : token_cue_type, "cue_index" : token_cue_index,
                                        "cue_label" : token_cue_label,
                                        "scope" : token_scope_text, 
                                        "scope_index" : token_scope_index,
                                        "scope_label" : token_scope_label,
                                        "focus" : token_focus_text, 
                                        "focus_index" : token_focus_index,
                                        "focus_label" : token_focus_label,
                                        "event" : token_event_text, 
                                        "event_index" : token_event_index,
                                        "event_label" : token_event_label,
                                        "cp" : token_cp_text, 
                                        "cp_index" :  token_cp_index,
                                        "cp_label" : token_cp_label}
                
              labeled_dataset.loc[len(labeled_dataset)] = labeled_dataset_dict
              token_id = token_id + 1
            sentence_id = sentence_id + 1
            sentence_set_id = sentence_set_id + 1
          sentence_tokens = []
    self.sentence_dataset = sentence_dataset
    self.labeled_dataset = labeled_dataset

      

if __name__ == "__main__":
  root_dir = os.path.join(os.getcwd(), 'annotated-dataset-xmi')
  annotation_data = AnnotationData()
  
  for (dirpath, dirnames, filenames) in os.walk(root_dir):
    for filename in filenames:
      xmi_path = os.path.join(dirpath, filename)
      document = Document(xmi_path, annotation_data)
      annotation_data.add_document(document)