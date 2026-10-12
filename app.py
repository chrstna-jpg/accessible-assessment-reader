import json, os, re, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
ROOT=Path(__file__).parent
RUBRIC={'Focus': {'4': 'Text is clearly focused on a topic or idea and is developed throughout.', '3': 'Text is mostly focused on a topic or idea and developed throughout.', '2': 'Text may occasionally lose focus or lack development.', '1': 'Text is unfocused, confusing, or too short.', '0': 'The text gets no credit if it does not demonstrate adequate command of the traits of the mode of writing.'}, 'Organization': {'4': 'Text is well-organized with a logical structure/sequence and clear transitions.', '3': 'Text is organized with a mostly logical structure/sequence but may lack effective transitions.', '2': 'Text is somewhat unclear or difficult to follow and may lack transitions.', '1': 'Text has little or no structure or sequence of events.', '0': 'The text gets no credit if it does not demonstrate adequate command of the traits of the mode of writing.'}, 'Development': {'4': 'Text includes thorough and effective details, description, dialogue, evidence, and/or text features.', '3': 'Text includes adequate use of details, description, dialogue, evidence, and/or text features.', '2': 'Text includes few details and minimal description, dialogue, evidence, and/or text features.', '1': 'Text includes few or no details, little or no description, dialogue, evidence, and/or text features.', '0': 'The text gets no credit if it does not demonstrate adequate command of the traits of the mode of writing.'}, 'Language and Vocabulary': {'4': 'Text uses precise, relevant, and accurate language and/or domain-specific vocabulary.', '3': 'Text uses mostly precise, relevant, and accurate language and/or domain-specific vocabulary.', '2': 'Text may use overly general or imprecise/inaccurate language and/or domain-specific vocabulary.', '1': 'Text uses vague, unclear, or confusing language.', '0': 'The text gets no credit if it does not demonstrate adequate command of the traits of the mode of writing.'}, 'Conventions': {'4': 'Text has correct grammar, usage, spelling, capitalization, and punctuation.', '3': 'Text has a few conventions errors but is mostly clear and coherent.', '2': 'Text has conventions errors that may affect clarity.', '1': 'Text is hard to follow because of frequent errors.', '0': 'The text gets no credit if it does not demonstrate adequate command of the traits of the mode of writing.'}}
PROMPT='''You are a teacher-facing Grade 5 narrative-writing rubric reviewer, not a final grader. Apply ONLY the five supplied criteria and their exact 0–4 descriptions. Assess the student's original text without inventing or improving it. Keep Focus, Organization, Development, Language and Vocabulary, and Conventions distinct: grammar/spelling/punctuation belong under Conventions, not automatically under other criteria. For Development, evidence means narrative details, description, and other relevant features, not citations. Quote brief exact phrases from the response when possible, or explicitly state that evidence is absent. Do not automatically award zero for a short response; apply the actual descriptors and flag ambiguity for teacher review. Return ONLY JSON: {"criteria":[{"name":"Focus","score":0,"evidence":"...","rationale":"..."}, ...],"review_note":"..."}. Include each supplied criterion exactly once. Scores are integers from 0 through 4 and are provisional.''' 
ANALYZE='''Analyze the student's narrative response against the five supplied rubric criteria without assigning scores. For each criterion, cite brief exact evidence from the student's text and note what is missing or unclear. Keep writing content separate from conventions. Do not infer missing ideas. Return ONLY JSON: {"criteria":[{"name":"Focus","observed_evidence":"...","missing_or_unclear":"..."}, ...]}. Include every supplied criterion exactly once.''' 
SCORE2='''You are a teacher-facing rubric reviewer. Use the supplied original student response, exact rubric descriptions (0–4), and intermediate evidence analysis to suggest a score for each of the five criteria. Verify intermediate claims against the original response; do not treat them as infallible. Keep content criteria separate from Conventions. Do not invent evidence. Return ONLY JSON: {"criteria":[{"name":"Focus","score":0,"evidence":"...","rationale":"..."}, ...],"review_note":"..."}. Include every criterion exactly once; scores must be integers from 0 to 4. Teacher makes final decision.''' 


