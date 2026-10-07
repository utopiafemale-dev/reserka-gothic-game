import { MAP_H, MAP_W, TILE, npcs, regions } from "./world";
import type { Phase, Player, RegionId } from "./types";
export const VIEW_W=MAP_W*TILE,VIEW_H=MAP_H*TILE;
const palette={village:["#526b48","#394d3e"],bamboo:["#304f3d","#1f3b34"],river:["#66806b","#465f57"],shrine:["#5b604e","#3d443e"],woods:["#243c34","#182b29"]} as const;
export function render(ctx:CanvasRenderingContext2D,region:RegionId,players:Player[],me:Player,phase:Phase,clock:string,t:number){
 const r=regions[region],pal=palette[region];ctx.imageSmoothingEnabled=false;ctx.fillStyle=pal[0];ctx.fillRect(0,0,VIEW_W,VIEW_H);
 for(let y=0;y<MAP_H;y++)for(let x=0;x<MAP_W;x++){const blocked=r.tiles[y][x];ctx.fillStyle=blocked?pal[1]:((x+y)%2?pal[0]:`${pal[0]}dd`);ctx.fillRect(x*TILE,y*TILE,TILE,TILE);if(blocked)plant(ctx,x*TILE,y*TILE,region,t);}
 landmark(ctx,region,phase,t);
 npcs.filter(n=>n.region===region&&(n.day?phase!=="NIGHT":phase==="NIGHT")).forEach(n=>person(ctx,n.x*TILE,n.y*TILE,"#d6bd77",n.name));
 players.filter(p=>p.region===region).forEach(p=>person(ctx,p.x*TILE,p.y*TILE,p.color,p.id===me.id?"YOU":p.name));
 if(phase!=="DAY"){ctx.fillStyle=phase==="NIGHT"?"rgba(5,8,27,.52)":"rgba(52,24,42,.25)";ctx.fillRect(0,0,VIEW_W,VIEW_H);const g=ctx.createRadialGradient(me.x*TILE+16,me.y*TILE+16,8,me.x*TILE+16,me.y*TILE+16,110);g.addColorStop(0,"rgba(255,206,112,.15)");g.addColorStop(1,"rgba(0,0,0,.35)");ctx.fillStyle=g;ctx.fillRect(0,0,VIEW_W,VIEW_H);}
 ctx.fillStyle="#f3e4bd";ctx.font="10px monospace";ctx.fillText(`${r.name.toUpperCase()}  ${phase} · ${clock}`,12,18);
}
function plant(c:CanvasRenderingContext2D,x:number,y:number,r:RegionId,t:number){c.fillStyle=r==="bamboo"||r==="woods"?"#172e29":"#273a32";c.fillRect(x+8,y+3,16,29);c.fillStyle="#60734c";c.fillRect(x+3,y+3,26,8);if(r==="bamboo"){c.fillStyle="#82905c";c.fillRect(x+14,y,4,32);c.fillRect(x+6,y+8,4,24);}}
function landmark(c:CanvasRenderingContext2D,r:RegionId,p:Phase,t:number){if(r==="village"){c.fillStyle="#8f542e";c.fillRect(330,248,24,14);c.fillStyle="#ffb447";c.fillRect(338,236+Math.sin(t/160)*2,9,15);}if(r==="river"){c.fillStyle="#527f8d";c.fillRect(0,352,VIEW_W,52);for(let x=0;x<VIEW_W;x+=38){c.fillStyle="#91b6ad";c.fillRect(x+(t/30)%38,366,17,2)}}if(r==="shrine"){c.fillStyle="#a94d42";c.fillRect(344,84,12,100);c.fillRect(416,84,12,100);c.fillRect(330,75,112,14);}}
function person(c:CanvasRenderingContext2D,x:number,y:number,color:string,label:string){c.fillStyle="#151b24";c.fillRect(x+9,y+19,14,11);c.fillStyle=color;c.fillRect(x+8,y+8,16,14);c.fillStyle="#f1d4b5";c.fillRect(x+11,y+3,10,8);c.fillStyle="rgba(5,8,12,.7)";c.fillRect(x-4,y-8,Math.max(32,label.length*6),9);c.fillStyle="#fff1c9";c.font="7px monospace";c.fillText(label,x,y-1);}
