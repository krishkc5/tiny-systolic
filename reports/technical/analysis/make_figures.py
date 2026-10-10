from pathlib import Path
import json, math, csv
from reportlab.graphics.shapes import Drawing,Rect,Line,String,Polygon
from reportlab.graphics import renderSVG
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.lib.colors import HexColor, Color, white
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'reports/technical/figures'
BLUE=HexColor('#22577A'); GREEN=HexColor('#277C71'); GRAY=HexColor('#64748B'); LIGHT=HexColor('#EAF1F5'); DARK=HexColor('#182D3A')
def label(d,x,y,s,size=11,color=DARK,anchor='middle'):
 d.add(String(x,y,s,fontName='Helvetica',fontSize=size,fillColor=color,textAnchor=anchor))
def box(d,x,y,w,h,title,sub='',color=LIGHT):
 d.add(Rect(x,y,w,h,rx=4,ry=4,fillColor=color,strokeColor=BLUE,strokeWidth=1))
 label(d,x+w/2,y+h/2+(5 if sub else -3),title,12)
 if sub:label(d,x+w/2,y+h/2-12,sub,9)
def arrow(d,x1,y1,x2,y2,color=GRAY):
 d.add(Line(x1,y1,x2,y2,strokeColor=color,strokeWidth=1.5))
 a=math.atan2(y2-y1,x2-x1);r=6
 pts=[x2,y2,x2-r*math.cos(a-.45),y2-r*math.sin(a-.45),x2-r*math.cos(a+.45),y2-r*math.sin(a+.45)]
 d.add(Polygon(pts,fillColor=color,strokeColor=color))
def save(d,name):renderSVG.drawToFile(d,str(OUT/(name+'.svg')))
# Architectural data movement. Conceptual netlist topology, not a physical floorplan.
d=Drawing(640,290)
box(d,10,120,122,62,'Host interface','8-bit input / output')
box(d,180,187,145,52,'Streaming controller','K counter / byte pairing')
box(d,180,60,145,52,'Input skew','A row 1 / B column 1')
arrow(d,132,156,180,213);arrow(d,250,187,250,112)
for x,y,t in [(390,178,'PE 00'),(535,178,'PE 01'),(390,65,'PE 10'),(535,65,'PE 11')]:box(d,x,y,90,52,t,'INT4 MAC / sum12')
arrow(d,325,86,390,91);arrow(d,350,203,390,203);arrow(d,480,204,535,204,GREEN);arrow(d,480,91,535,91,GREEN)
arrow(d,435,178,435,117,BLUE);arrow(d,580,178,580,117,BLUE)
label(d,505,245,'A moves right',10,GREEN);label(d,507,141,'B moves down',10,BLUE)
label(d,460,25,'Four 16-bit sign-extended results feed byte readback',10)
save(d,'architecture')
# State transitions.
d=Drawing(640,225)
for x,t,sub in [(10,'IDLE','waiting for START'),(175,'LOAD','2K input bytes'),(340,'DRAIN','two enabled edges'),(505,'DONE','eight result bytes')]:box(d,x,100,125,60,t,sub)
for x,s in [(135,'START'),(300,'last B'),(465,'2 edges')]:arrow(d,x,130,x+40,130);label(d,x+20,168,s,9)
d.add(Line(565,100,565,55,strokeColor=GRAY));d.add(Line(565,55,238,55,strokeColor=GRAY));arrow(d,238,55,238,100);label(d,400,35,'accepted START from DONE',10)
label(d,320,204,'RESET or enabled ABORT from any state returns to IDLE',11)
label(d,320,8,'ena = 0 freezes state and datapath; NOP still allows pipeline drain',10)
save(d,'state_machine')
# Ideal schedule K=4, products labelled by k at each PE; analytic, not waveform.
d=Drawing(640,210)
for i,name in enumerate(['PE 00','PE 01','PE 10','PE 11']):
 y=145-i*35;label(d,42,y+11,name,11)
 for t in range(6):
  k=t-[0,1,1,2][i];active=0<=k<4
  d.add(Rect(88+t*84,y,78,29,fillColor=LIGHT if active else white,strokeColor=HexColor('#CAD4DB')))
  label(d,127+t*84,y+10,'k = '+str(k) if active else '-',10)
