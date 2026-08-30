const translations={
pt:{demo:'CASE DEMONSTRATIVO',language:'Idioma',subtitle:'Análise documental com regras, API, IA assistida e histórico persistente.',analyzeDocument:'Analisar documento',analyzeFile:'Analisar arquivo',assistedAnalysis:'Análise assistida por IA',providerLocal:'Local (determinístico)',runAssisted:'Executar análise assistida',assistedResult:'ANÁLISE ASSISTIDA',aiResult:'Resultado da IA',provider:'Provider',priority:'Prioridade',model:'Modelo',requirements:'Requisitos',pending:'Pendências',risks:'Riscos',type:'Tipo',score:'Score',characters:'Caracteres',fullData:'Dados completos',persistence:'PERSISTÊNCIA',history:'Histórico de análises',refresh:'Atualizar',searchPlaceholder:'Buscar por nome do documento',allProviders:'Todos os providers',local:'Local',allPriorities:'Todas as prioridades',high:'Alta',medium:'Média',low:'Baixa',clear:'Limpar',savedAnalysis:'ANÁLISE SALVA',analysisDetails:'Detalhes da análise',date:'Data',exportMarkdown:'Exportar Markdown',exportPdf:'Exportar PDF',technicalData:'Ver dados técnicos completos',footer:'Dados demonstrativos • revisão humana recomendada',loading:'Carregando histórico...',emptyHistory:'Nenhuma análise assistida foi persistida ainda.',analysesFound:'análise(s) encontrada(s).',analyzing:'Analisando documento...',sending:'Enviando documento e consultando provider...',selectFile:'Selecione um arquivo antes de executar a análise assistida.',assistedDone:'Análise assistida concluída e salva no histórico.',analysisDone:'Análise concluída:',noIndicators:'Nenhum indício identificado.',noSummary:'Sem resumo disponível.',error:'Erro:'},
en:{demo:'DEMONSTRATION CASE',language:'Language',subtitle:'Document analysis with rules, API, assisted AI, and persistent history.',analyzeDocument:'Analyze document',analyzeFile:'Analyze file',assistedAnalysis:'AI-assisted analysis',providerLocal:'Local (deterministic)',runAssisted:'Run assisted analysis',assistedResult:'ASSISTED ANALYSIS',aiResult:'AI result',provider:'Provider',priority:'Priority',model:'Model',requirements:'Requirements',pending:'Pending items',risks:'Risks',type:'Type',score:'Score',characters:'Characters',fullData:'Full data',persistence:'PERSISTENCE',history:'Analysis history',refresh:'Refresh',searchPlaceholder:'Search by document name',allProviders:'All providers',local:'Local',allPriorities:'All priorities',high:'High',medium:'Medium',low:'Low',clear:'Clear',savedAnalysis:'SAVED ANALYSIS',analysisDetails:'Analysis details',date:'Date',exportMarkdown:'Export Markdown',exportPdf:'Export PDF',technicalData:'View complete technical data',footer:'Demonstration data • human review recommended',loading:'Loading history...',emptyHistory:'No assisted analysis has been persisted yet.',analysesFound:'analysis(es) found.',analyzing:'Analyzing document...',sending:'Sending document and querying provider...',selectFile:'Select a file before running assisted analysis.',assistedDone:'Assisted analysis completed and saved to history.',analysisDone:'Analysis completed:',noIndicators:'No indicators identified.',noSummary:'No summary available.',error:'Error:'},
es:{demo:'CASO DEMOSTRATIVO',language:'Idioma',subtitle:'Análisis documental con reglas, API, IA asistida e historial persistente.',analyzeDocument:'Analizar documento',analyzeFile:'Analizar archivo',assistedAnalysis:'Análisis asistido por IA',providerLocal:'Local (determinístico)',runAssisted:'Ejecutar análisis asistido',assistedResult:'ANÁLISIS ASISTIDO',aiResult:'Resultado de IA',provider:'Proveedor',priority:'Prioridad',model:'Modelo',requirements:'Requisitos',pending:'Pendientes',risks:'Riesgos',type:'Tipo',score:'Puntuación',characters:'Caracteres',fullData:'Datos completos',persistence:'PERSISTENCIA',history:'Historial de análisis',refresh:'Actualizar',searchPlaceholder:'Buscar por nombre del documento',allProviders:'Todos los proveedores',local:'Local',allPriorities:'Todas las prioridades',high:'Alta',medium:'Media',low:'Baja',clear:'Limpiar',savedAnalysis:'ANÁLISIS GUARDADO',analysisDetails:'Detalles del análisis',date:'Fecha',exportMarkdown:'Exportar Markdown',exportPdf:'Exportar PDF',technicalData:'Ver datos técnicos completos',footer:'Datos demostrativos • se recomienda revisión humana',loading:'Cargando historial...',emptyHistory:'Aún no se ha guardado ningún análisis asistido.',analysesFound:'análisis encontrado(s).',analyzing:'Analizando documento...',sending:'Enviando documento y consultando al proveedor...',selectFile:'Seleccione un archivo antes de ejecutar el análisis asistido.',assistedDone:'Análisis asistido completado y guardado en el historial.',analysisDone:'Análisis completado:',noIndicators:'No se identificaron indicios.',noSummary:'No hay resumen disponible.',error:'Error:'}
};
let language=localStorage.getItem('dia-language')||'pt';
function t(key){return translations[language][key]||translations.pt[key]||key}
function applyLanguage(){
 document.documentElement.lang=language==='pt'?'pt-BR':language;
 document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n)});
 document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{el.placeholder=t(el.dataset.i18nPlaceholder)});
 document.getElementById('language-select').value=language;
}
const form=document.getElementById('upload-form');
const status=document.getElementById('status');
const results=document.getElementById('results');
const aiForm=document.getElementById('ai-form');
const aiStatus=document.getElementById('ai-status');
const aiResults=document.getElementById('ai-results');
const historyStatus=document.getElementById('history-status');
const historyList=document.getElementById('history-list');
const historyDetail=document.getElementById('history-detail');
const historyTitle=document.getElementById('history-title');
const historyJson=document.getElementById('history-json');
let currentHistoryId=null;

