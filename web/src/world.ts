import type { RegionId } from "./types";
export const TILE=32, MAP_W=24, MAP_H=15;
export interface Region { id:RegionId; name:string; subtitle:string; tiles:number[][]; spawn:[number,number]; exits:{x:number;y:number;to:RegionId;tx:number;ty:number}[] }
const bordered=(seed:number)=>Array.from({length:MAP_H},(_,y)=>Array.from({length:MAP_W},(_,x)=>x===0||y===0||x===MAP_W-1||y===MAP_H-1?1:((x*17+y*13+seed)%29===0?1:0)));
function region(id:RegionId,name:string,subtitle:string,seed:number,spawn:[number,number]):Region { return {id,name,subtitle,tiles:bordered(seed),spawn,exits:[]}; }
export const regions:Record<RegionId,Region>={
 village:region("village","Hollow Village","Where every greeting sounds rehearsed",2,[11,8]),
 bamboo:region("bamboo","Bamboo Path","The stalks lean closer when no one speaks",7,[2,7]),
 river:region("river","River Valley","The current carries voices uphill",11,[2,7]),
 shrine:region("shrine","Mountain Shrine","No caretaker has swept these steps",17,[2,7]),
 woods:region("woods","Forbidden Woods","Paths remember different travelers",23,[2,7])
};
regions.village.exits=[{x:23,y:7,to:"bamboo",tx:1,ty:7}]; regions.bamboo.exits=[{x:0,y:7,to:"village",tx:22,ty:7},{x:23,y:7,to:"river",tx:1,ty:7}];
regions.river.exits=[{x:0,y:7,to:"bamboo",tx:22,ty:7},{x:23,y:7,to:"shrine",tx:1,ty:7}]; regions.shrine.exits=[{x:0,y:7,to:"river",tx:22,ty:7},{x:23,y:7,to:"woods",tx:1,ty:7}]; regions.woods.exits=[{x:0,y:7,to:"shrine",tx:22,ty:7}];
// Keep region gates open and add authored landmarks/collision silhouettes.
Object.values(regions).forEach(r=>r.exits.forEach(e=>r.tiles[e.y][e.x]=0));
export const npcs=[
 {id:"elder",region:"village",x:8,y:6,name:"Elder Nao",day:true,text:"You came back with the bell. But I have never seen your face."},
 {id:"merchant",region:"village",x:15,y:9,name:"Ichi",day:true,text:"At dusk, do not count the houses. There will be one too many."},
 {id:"child",region:"village",x:5,y:10,name:"Mina",day:true,text:"Your shadow arrived yesterday. It was waiting by the fire."},
 {id:"monk",region:"shrine",x:12,y:6,name:"Silent Monk",day:false,text:"The shrine is empty. Then who rang the bell?"}
] as const;
export function isBlocked(region:RegionId,x:number,y:number){return x<0||y<0||x>=MAP_W||y>=MAP_H||regions[region].tiles[y][x]===1||npcs.some(n=>n.region===region&&n.x===x&&n.y===y);}
export function phaseAt(worldMinutes:number){ const p=((worldMinutes%20)+20)%20; return p<8?"DAY":p<11?"DUSK":p<17?"NIGHT":"DAWN"; }