# Refined V2 is an additional workflow; original V1 and initial V2 remain unchanged.
ANALYZE_REFINED = """You are performing STAGE 1 of a two-stage teacher-facing Grade 5 narrative rubric review. Do NOT score. Analyze the COMPLETE original student response, not just one sentence per criterion. For each of the five rubric criteria, collect multiple brief VERBATIM excerpts when available (maximum 5), identify specific strengths, and identify actual gaps without inventing them. Organization: inspect the entire event sequence and all transition words (including First, Then, At first, When, By the end). Development: inspect all sensory details, comparisons, actions, feelings, and descriptions; do not ignore evidence elsewhere in the paragraph. Focus: assess consistency of the journey topic and comparison task. Language and Vocabulary: assess word precision separately from grammar. Conventions: ONLY assess grammar, usage, spelling, capitalization, and punctuation. Identify exact erroneous text and describe the error if any exists; if none is identifiable, explicitly state 'No identifiable conventions errors' and do not criticize vocabulary simplicity, sentence complexity, or length under Conventions. Do not equate lack of sophistication with an error. Do not demand dialogue if the rubric allows description and/or other narrative features. Return ONLY JSON: {"criteria":[{"name":"Focus","observed_evidence":"verbatim excerpts and observations","missing_or_unclear":"specific limitations or none"}, ...]}. Include each supplied criterion exactly once."""
SCORE_REFINED = """You are performing STAGE 2 of a two-stage teacher-facing Grade 5 narrative rubric review. Suggest scores using the original student response, the complete evidence analysis, and the exact provided 0–4 descriptors. Verify all claims against the ORIGINAL RESPONSE; the evidence analysis may be mistaken. Review the WHOLE paragraph for each criterion, not just the first excerpt. For any score below 4, cite the SPECIFIC unmet part of the higher descriptor and concrete textual evidence, or state that the distinction is uncertain and requires teacher judgment. Never lower a score solely because the writing could be more sophisticated. Do not require extra narrative elements when the rubric says 'and/or'. For Organization, explicitly consider the full sequence and existing transitions. For Development, account for all descriptions, comparisons, sensory details, actions and feelings. For Conventions, deductions MUST be supported by identifiable grammar, usage, spelling, capitalization, or punctuation errors in the original response; if none are identifiable, do not invent errors or penalize simple sentence structure or vocabulary. Keep all five criteria separate. No score is final. Return ONLY JSON: {"criteria":[{"name":"Focus","score":0,"evidence":"short exact excerpts or an explicit absence of evidence","rationale":"rubric-specific explanation"}, ...],"review_note":"uncertainties requiring teacher review"}. Include every criterion exactly once and integer scores 0 through 4."""

