# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 22:22:38 2023

@author: cardcentric
"""

from cassis import *

class AnnotationData:
  def __init__(self):
    self.documents = []
    self.negation_count = {
        "morphological": 0,
        "lexical": 0,
        "syntactical": 0,
        "_me": 0,
        "_sız": 0
        }
    self.multi_negation_count = 0

  def add_document(self, document):
    self.documents.append(document)

  def process_all_documents(self, resetIndexes = True):
    dataset = []
    for document in self.documents:
      dataset.append(document.process(resetIndexes))
    return dataset
  
class Document():
  def __init__(self, xmi_path, typesystem_path, dataset: AnnotationData):
    self.xmi_path = xmi_path
    self.typesystem_path = typesystem_path
    self.cas = None
    self.negation_count = {}
    self.dataset = dataset

  def load(self):
    with open(self.typesystem_path, 'rb') as f:
      typesystem = load_typesystem(f)

    with open(self.xmi_path, 'rb') as f:
      self.cas = load_cas_from_xmi(f, typesystem=typesystem)

  def load_negation_features(self, feature_list):
    if feature_list:
      result = []
      for item in feature_list:
        begin = item.target.begin
        end = item.target.end
        tar_text = item.target.get_covered_text()
        result.append((begin, end, tar_text))
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
      neg_type = neg_marker.markerType
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
        "neg_marker": neg_marker.get_covered_text(),
        "neg_marker_begin": neg_marker.begin,
        "neg_marker_end": neg_marker.end,
        "neg_marker_type": neg_marker.markerType,
        "neg_scope": neg_scope,
        "neg_focus": neg_focus,
        "neg_event": neg_event,
        "neg_coor_part": neg_coordination_particle
      }
      neg_in_doc.append(neg)
    #print(neg_in_doc[2])
    return neg_in_doc
  
  def count_negation(self, neg_marker: dict):
    if neg_marker["neg_marker_type"] == 'NegMorMarker':
      self.dataset.negation_count["morphological"] += 1
    elif neg_marker["neg_marker_type"] == 'NegLexMarker':
      self.dataset.negation_count["lexical"] += 1
    elif neg_marker["neg_marker_type"] == 'NegSynMarker':
      self.dataset.negation_count["syntactical"] += 1
    else:
      print(f'Type error with {neg_marker["neg_marker"]}...\n')
    
    if neg_marker["neg_marker"] == 'ma' or neg_marker["neg_marker"] == 'me' or neg_marker["neg_marker"] == 'mı' or neg_marker["neg_marker"] == 'mi':
      self.dataset.negation_count["_me"] += 1
    elif neg_marker["neg_marker"] == 'sız' or neg_marker["neg_marker"] == 'siz' or neg_marker["neg_marker"] == 'suz' or neg_marker["neg_marker"] == 'süz':
      self.dataset.negation_count["_sız"] += 1
  
  def find_tokens(self,sentence, reset_indexes = True):
    token_id = 0
    result = []
    token_dict ={}
    for token in self.cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'):
      if token.begin >= sentence.begin and token.end <= sentence.end:
        token_dict = {
          "token_id": token_id,
          "token": token.get_covered_text(),
          "token_begin": token.begin - sentence.begin,
          "token_end": token.end - sentence.begin,
          "neg_cue_type": '',
          "is_scope": False,
          "is_focus": False,
          "is_event": False
        }

        #sentence_dict["tokens"].append(token_dict)
        token_id += 1
        result.append(token_dict)
    return result

  def process(self, reset_indexes=True):
    if self.cas is None:
      raise ValueError("Document not loaded. Call load() first.")
    else:
      negations_in_doc = self.extract_elements_of_marker()
      dataset_dict = []
      sentence_id = 0
      
      
      for sentence in self.cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):   
        sentence_dict = {}
        sentence_neg_markers = [item for item in negations_in_doc 
                            if sentence.begin <= item["neg_marker_begin"] <= sentence.end]
        token_id = 0
        
            
          
        if len(sentence_neg_markers)>1:
          for neg_marker in sentence_neg_markers:
            sentence_dict = {}
            sentence_dict["sentence_id"] = sentence_id
            sentence_dict["text"] = sentence.get_covered_text()
            sentence_dict["sentence_begin"] = 0 if reset_indexes else sentence.begin
            sentence_dict["sentence_end"] = sentence.end - sentence.begin if reset_indexes else sentence.end
            sentence_dict["items"] = neg_marker
            sentence_dict["tokens"] = self.find_tokens(sentence)
            
            dataset_dict.append(sentence_dict)
            sentence_id += 1
            self.count_negation(neg_marker)
          self.dataset.multi_negation_count = self.dataset.multi_negation_count + 1
            
        elif len(sentence_neg_markers) == 1:
          sentence_dict["sentence_id"] = sentence_id
          sentence_dict["text"] = sentence.get_covered_text()
          sentence_dict["sentence_begin"] = 0 if reset_indexes else sentence.begin
          sentence_dict["sentence_end"] = sentence.end - sentence.begin if reset_indexes else sentence.end
          sentence_dict["items"] = sentence_neg_markers[0]
          sentence_dict["tokens"] = self.find_tokens(sentence, reset_indexes)
          
          dataset_dict.append(sentence_dict)
          sentence_id += 1
          self.count_negation(neg_marker)
          
        else:
          sentence_dict["sentence_id"] = sentence_id
          sentence_dict["text"] = sentence.get_covered_text()
          sentence_dict["sentence_begin"] = 0 if reset_indexes else sentence.begin
          sentence_dict["sentence_end"] = sentence.end - sentence.begin if reset_indexes else sentence.end
          sentence_dict["items"] = {}
          sentence_dict["tokens"] = self.find_tokens(sentence, reset_indexes)
          
          dataset_dict.append(sentence_dict)
          sentence_id += 1
        
    return dataset_dict

      

if __name__ == "__main__":
    annotation_data = AnnotationData()

    # Replace these paths with your actual file paths
    xmi_paths = [r'C:\Users\cardcentric\Downloads\796005\796005.xmi']
    typesystem_paths = [r"C:\Users\cardcentric\Downloads\796005\TypeSystem.xml"]

    for xmi_path, typesystem_path in zip(xmi_paths, typesystem_paths):
        document = Document(xmi_path, typesystem_path, annotation_data)
        document.load()
        annotation_data.add_document(document)

    dataset = annotation_data.process_all_documents(resetIndexes=False)
    print(annotation_data.negation_count, annotation_data.multi_negation_count)