function fillList(id,values){
  const element=document.getElementById(id);
  element.innerHTML='';
  const items=Array.isArray(values)?values:[];
  if(!items.length){element.innerHTML='<li>'+t('noIndicators')+'</li>';return}
  items.forEach(value=>{const item=document.createElement('li');item.textContent=value;element.appendChild(item)});
}

async function loadHistory(){
  historyStatus.textContent=t('loading');
  historyList.innerHTML='';
  try{
    const params=new URLSearchParams({limit:'20'});
    const filename=document.getElementById('history-search').value.trim();
    const provider=document.getElementById('history-provider-filter').value;
    const priority=document.getElementById('history-priority-filter').value;
    if(filename)params.set('filename',filename);
    if(provider)params.set('provider',provider);
    if(priority)params.set('priority',priority);
    const response=await fetch('/history?'+params.toString());
    const records=await response.json();
    if(!response.ok)throw new Error(records.detail||'Falha ao carregar histórico');
    if(!records.length){
      historyStatus.textContent=t('emptyHistory');
      return;
    }
    historyStatus.textContent=records.length+' '+t('analysesFound');
    records.forEach(record=>{
      const button=document.createElement('button');
      button.type='button';
      button.className='history-item';
      button.innerHTML='<strong>#'+record.id+' • '+escapeHtml(record.filename)+'</strong><span>'+escapeHtml(record.provider)+' • '+formatDate(record.created_at)+'</span>';
      button.addEventListener('click',()=>openHistory(record.id));
      historyList.appendChild(button);
    });
  }catch(error){historyStatus.textContent=t('error')+' '+error.message}
}

async function openHistory(id){
  try{
    const response=await fetch('/history/'+id);
    const record=await response.json();
    if(!response.ok)throw new Error(record.detail||'Falha ao abrir análise');
    currentHistoryId=record.id;
    const analysis=record.analise_assistida||{};
    historyTitle.textContent='Análise #'+record.id+' • '+record.filename;
    document.getElementById('history-summary').textContent=analysis.resumo_executivo||t('noSummary');
    document.getElementById('history-provider').textContent=analysis.provider||record.provider||'—';
    document.getElementById('history-priority').textContent=analysis.prioridade_sugerida||'—';
    document.getElementById('history-date').textContent=formatDate(record.created_at);
    fillList('history-requirements',analysis.requisitos);
    fillList('history-pending',analysis.pendencias);
    fillList('history-risks',analysis.riscos);
    historyJson.textContent=JSON.stringify(record,null,2);
    historyDetail.hidden=false;
    historyDetail.scrollIntoView({behavior:'smooth',block:'nearest'});
  }catch(error){historyStatus.textContent='Erro: '+error.message}
}

