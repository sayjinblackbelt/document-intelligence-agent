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

function fillList(id,values){
  const element=document.getElementById(id);
  element.innerHTML='';
  const items=Array.isArray(values)?values:[];
  if(!items.length){element.innerHTML='<li>Nenhum indício identificado.</li>';return}
  items.forEach(value=>{const item=document.createElement('li');item.textContent=value;element.appendChild(item)});
}

async function loadHistory(){
  historyStatus.textContent='Carregando histórico...';
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
      historyStatus.textContent='Nenhuma análise assistida foi persistida ainda.';
      return;
    }
    historyStatus.textContent=records.length+' análise(s) encontrada(s).';
    records.forEach(record=>{
      const button=document.createElement('button');
      button.type='button';
      button.className='history-item';
      button.innerHTML='<strong>#'+record.id+' • '+escapeHtml(record.filename)+'</strong><span>'+escapeHtml(record.provider)+' • '+formatDate(record.created_at)+'</span>';
      button.addEventListener('click',()=>openHistory(record.id));
      historyList.appendChild(button);
    });
  }catch(error){historyStatus.textContent='Erro: '+error.message}
}

async function openHistory(id){
  try{
    const response=await fetch('/history/'+id);
    const record=await response.json();
    if(!response.ok)throw new Error(record.detail||'Falha ao abrir análise');
    const analysis=record.analise_assistida||{};
    historyTitle.textContent='Análise #'+record.id+' • '+record.filename;
    document.getElementById('history-summary').textContent=analysis.resumo_executivo||'Sem resumo disponível.';
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
  status.textContent='Analisando documento...';
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
    status.textContent='Análise concluída: '+result.arquivo;
  }catch(error){status.textContent='Erro: '+error.message}
});

aiForm.addEventListener('submit',async event=>{
  event.preventDefault();
  const file=document.getElementById('file').files[0];
  if(!file){aiStatus.textContent='Selecione um arquivo antes de executar a análise assistida.';return}
  aiStatus.textContent='Enviando documento e consultando provider...';
  aiResults.hidden=true;
  try{
    const provider=document.getElementById('ai-provider').value;
    const data=new FormData();
    data.append('file',file);
    const response=await fetch('/analyze/ai/file?provider='+encodeURIComponent(provider),{
      method:'POST',
      body:data
    });
    const record=await response.json();
    if(!response.ok)throw new Error(record.detail||'Falha na análise assistida');
    const analysis=record.analise_assistida||{};
    document.getElementById('ai-title').textContent='Análise #'+record.id+' • '+record.filename;
    document.getElementById('ai-summary').textContent=analysis.resumo_executivo||'Sem resumo disponível.';
    document.getElementById('ai-provider-result').textContent=analysis.provider||record.provider||'—';
    document.getElementById('ai-priority').textContent=analysis.prioridade_sugerida||'—';
    document.getElementById('ai-model').textContent=analysis.model||'local';
    fillList('ai-requirements',analysis.requisitos);
    fillList('ai-pending',analysis.pendencias);
    fillList('ai-risks',analysis.riscos);
    aiResults.hidden=false;
    aiStatus.textContent='Análise assistida concluída e salva no histórico.';
    await loadHistory();
    aiResults.scrollIntoView({behavior:'smooth',block:'start'});
  }catch(error){aiStatus.textContent='Erro: '+error.message}
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