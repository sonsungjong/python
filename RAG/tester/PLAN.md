# LangGraph 기반 RAG 시스템 구현 계획서

## 📋 프로젝트 개요
**목표**: SPRI_AI_Brief_2023년12월호_F.pdf를 기반으로 LangGraph와 ChatOpenAI를 활용한 Agentic RAG 시스템 구축

**핵심 기능**:
- PDF 문서 임베딩 및 벡터 검색
- 검색 결과 품질 평가 (Document Grading)
- 검색 실패 시 자동 쿼리 재작성 (Query Rewriting)
- 최종 답변 생성

---

## 🏗️ 시스템 아키텍처

### 1. 상태(State) 정의
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```
- 대화 히스토리와 문서 검색 결과를 messages로 관리
- `add_messages`로 메시지 자동 누적

### 2. 노드(Node) 구성

#### 2.1 **retrieve** 노드
- **역할**: PDF 문서에서 관련 내용 검색 (무조건 실행)
- **구현**: FAISS retriever.invoke()
- **검색 대상**: FAISS 벡터 스토어
- **출력**: 검색된 문서 chunks

#### 2.2 **grade_documents** 노드 (조건부 엣지)
- **역할**: 검색된 문서의 관련성 평가
- **평가 기준**: 
  - "yes": 문서가 질문과 관련있음 → `generate`로 이동
  - "no": 문서가 질문과 무관함 → `rewrite`로 이동
- **구현**: Structured Output (Pydantic)
- **사용 모델**: ChatOpenAI (gpt-5-nano)

#### 2.3 **rewrite** 노드
- **역할**: 검색 실패 시 질문 재구성
- **전략**: 
  - 원래 질문의 의도 분석
  - 더 구체적이고 검색 가능한 형태로 변환
- **출력**: 개선된 질문 → 다시 `retrieve`로
- **사용 모델**: ChatOpenAI (gpt-5-nano)

#### 2.4 **generate** 노드
- **역할**: 검색된 문서 기반 최종 답변 생성
- **입력**: 원래 질문 + 검색된 문서
- **출력**: 최종 답변
- **사용 모델**: ChatOpenAI (gpt-5-nano)

---

## 🔄 워크플로우 그래프

```
START 
  ↓
retrieve (무조건 문서 검색)
  ↓
grade_documents (문서 품질 평가)
  ↓ (yes)         ↓ (no)
generate        rewrite
  ↓               ↓
END            retrieve (재시도)
```

---

## 🛠️ 기술 스택

### 핵심 라이브러리
- **LangGraph**: 워크플로우 관리
- **LangChain**: RAG 체인 구성
- **OpenAI**: ChatOpenAI (gpt-4o-mini)
- **FAISS**: 벡터 검색
- **PyMuPDF**: PDF 파싱

### 주요 컴포넌트
1. **Document Loader**: PyMuPDFLoader
2. **Text Splitter**: RecursiveCharacterTextSplitter
3. **Embeddings**: OpenAIEmbeddings
4. **Vector Store**: FAISS
5. **LLM**: ChatOpenAI

---

## 📝 구현 단계

### Phase 1: 문서 준비 및 임베딩
1. PDF 로드 (`PyMuPDFLoader`)
2. 텍스트 청킹 (chunk_size=1000, overlap=200)
3. OpenAI Embeddings 생성
4. FAISS 벡터 스토어 구축

### Phase 2: 검색기 구성
1. FAISS retriever 설정 (k=4)
2. retriever를 직접 노드에서 사용

### Phase 3: LangGraph 노드 구현
1. **retrieve 노드**: FAISS retriever로 직접 검색
2. **grade_documents**: Structured Output 기반 평가
3. **rewrite 노드**: 질문 개선 프롬프트
4. **generate 노드**: RAG 체인 실행

### Phase 4: 그래프 연결 및 컴파일
1. StateGraph 생성
2. 노드 추가 (`add_node`)
3. 엣지 연결 (`add_edge`, `add_conditional_edges`)
4. 그래프 컴파일

### Phase 5: 테스트 및 검증
1. 정상 케이스: PDF 내용 관련 질문
2. 실패 케이스: PDF와 무관한 질문 → 재질문 확인
3. 재귀 제한(recursion_limit) 설정

---

## ⚙️ 주요 설정값

```python
# LLM 설정
MODEL_NAME = 'gpt-5-nano'
TEMPERATURE = 0

# 텍스트 분할
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 검색 설정
TOP_K = 4

# 재귀 제한
RECURSION_LIMIT = 10
```

---

## 🎯 핵심 차별점

1. **무조건 RAG 기반 답변**: 모든 질문에 대해 PDF 문서 기반으로만 답변
2. **자동 쿼리 개선**: 검색 실패 시 자동으로 질문을 재구성하여 재시도
3. **문서 품질 평가**: Structured Output으로 명확한 yes/no 판단
4. **순환 구조**: rewrite → retrieve → grade 반복으로 최적 답변 도출
5. **무한 루프 방지**: recursion_limit으로 최대 반복 횟수 제한

---

## 📊 예상 시나리오

### 시나리오 1: 성공적인 검색
### 시나리오 1: 성공적인 검색
```
User: "삼성전자가 개발한 생성형 AI의 이름은?"
 ↓
retrieve (문서 검색)
 ↓
grade_documents: "yes" (관련 문서 발견)
 ↓
generate → "삼성 가우스(Samsung Gauss)입니다."
```

### 시나리오 2: 검색 실패 후 재시도
```
User: "AI 트렌드에 대해 알려줘"
 ↓
retrieve (너무 광범위한 질문)
 ↓
grade_documents: "no" (문서 관련성 낮음)
 ↓
rewrite: "SPRI AI Brief 2023년 12월호에 언급된 주요 AI 트렌드는?"
 ↓
retrieve → grade: "yes" → generate (성공)
```

### 시나리오 3: 문서에 없는 내용
```
User: "내일 날씨는?"
 ↓
retrieve → grade: "no"
 ↓
rewrite → retrieve → grade: "no"
 ↓
... (recursion_limit까지 반복)
 ↓
GraphRecursionError: "문서에서 관련 정보를 찾을 수 없습니다."
```
---

## 🔍 참고 코드
- `/home/user/source/python312/python/RAG/17-LangGraph/02-Structures/06-Agentic_Rag.ipynb`
- `/home/user/source/python312/python/LangGraph/5. LangGraph/_LangGraph.ipynb`

---

## ✅ 체크리스트

- [ ] PDF 로드 및 임베딩 완료
- [ ] FAISS 벡터 스토어 생성
- [ ] FAISS retriever 구성
- [ ] retrieve 노드 구현 (무조건 검색)
- [ ] grade_documents 조건부 엣지 구현
- [ ] rewrite 노드 구현
- [ ] generate 노드 구현
- [ ] StateGraph 연결 및 컴파일
- [ ] 정상 케이스 테스트
- [ ] 재질문 케이스 테스트
- [ ] 에러 핸들링 (recursion_limit) 테스트

---

**작성일**: 2025년 12월 8일
**PDF 문서**: `SPRI_AI_Brief_2023년12월호_F.pdf`