function formatDate(value){
  const date=new Date(value);
  return Number.isNaN(date.getTime())?value:date.toLocaleString('pt-BR');
}

function escapeHtml(value){
  const div=document.createElement('div');
  div.textContent=value??'';
  return div.innerHTML;
}

form.addEventListener('submit',async event=>{
  event.preventDefault();
  const file=document.getElementById('file').files[0];
  if(!file)return;
  status.textContent=t('analyzing');
  results.hidden=true;
  const data=new FormData();
  data.append('file',file);
  try{
    const response=await fetch('/analyze/file',{method:'POST',body:data});
    const result=await response.json();
    if(!response.ok)throw new Error(result.detail||'Falha na análise');
    document.getElementById('type').textContent=result.tipo_documento||'—';
    document.getElementById('score').textContent=String(result.score_completude??0)+'%';
    document.getElementById('characters').textContent=result.caracteres??'—';
    const keywords=result.palavras_chave||{};
    fillList('requirements',keywords.requisitos);
    fillList('pending',keywords.pendencias);
    fillList('risks',keywords.riscos);
    document.getElementById('json').textContent=JSON.stringify(result,null,2);
    results.hidden=false;
    status.textContent=t('analysisDone')+' '+result.arquivo;
  }catch(error){status.textContent=t('error')+' '+error.message}
});

aiForm.addEventListener('submit',async event=>{
  event.preventDefault();
  const file=document.getElementById('file').files[0];
  if(!file){aiStatus.textContent=t('selectFile');return}
  aiStatus.textContent=t('sending');
  aiResults.hidden=true;
  try{
    const provider=document.getElementById('ai-provider').value;
    const data=new FormData();
    data.append('file',file);
    const response=await fetch('/analyze/ai/file?provider='+encodeURIComponent(provider)+'&language='+encodeURIComponent(language),{
      method:'POST',
      body:data
    });
    const record=await response.json();
    if(!response.ok)throw new Error(record.detail||'Falha na análise assistida');
    const analysis=record.analise_assistida||{};
    document.getElementById('ai-title').textContent='Análise #'+record.id+' • '+record.filename;
    document.getElementById('ai-summary').textContent=analysis.resumo_executivo||t('noSummary');
    document.getElementById('ai-provider-result').textContent=analysis.provider||record.provider||'—';
    document.getElementById('ai-priority').textContent=analysis.prioridade_sugerida||'—';
    document.getElementById('ai-model').textContent=analysis.model||'local';
    fillList('ai-requirements',analysis.requisitos);
    fillList('ai-pending',analysis.pendencias);
    fillList('ai-risks',analysis.riscos);
    aiResults.hidden=false;
    aiStatus.textContent=t('assistedDone');
    await loadHistory();
    aiResults.scrollIntoView({behavior:'smooth',block:'start'});
  }catch(error){aiStatus.textContent=t('error')+' '+error.message}
});

document.getElementById('history-export').addEventListener('click',event=>{
  const format=event.target.dataset.export;
  if(format&&currentHistoryId){
    window.open('/history/'+currentHistoryId+'/export?format='+format,'_blank');
  }
});

document.getElementById('refresh-history').addEventListener('click',loadHistory);
document.getElementById('history-provider-filter').addEventListener('change',loadHistory);
document.getElementById('history-priority-filter').addEventListener('change',loadHistory);
document.getElementById('history-search').addEventListener('search',loadHistory);
document.getElementById('history-search').addEventListener('input',event=>{
  clearTimeout(window.historySearchTimer);
  window.historySearchTimer=setTimeout(loadHistory,300);
});
document.getElementById('clear-history-filters').addEventListener('click',()=>{
  document.getElementById('history-search').value='';
  document.getElementById('history-provider-filter').value='';
  document.getElementById('history-priority-filter').value='';
  loadHistory();
});
loadHistory();

document.getElementById('language-select').addEventListener('change',event=>{
 language=event.target.value;
 localStorage.setItem('dia-language',language);
 applyLanguage();
 loadHistory();
});
applyLanguage();