def call_llm(system, data):
 key=os.getenv('OPENAI_API_KEY')
 if not key: raise ValueError('OPENAI_API_KEY is not configured on the server.')
 payload=json.dumps({'model':os.getenv('OPENAI_MODEL','gpt-4o-mini'),'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(data)}]}).encode()
 req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=payload,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as resp: raw=json.load(resp)
 return json.loads(raw['choices'][0]['message']['content'])

def validate(result):
 if not isinstance(result,dict) or not isinstance(result.get('criteria'),list):raise ValueError('Model response missing criteria.')
 items=result['criteria']; expected=set(RUBRIC)
 if len(items)!=len(expected) or {x.get('name') for x in items}!=expected:raise ValueError('Model returned unexpected rubric criteria.')
 for x in items:
  if type(x.get('score')) is not int or x['score'] not in (0,1,2,3,4):raise ValueError('Model returned an invalid score.')
  if not isinstance(x.get('evidence'),str) or not isinstance(x.get('rationale'),str):raise ValueError('Model response missing evidence/rationale.')
 result['total']=sum(x['score'] for x in items);result['maximum']=len(RUBRIC)*4
 result['review_required']=True
 return result
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def do_GET(self):
  path=self.path.split("?",1)[0]
  if path not in ("/", "/index.html", "/teacher.html", "/student.html"):
   self.send_error(404)
   return
  self.path="/index.html" if path=="/" else path
  return super().do_GET()
 def do_POST(self):
  if self.path=='/api/speech':
   return self.handle_speech()
  if self.path!='/api/review':self.send_error(404);return
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n>30000:raise ValueError('Input too long.')
   data=json.loads(self.rfile.read(n))
   response=data.get('response','')
   if not isinstance(response,str) or not response.strip():raise ValueError('Please enter a student response before requesting a review.')
   if len(response)>12000:raise ValueError('Student response is too long for this prototype.')
   if data.get('mode') not in ('v1','v2','v2_refined'):raise ValueError('Invalid workflow selection.')
   context={'grade':5,'task':'Write a paragraph describing a journey to a new, unknown place. Compare what you see to things you already know. Use characteristics of a personal narrative.','rubric':RUBRIC,'student_response':response}
   if data['mode']=='v2_refined':
    analysis=call_llm(ANALYZE_REFINED,context)
    result=validate(call_llm(SCORE_REFINED,{**context,'intermediate_evidence_analysis':analysis}))
    result['intermediate_analysis']=analysis
   elif data['mode']=='v2':
    analysis=call_llm(ANALYZE,context)
    result=validate(call_llm(SCORE2,{**context,'intermediate_evidence_analysis':analysis}))
    result['intermediate_analysis']=analysis
   else:result=validate(call_llm(PROMPT,context))
   self.send_json(200,result)
  except urllib.error.HTTPError as e:
   self.send_json(502,{'error':'API error '+str(e.code)+': '+e.read().decode()[:350]})
  except Exception as e:self.send_json(400,{'error':str(e)})
 def handle_speech(self):
  # Prototype-only endpoint. Public deployments need authentication and stronger rate limits.
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n<1 or n>12000:raise ValueError('Invalid speech request size.')
   data=json.loads(self.rfile.read(n))
   if not isinstance(data,dict) or data.get('section') not in ('directions','passage','prompt','response'):
    raise ValueError('Invalid speech section.')
   original='Traveling to an unknown place can be both exciting and scary. One way to describe your journey is to compare and contrast what you see to things you already know. Write a paragraph describing a journey you take to a new, unknown place. Remember the characteristics of a personal narrative as you write.'
   if 'text' in data:
    spoken=data['text']
    if not isinstance(spoken,str) or not spoken.strip() or len(spoken)>3000:
     raise ValueError('Natural voice text must be 1–3000 characters.')
   elif data['section']=='directions':
    spoken=original
   else:
    raise ValueError('No passage supplied.')
   key=os.getenv('OPENAI_API_KEY')
   if not key:raise ValueError('Speech service is not configured.')
   payload=json.dumps({'model':'gpt-4o-mini-tts','voice':'coral','input':spoken,'response_format':'mp3','instructions':'Read this assessment text clearly, warmly, and at a calm, accessible pace. Do not add or change any words.'}).encode()
   req=urllib.request.Request('https://api.openai.com/v1/audio/speech',data=payload,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=60) as resp:audio=resp.read(3000001)
   if not audio or len(audio)>3000000:raise ValueError('Invalid speech response.')
   self.send_response(200)
   self.send_header('Content-Type','audio/mpeg')
   self.send_header('Cache-Control','no-store')
   self.send_header('Content-Length',str(len(audio)))
   self.end_headers()
   self.wfile.write(audio)
  except urllib.error.HTTPError as e:self.send_json(502,{'error':'Speech service returned an error ('+str(e.code)+').'})
  except Exception as e:self.send_json(400,{'error':str(e)})
 def send_json(self,status,data):
  raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
if __name__=='__main__':
 port=int(os.getenv('PORT','8000'))
 print(f'Server listening on port {port}. Keep API keys in server environment variables only.')
 ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
