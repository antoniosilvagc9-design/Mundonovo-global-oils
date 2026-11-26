/*
 * Mundo Novo Trade · Curva Mensal · Exportação de imagem A4.
 * Usa somente preços já calculados na própria página; não acessa configurações financeiras.
 * Logo oficial reaproveitada do exportador de Cotação Definitiva.
 */
const LOGO_SRC = 'data:image/png;base64,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';
const W=2480, H=3508;
const ACCENT='#6B033B', HEADER='#95A2AA', TURQUOISE='#48B7BE', INK='#172027', LIGHT='#F5F7F8';
export const reportProducts=[
  'ÓLEO DE PALMA (RBDPO)',
  'ESTEARINA DE PALMA (RBDPS)',
  'ÓLEO DE PALMISTE (RBDPKO)',
  'ESTEARINA DE PALMISTE (RBDPKS)'
];
const MONTHS=['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'];
const moneyText=s=>/^\d[\d.,]*$/.test(String(s||'').trim())?'R$ '+String(s).trim():'';
const brDate=new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',hour12:false});
function layoutTable(ctx, data, monthKeys, first, startY, fullWidth){
  const x=145,w=fullWidth,headH=79,rowH=88,prodW=570,colW=(w-prodW)/6;
  ctx.fillStyle=ACCENT;ctx.font='bold 36px Arial';
  ctx.fillText(MONTHS[Number(monthKeys[first].slice(5,7))-1]+' '+monthKeys[first].slice(0,4)+' A '+MONTHS[Number(monthKeys[first+5].slice(5,7))-1]+' '+monthKeys[first+5].slice(0,4),x,startY-32);
  const top=startY;
  ctx.fillStyle=HEADER;ctx.fillRect(x,top,w,headH);
  ctx.strokeStyle='#39424a';ctx.lineWidth=2;
  const cellText=(str,xx,yy,ww,size=32,bold=false,center=false)=>{
    ctx.save();ctx.beginPath();ctx.rect(xx+8,yy+5,ww-16,rowH-10);ctx.clip();
    ctx.font=(bold?'bold ':'')+size+'px Arial';ctx.fillStyle=INK;
    ctx.textBaseline='middle';ctx.textAlign=center?'center':'left';
    ctx.fillText(str,center?xx+ww/2:xx+14,yy+rowH/2);
    ctx.restore();
  };
  ctx.font='bold 32px Arial';ctx.fillStyle=INK;ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillText('PRODUTO',x+prodW/2,top+headH/2);
  for(let j=0;j<6;j++){
    const idx=first+j;
    const month=MONTHS[Number(monthKeys[idx].slice(5,7))-1]+'/'+monthKeys[idx].slice(2,4);
    ctx.fillText(month,x+prodW+colW*(j+.5),top+headH/2);
  }
  let y=top+headH;
  for(let i=0;i<4;i++){
    ctx.fillStyle=i%2===0?'#FFFFFF':LIGHT;ctx.fillRect(x,y,w,rowH);
    cellText(data[i].name,x,y,prodW,29,true);
    for(let j=0;j<6;j++)cellText(moneyText(data[i].sales[first+j]),x+prodW+colW*j,y,colW,27,false,true);
    y+=rowH;
    ctx.fillStyle=TURQUOISE;ctx.fillRect(x,y,w,rowH);
    cellText('PREÇO NET',x,y,prodW,29,true);
    for(let j=0;j<6;j++)cellText(moneyText(data[i].net[first+j]),x+prodW+colW*j,y,colW,27,false,true);
    y+=rowH;
  }
  ctx.beginPath();
  const bottom=top+headH+8*rowH;
  for(let k=0;k<=6;k++){
    const xpos=k===0?x:k===1?x+prodW:x+prodW+(k-1)*colW;
    ctx.moveTo(xpos,top);ctx.lineTo(xpos,bottom);
  }
  ctx.moveTo(x+w,top);ctx.lineTo(x+w,bottom);
  for(let j=0;j<=8;j++){
    const ypos=top+headH+j*rowH;
    ctx.moveTo(x,ypos);ctx.lineTo(x+w,ypos);
  }
  ctx.moveTo(x,top);ctx.lineTo(x+w,top);
  ctx.stroke();
  return bottom;
}
function imgFromData(src){return new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=()=>reject(Error('Não foi possível carregar a logo oficial'));i.src=src;});}
export async function exportMonthlyA4({payment,year,months:monthKeys,products,scenario=''}){
  if(!Number.isInteger(year)||year<2020||year>2100)throw Error('Ano de referência inválido');
  if(!Array.isArray(monthKeys)||monthKeys.length!==12||monthKeys.some(v=>typeof v!=='string'||v.length!==7||v[4]!=='-'||Number(v.slice(5,7))<1||Number(v.slice(5,7))>12))throw Error('Período mensal inválido');
  if(!payment||!payment.trim())throw Error('Informe a condição de pagamento antes de exportar');
  if(!Array.isArray(products)||products.length!==4||products.some(p=>p.sales?.length!==12||p.net?.length!==12))throw Error('Dados da Curva Mensal incompletos');
  if(!products.some(p=>p.sales.some(moneyText)))throw Error('Preencha e calcule ao menos um preço comercial antes da exportação.');
  const canvas=document.createElement('canvas');
  canvas.width=W;canvas.height=H;
  const ctx=canvas.getContext('2d',{alpha:false});
  if(!ctx)throw Error('Seu navegador não suporta exportação de imagem Canvas.');
  ctx.fillStyle='#FFFFFF';ctx.fillRect(0,0,W,H);
  const logo=await imgFromData(LOGO_SRC);
  const maxLogoW=950,maxLogoH=510;
  const factor=Math.min(maxLogoW/logo.naturalWidth,maxLogoH/logo.naturalHeight);
  const lw=logo.naturalWidth*factor,lh=logo.naturalHeight*factor;
  ctx.drawImage(logo,(W-lw)/2,118,lw,lh);
  ctx.textAlign='center';ctx.fillStyle=ACCENT;ctx.font='bold 45px Arial';ctx.textBaseline='middle';
  ctx.fillText('MUNDO NOVO TRADE · PROPOSTA COMERCIAL',W/2,710);
  ctx.fillStyle=INK;ctx.font='bold 53px Arial';
  ctx.fillText('CONDIÇÕES DE PAGAMENTO — '+payment.toUpperCase(),W/2,803,2160);
  ctx.fillStyle='#6c7680';ctx.font='29px Arial';
  ctx.fillText('CURVA MENSAL DE PREÇOS · '+monthKeys[0]+' A '+monthKeys[11],W/2,875);
  ctx.strokeStyle=ACCENT;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(145,934);ctx.lineTo(W-145,934);ctx.stroke();
  const tableW=W-290;
  layoutTable(ctx,products,monthKeys,0,1030,tableW);
  layoutTable(ctx,products,monthKeys,6,2040,tableW);
  ctx.strokeStyle=ACCENT;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(145,3050);ctx.lineTo(W-145,3050);ctx.stroke();
  ctx.fillStyle=INK;ctx.font='29px Arial';ctx.textAlign='center';
  const when=brDate.format(new Date())+' (Brasília)';
  ctx.fillText('COTAÇÃO EMITIDA EM '+when+' · FOB PARANAGUÁ · SUJEITA A ALTERAÇÕES',W/2,3137,2180);
  if(scenario){ctx.fillStyle='#56606b';ctx.font='27px Arial';ctx.fillText('Cenário: '+scenario,W/2,3205,2180);}
  ctx.fillStyle='#7b858d';ctx.font='26px Arial';
  ctx.fillText('Valores em R$/kg, apresentados com a precisão calculada na Curva Mensal.',W/2,3305,2180);
  const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
  if(!blob)throw Error('Não foi possível gerar o arquivo PNG');
  const url=URL.createObjectURL(blob);
  const link=document.createElement('a');link.href=url;
  const date=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  link.download='MundoNovo_CurvaMensal_'+date+'.png';
  document.body.append(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),30000);
  return {width:W,height:H,bytes:blob.size};
}