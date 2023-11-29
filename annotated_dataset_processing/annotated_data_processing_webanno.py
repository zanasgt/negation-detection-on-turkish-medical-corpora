# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 17:22:34 2023

@author: cardcentric
"""

import pandas as pd

def parse_neg_element(elements):
  result = [element.split('-')[-1] for element in elements]
  return result

def parse_webanno_tsv(tsv_path):
  # Read the TSV file into a DataFrame
  try:
    df = pd.read_csv(tsv_path, sep='\t', quoting=3, comment='#', header=None, skip_blank_lines=True)
  except pd.errors.ParserError as e:
    print(f"Error parsing TSV file: {e}")
    return
    
  df['sentence_id'] = df[0].str.split('-', expand=True)[0].astype(int)
  df['token_id'] = df[0].str.split('-', expand=True)[1]
  sentence_length = df['sentence_id'].max()
  # print(sentence_length)
  
  df_result = pd.DataFrame()
  columns = ['sentence_id', 'sentence', 'cue', 'cue_type', 'scope', 'scope_index', 'focus', 'focus_index', 'event', 'event_index', 'cp']
  
  # neg. type:  column 17
  # scope:      column 19
  # focus:      column 16
  # event:      column 14
  # cor. part.: column 12
  for i in range(1, sentence_length+1):
    df_sentence = df[df['sentence_id'] == i]
    sentence_text = ' '.join(df_sentence[2])
    
    if (df_sentence[20] == '*').any():
      df_negation = df_sentence[df_sentence[20] == '*']
      for index, row in df_negation.iterrows():
        negation_type   = df_negation[17]
        scope_elements  = parse_neg_element(row[19].split(';'))
        focus_elements  = parse_neg_element(row[16].split(';'))
        event_elements  = parse_neg_element(row[14].split(';'))
        cp_elements     = parse_neg_element(row[12].split(';'))
    else:
      b=5
      
    # Append data to df_result
    # df_result = df_result.append({
    #     'sentence_id': i,
    #     'sentence': sentence_text,
    #     'cue': cue,
    #     'cue_type': cue_type,
    #     'scope': scope,
    #     'scope_index': scope_index,
    #     'focus': focus,
    #     'focus_index': focus_index,
    #     'event': event,
    #     'event_index': event_index,
    #     'cp': cp
    # }, ignore_index=True)
    # print(df_negations)
  # Assuming WebAnno TSV format with columns: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
  # columns = ['ID', 'INDEX', 'TOKEN', 'isCP', 'isSCOPE', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
  # df.columns = columns

  # Process the DataFrame as needed
  # For example, you can access the 'FORM' and 'UPOS' columns
  # forms = df['FORM'].tolist()
  # upos_tags = df['UPOS'].tolist()
  # Print the parsed data
  # for form, upos in zip(forms, upos_tags):
  #    print(f'Word: {form}, UPOS: {upos}')
  return df
  
# Replace 'your_webanno_file.tsv' with the path to your WebAnno TSV file
a = parse_webanno_tsv(r'C:\Users\cardcentric\Downloads\756488.tsv')
