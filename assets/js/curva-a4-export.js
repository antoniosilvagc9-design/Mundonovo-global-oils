/*
 * Mundo Novo Trade · Proposta comercial mensal · PNG A4 paisagem (3508 × 2480).
 * Fonte única dos valores: células Venda R$/kg e NET R$/kg já calculadas na Curva Mensal.
 * Geração local no navegador: sem recálculo financeiro e sem envio a serviços externos.
 */
const LOGO_SRC = 'data:image/png;base64,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';
const W=3508, H=2480;
const WINE='#6B033B', SLATE='#95A2AA', INK='#262A30', WHITE='#FFFFFF', PALE='#F4F6F7';
export const reportProducts=[
  'ÓLEO DE PALMA (RBDPO)',
  'ESTEARINA DE PALMA (RBDPS)',
  'ÓLEO DE PALMISTE (RBDPKO)',
  'ESTEARINA DE PALMISTE (RBDPKS)'
];
const MONTHS=['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'];
const moneyText=value=>/^\d[\d.,]*$/.test(String(value??'').trim())?'R$ '+String(value).trim():'';
const brDate=new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',hour12:false});
const dateForFile=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'});

function paintText(ctx,text,x,y,width,size,{bold=false,color=INK,align='left'}={}){
  ctx.save();
  ctx.fillStyle=color;
  ctx.font=(bold?'700 ':'400 ')+size+'px Arial, Helvetica, sans-serif';
  ctx.textAlign=align;
  ctx.textBaseline='middle';
  ctx.fillText(String(text),x,y,width);
  ctx.restore();
}
function fill(ctx,x,y,w,h,color){
  ctx.fillStyle=color;ctx.fillRect(x,y,w,h);
}
function drawTable(ctx,products,monthKeys){
  const x=100,top=795,width=W-200,labelW=640,monthW=(width-labelW)/12;
  const headH=112,rowH=154;
  fill(ctx,x,top,width,headH,SLATE);
  paintText(ctx,'PRODUTO',x+labelW/2,top+headH/2,labelW-30,36,{bold:true,color:WHITE,align:'center'});
  for(let j=0;j<12;j++){
    const key=monthKeys[j];
    const month=MONTHS[Number(key.slice(5,7))-1]+'/'+key.slice(2,4);
    paintText(ctx,month,x+labelW+monthW*(j+.5),top+headH/2,monthW-10,33,{bold:true,color:WHITE,align:'center'});
  }
  for(let i=0;i<4;i++){
    const saleY=top+headH+(i*2)*rowH,netY=saleY+rowH;
    fill(ctx,x,saleY,width,rowH,i%2===0?WHITE:PALE);
    fill(ctx,x,netY,width,rowH,WINE);
    paintText(ctx,products[i].name,x+22,saleY+rowH/2,labelW-36,35,{bold:true});
    paintText(ctx,'PREÇO NET',x+22,netY+rowH/2,labelW-36,35,{bold:true,color:WHITE});
    for(let j=0;j<12;j++){
      const cx=x+labelW+monthW*(j+.5);
      paintText(ctx,moneyText(products[i].sales[j]),cx,saleY+rowH/2,monthW-16,32,{color:INK,align:'center'});
      paintText(ctx,moneyText(products[i].net[j]),cx,netY+rowH/2,monthW-16,32,{color:WHITE,align:'center'});
    }
  }
  const bottom=top+headH+8*rowH;
  ctx.save();ctx.strokeStyle='#55616A';ctx.lineWidth=2;ctx.beginPath();
  for(let j=0;j<=13;j++){
    const xx=j===0?x:j===1?x+labelW:x+labelW+(j-1)*monthW;
    ctx.moveTo(xx,top);ctx.lineTo(xx,bottom);
  }
  for(let j=0;j<=8;j++){
    const yy=top+headH+j*rowH;
    ctx.moveTo(x,yy);ctx.lineTo(x+width,yy);
  }
  ctx.moveTo(x,top);ctx.lineTo(x+width,top);
  ctx.stroke();ctx.restore();
  return bottom;
}
function imageFromData(src){
  return new Promise((resolve,reject)=>{
    const img=new Image();
    img.onload=()=>resolve(img);
    img.onerror=()=>reject(Error('Não foi possível carregar a logo da Mundo Novo Trade.'));
    img.src=src;
  });
}
export async function exportMonthlyA4({payment,year,months:monthKeys,products}){
  if(!Number.isInteger(year)||year<2020||year>2100)throw Error('Ano de referência inválido.');
  if(!Array.isArray(monthKeys)||monthKeys.length!==12||!monthKeys.every(key=>typeof key==='string'&&/^\d{4}-(0[1-9]|1[0-2])$/.test(key)))throw Error('Período mensal inválido.');
  for(let i=1;i<monthKeys.length;i++){
    const [y,m]=monthKeys[i-1].split('-').map(Number),next=new Date(Date.UTC(y,m,1));
    if(monthKeys[i]!==next.getUTCFullYear()+'-'+String(next.getUTCMonth()+1).padStart(2,'0'))throw Error('Os meses precisam estar em ordem cronológica.');
  }
  if(!payment||!payment.trim())throw Error('Informe a condição de pagamento antes de exportar.');
  if(!Array.isArray(products)||products.length!==4||products.some(p=>p.sales?.length!==12||p.net?.length!==12))throw Error('Os quatro produtos devem conter 12 meses.');
  if(!products.some(p=>p.sales.some(moneyText)))throw Error('Calcule ao menos um preço comercial para exportar.');
  const canvas=document.createElement('canvas');
  canvas.width=W;canvas.height=H;
  const ctx=canvas.getContext('2d',{alpha:false});
  if(!ctx)throw Error('Seu navegador não suporta a exportação por Canvas.');
  fill(ctx,0,0,W,H,WHITE);
  const logo=await imageFromData(LOGO_SRC);
  const factor=Math.min(640/logo.naturalWidth,370/logo.naturalHeight);
  const lw=logo.naturalWidth*factor,lh=logo.naturalHeight*factor;
  ctx.drawImage(logo,(W-lw)/2,30,lw,lh);
  paintText(ctx,'PROPOSTA COMERCIAL',W/2,535,2300,64,{bold:true,color:WINE,align:'center'});
  paintText(ctx,'CONDIÇÕES DE PAGAMENTO — '+payment.trim().toUpperCase(),W/2,635,3050,49,{bold:true,color:INK,align:'center'});
  fill(ctx,100,720,W-200,6,WINE);
  const tableBottom=drawTable(ctx,products,monthKeys);
  const footerY=Math.max(tableBottom+90,2300);
  fill(ctx,100,footerY-45,W-200,3,SLATE);
  paintText(ctx,'COTAÇÃO EMITIDA EM '+brDate.format(new Date())+' (BRASÍLIA) · FOB PARANAGUÁ',W/2,footerY+20,W-240,31,{color:INK,align:'center'});
  const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
  if(!blob)throw Error('Não foi possível gerar o arquivo PNG.');
  const url=URL.createObjectURL(blob);
  const link=document.createElement('a');link.href=url;
  link.download='MundoNovo_PropostaComercial_A4_Paisagem_'+dateForFile.format(new Date())+'.png';
  document.body.append(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),30000);
  return {width:W,height:H,bytes:blob.size};
}