for t in range(6):label(d,127+t*84,188,'Edge '+str(t+1),10)
label(d,320,9,'Full-rate core schedule: K + 2 enabled edges including first injection',11)
save(d,'schedule')
# Workflow.
d=Drawing(640,245)
for x,t,s in [(10,'RTL and model','Git source + fixtures'),(235,'Functional verification','MAC / core / chip / ML'),(460,'Physical build','synthesis / place / route')]:box(d,x,153,170, sixty:=60,t,s)
arrow(d,180,183,235,183);arrow(d,405,183,460,183)
for x,t,s in [(10,'Report and review','metrics + issues + provenance'),(235,'Netlist regression','same pin-level ML tests'),(460,'Physical checks','STA / DRC / LVS / precheck')]:box(d,x,38,170,60,t,s)
arrow(d,545,153,545,98);arrow(d,460,68,405,68);arrow(d,235,68,180,68)
label(d,320,8,'Passing workflow status and detailed electrical findings are reported separately',10)
save(d,'workflow')
# Charts using the reportlab chart library.
def bars(name,data,names,ymax,step,ytitle,values):
 d=Drawing(620,255);ch=VerticalBarChart();ch.x=65;ch.y=45;ch.width=490;ch.height=175;ch.data=[data];ch.categoryAxis.categoryNames=names
 ch.valueAxis.valueMin=0;ch.valueAxis.valueMax=ymax;ch.valueAxis.valueStep=step;ch.categoryAxis.labels.fontSize=11;ch.valueAxis.labels.fontSize=10
 ch.bars[0].fillColor=BLUE;ch.bars[0,1].fillColor=GREEN;ch.barWidth=65;ch.groupSpacing=80;ch.strokeColor=None
 d.add(ch);label(d,20,232,ytitle,10,anchor='start')
 for x,v,amount in zip([187,432],values,data):label(d,x,45+175*amount/ymax+8,v,12)
 save(d,name)
bars('area',[13309,11649.9],['Baseline 16-bit sums','Optimized 12-bit sums'],15000,3000,'Standard-cell area in square micrometers',['13,309.0','11,649.9'])
bars('accuracy',[95.5556,90.8333],['Float software','INT4 software and RTL'],100,20,'Held-out accuracy percent',['344 / 360','327 / 360'])
d=Drawing(620,260);lp=LinePlot();lp.x=60;lp.y=45;lp.width=500;lp.height=170;lp.data=[[(k,k+2)for k in range(1,17)],[(k,2*k+11)for k in range(1,17)]];lp.xValueAxis.valueMin=1;lp.xValueAxis.valueMax=16;lp.xValueAxis.valueSteps=[1,4,8,12,16];lp.yValueAxis.valueMin=0;lp.yValueAxis.valueMax=48;lp.yValueAxis.valueStep=8;lp.lines[0].strokeColor=GREEN;lp.lines[1].strokeColor=BLUE;lp.lines[0].strokeWidth=2;lp.lines[1].strokeWidth=2;d.add(lp);label(d,310,11,'Reduction length K',11);label(d,60,238,'Clock cycles',11,anchor='start');label(d,380,235,'Blue: full protocol   Green: ideal core',10);save(d,'latency')
# ML mapping.
d=Drawing(640,260)
for x,t,s in [(10,'Two images','2 x 64 INT4 inputs'),(235,'Hidden layer','2 x 16 neurons'),(460,'Digit scores','2 x 10 outputs')]:box(d,x,155,170,60,t,s)
arrow(d,180,185,235,185);arrow(d,405,185,460,185)
box(d,90,45,205, sixty,'Layer one on chip','32 tiles with K = 16');box(d,355,45,205,60,'Layer two on chip','5 tiles with K = 16');arrow(d,320,155,320,120)
label(d,320,127,'Host combines partial sums and applies scales / bias / ReLU',10)
label(d,320,14,'37 transactions per image pair; weights are streamed, not stored on chip',11)
save(d,'ml_mapping')
# Confusion matrix derived directly from preserved fixture predictions, also matched by RTL.
f=json.loads((ROOT/'ml/fixtures/digits_int4.json').read_text());cm=[[0]*10 for _ in range(10)]
for a,b in zip(f['labels'],f['reference_predictions']):cm[a][b]+=1
d=Drawing(490,410);mx=max(map(max,cm));cell=31;x0=105;y0=51
for r in range(10):
 label(d,90,y0+(9-r)*cell+11,str(r),10)
 for c in range(10):
  n=cm[r][c];q=n/mx;col=Color(1-.85*q,1-.63*q,1-.52*q)
  d.add(Rect(x0+c*cell,y0+(9-r)*cell,cell,cell,fillColor=col,strokeColor=white))
  label(d,x0+c*cell+cell/2,y0+(9-r)*cell+11,str(n),9,white if q>.6 else DARK)
for c in range(10):label(d,x0+c*cell+cell/2,35,str(c),10)
label(d,260,12,'Predicted class',11);label(d,20,225,'True',10,anchor='start');label(d,20,209,'class',10,anchor='start');label(d,260,385,'INT4 confusion matrix on 360 held-out examples',12);save(d,'confusion')
# Exact representative trace from Icarus output.
rows=list(csv.DictReader((ROOT/'reports/technical/evidence/k1-trace.csv').open()))
d=Drawing(640,195)
for i,r in enumerate(rows):
 x=80+i*39
 label(d,x+16,173,r['cycle'],9)
 for j,key in enumerate(['command','byte_before_edge','status_after_edge']):
  y=120-j*35;d.add(Rect(x,y,36,29,fillColor=LIGHT if r['command']=='3' else white,strokeColor=HexColor('#CBD5E1')))
  label(d,x+18,y+10,r[key],9)
for y,t in [(131,'Command'),(96,'Byte before'),(61,'Status after')]:label(d,73,y,t,9,anchor='end')
label(d,320,15,'K = 1 captured trace; hex bytes; READ samples before the rising edge',10);save(d,'trace')
(OUT/'confusion.json').write_text(json.dumps(cm,indent=2)+'\n')
print('Figures prepared')
